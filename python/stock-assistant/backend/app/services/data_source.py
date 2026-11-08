"""行情数据采集层：统一封装腾讯财经 / 东方财富公开接口与 AkShare，向上提供
实时行情、大盘指数、股票搜索、日 K 线、当日分时、个股 / 板块资金流向。

数据源策略（主 → 备，失败自动降级，具体映射见 README「数据源说明」）：
- 实时行情 / 指数 / 搜索 / 日 K：腾讯公开行情接口为主，AkShare 兜底
- 当日分时：东方财富 trends2 为主，腾讯分时接口兜底
- 板块资金流：东方财富 push2；个股资金流：AkShare（底层为东财）

单位口径：实时行情 Quote 成交量换算为「股」、成交额换算为「元」
（腾讯原始字段为手 / 万元）；日 K 与分时序列的成交量保留源口径「手」。

并发模型：第三方接口与 AkShare 均为同步调用，通过 asyncio.to_thread 放到线程池，
避免阻塞 FastAPI 事件循环。

网络说明：macOS 系统代理（Clash 等）会导致 Python requests 出现 ProxyError，
通过 monkeypatch requests.Session.request 在原生请求失败后回退到 curl 子进程，
绕过 Python 层代理/TLS 问题（curl 直连或走系统代理均正常）。
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

import akshare as ak
import requests as _requests

from app.schemas.quote import IndexQuote, Quote
from app.services.seed import INDEX_DEFS

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════
#  curl 传输回退：requests 原生请求失败时用 curl 子进程兜底
# ════════════════════════════════════════════════════════════════════


class _CurlResponse:
    """模拟 requests.Response，用 curl 输出构造。"""

    def __init__(self, status_code: int, body: bytes, url: str) -> None:
        self.status_code = status_code
        self._content = body
        self.url = url
        self.text = body.decode("utf-8", errors="replace")
        self.encoding = "utf-8"
        self.reason = ""
        self.headers: dict[str, str] = {}

    @property
    def content(self) -> bytes:
        return self._content

    def json(self) -> Any:
        return json.loads(self._content)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise _requests.HTTPError(
                f"HTTP {self.status_code}", response=self  # type: ignore[arg-type]
            )

    def close(self) -> None:
        pass


def _curl_get(
    url: str,
    params: dict | None = None,
    timeout: float | tuple | None = 15,
    headers: dict | None = None,
) -> _CurlResponse:
    """用 curl 子进程发起 GET 请求并返回模拟 Response。"""
    full_url = url
    if params:
        full_url = f"{url}?{urlencode(params)}"

    t = 15
    if isinstance(timeout, (int, float)):
        t = int(timeout)
    elif isinstance(timeout, tuple) and timeout:
        t = int(timeout[0])

    cmd: list[str] = [
        "curl",
        "-sS",
        "--connect-timeout",
        str(t),
        "-m",
        str(t + 5),
        "-w",
        "\n%{http_code}",
    ]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    cmd.append(full_url)

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=t + 10)
    except subprocess.TimeoutExpired as e:
        raise _requests.ConnectionError(f"curl timeout: {e}") from e

    output = result.stdout
    parts = output.rsplit(b"\n", 1)
    if len(parts) == 2 and parts[1].strip().isdigit():
        body, code_bytes = parts
        status_code = int(code_bytes.strip())
    else:
        body = output
        status_code = 200 if output else 0

    if result.returncode != 0 and not body:
        raise _requests.ConnectionError(
            f"curl exit {result.returncode}: {result.stderr.decode(errors='replace')}"
        )

    return _CurlResponse(status_code, body, full_url)


def _curl_post(
    url: str,
    data: dict | str | None = None,
    timeout: float = 15,
    headers: dict | None = None,
) -> _CurlResponse:
    """用 curl 子进程发起 POST 请求并返回模拟 Response。"""
    t = int(timeout)
    cmd: list[str] = [
        "curl",
        "-sS",
        "-X", "POST",
        "--connect-timeout", str(t),
        "-m", str(t + 5),
        "-w", "\n%{http_code}",
    ]
    final_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if headers:
        final_headers.update(headers)

    if isinstance(data, dict):
        body_str = urlencode(data)
    elif isinstance(data, str):
        body_str = data
    else:
        body_str = ""

    for k, v in final_headers.items():
        cmd.extend(["-H", f"{k}: {v}"])
    if body_str:
        cmd.extend(["-d", body_str])
    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=t + 10)
    except subprocess.TimeoutExpired as e:
        raise _requests.ConnectionError(f"curl timeout: {e}") from e

    output = result.stdout
    parts = output.rsplit(b"\n", 1)
    if len(parts) == 2 and parts[1].strip().isdigit():
        body, code_bytes = parts
        status_code = int(code_bytes.strip())
    else:
        body = output
        status_code = 200 if output else 0

    if result.returncode != 0 and not body:
        raise _requests.ConnectionError(
            f"curl exit {result.returncode}: {result.stderr.decode(errors='replace')}"
        )

    return _CurlResponse(status_code, body, url)


async def _curl_post_async(
    url: str,
    data: dict | str | None = None,
    timeout: float = 15,
    headers: dict | None = None,
) -> _CurlResponse:
    """异步包装 _curl_post。"""
    return await asyncio.to_thread(
        _curl_post, url, data, timeout, headers
    )


# 保存原生 request 方法，patch Session.request 加入 curl 回退
_original_request = _requests.Session.request


def _request_with_curl_fallback(self: Any, method: str, url: str, **kwargs: Any) -> Any:
    """先走原生 requests，ProxyError / ConnectionError 时回退 curl（仅 GET）。"""
    try:
        return _original_request(self, method, url, **kwargs)
    except (
        _requests.exceptions.ProxyError,
        _requests.exceptions.ConnectionError,
    ) as e:
        if method.upper() != "GET":
            raise
        logger.debug(
            "requests.%s 失败 (%s)，回退 curl: %s",
            method,
            type(e).__name__,
            url,
        )
        params = kwargs.get("params")
        timeout = kwargs.get("timeout") or 15
        headers = kwargs.get("headers")
        return _curl_get(url, params=params, timeout=timeout, headers=headers)


_requests.Session.request = _request_with_curl_fallback  # type: ignore[method-assign]
logger.info("已 patch requests.Session.request → curl 回退")


# ════════════════════════════════════════════════════════════════════
#  通用工具
# ════════════════════════════════════════════════════════════════════


def _safe_float(val: Any) -> float:
    """安全转 float，处理空值/字符串。"""
    if val is None or val == "":
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _infer_market(code: str) -> str:
    """根据代码前缀推断市场：688/60 开头 SH，其余 SZ。"""
    if code.startswith(("688", "60")):
        return "SH"
    return "SZ"


def _tencent_code(code: str) -> str:
    """股票代码 → 腾讯格式（600519 → sh600519, 000858 → sz000858）。"""
    # 6xx/9xx 开头 → 上交所；0xx/2xx/3xx → 深交所；8xx/4xx → 北交所
    if code.startswith(("6", "9")):
        return f"sh{code}"
    if code.startswith(("8", "4")):
        return f"bj{code}"
    return f"sz{code}"


def _parse_tencent_timestamp(ts: str) -> int:
    """解析腾讯时间戳（20260908161435）→ 毫秒。"""
    try:
        dt = datetime.strptime(ts, "%Y%m%d%H%M%S")
        return int(dt.timestamp() * 1000)
    except (ValueError, TypeError):
        return int(datetime.now().timestamp() * 1000)


def _parse_tencent_response(text: str) -> dict[str, list[str]]:
    """解析腾讯行情文本 → dict[code, fields]。

    输入格式：v_sh600519="1~贵州茅台~600519~1309.30~..."
    """
    result: dict[str, list[str]] = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or not line.startswith("v_"):
            continue
        eq_pos = line.find("=")
        if eq_pos < 0:
            continue
        raw = line[eq_pos + 1:].strip()
        # 去掉引号和分号
        raw = raw.strip('"').strip(";").strip('"')
        if not raw:
            continue
        fields = raw.split("~")
        if len(fields) > 5:
            code = fields[2] if len(fields) > 2 else ""
            if code:
                result[code] = fields
    return result


# ════════════════════════════════════════════════════════════════════
#  实时行情（腾讯行情为主，AkShare 为备）
# ════════════════════════════════════════════════════════════════════


def _fetch_tencent_quotes_sync(codes: list[str]) -> dict[str, Quote]:
    """同步：用 curl 调腾讯行情接口，一次取多只。"""
    if not codes:
        return {}
    tencent_codes = ",".join(_tencent_code(c) for c in codes)
    url = f"https://qt.gtimg.cn/q={tencent_codes}"
    try:
        resp = _curl_get(url, timeout=8)
    except Exception as e:  # noqa: BLE001
        logger.error("腾讯行情请求失败: %s", e)
        return {}
    if resp.status_code != 200:
        logger.warning("腾讯行情 HTTP %d", resp.status_code)
        return {}

    # 腾讯返回 GBK 编码
    text = resp.content.decode("gbk", errors="replace")
    parsed = _parse_tencent_response(text)

    result: dict[str, Quote] = {}
    for code in codes:
        fields = parsed.get(code)
        if not fields or len(fields) < 35:
            continue
        try:
            result[code] = Quote(
                code=code,
                name=fields[1].replace(" ", ""),
                price=_safe_float(fields[3]),
                changePct=_safe_float(fields[32]),
                changeAmt=_safe_float(fields[31]),
                volume=_safe_float(fields[36]) * 100,  # 手 → 股
                amount=_safe_float(fields[37]) * 10000,  # 万元 → 元
                high=_safe_float(fields[33]),
                low=_safe_float(fields[34]),
                open=_safe_float(fields[5]),
                preClose=_safe_float(fields[4]),
                timestamp=_parse_tencent_timestamp(fields[30]) if len(fields) > 30 else 0,
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("解析腾讯行情失败 code=%s: %s", code, e)
    return result


def _fetch_akshare_spot_df() -> Any:
    """同步调用 AkShare 获取全量 A 股实时行情 DataFrame（备选）。"""
    return ak.stock_zh_a_spot_em()


def _fetch_akshare_quotes_sync(codes: list[str]) -> dict[str, Quote]:
    """同步：AkShare 备选行情（全市场拉取后过滤）。"""
    try:
        df = _fetch_akshare_spot_df()
    except Exception as e:  # noqa: BLE001
        logger.error("AkShare stock_zh_a_spot_em 调用失败: %s", e)
        return {}
    if df is None or df.empty:
        return {}

    code_set = set(codes)
    now_ms = int(datetime.now().timestamp() * 1000)
    result: dict[str, Quote] = {}
    for _, row in df.iterrows():
        code = str(row.get("代码", "")).strip()
        if code not in code_set:
            continue
        try:
            result[code] = Quote(
                code=code,
                name=str(row.get("名称", "")),
                price=_safe_float(row.get("最新价")),
                changePct=_safe_float(row.get("涨跌幅")),
                changeAmt=_safe_float(row.get("涨跌额")),
                volume=_safe_float(row.get("成交量")),
                amount=_safe_float(row.get("成交额")),
                high=_safe_float(row.get("最高")),
                low=_safe_float(row.get("最低")),
                open=_safe_float(row.get("今开")),
                preClose=_safe_float(row.get("昨收")),
                timestamp=now_ms,
                speed5m=_safe_float(row.get("涨速")) if "涨速" in df.columns else None,
                volRatio=_safe_float(row.get("量比")) if "量比" in df.columns else None,
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("解析 AkShare 行情失败 code=%s: %s", code, e)
    return result


async def fetch_realtime_quotes(codes: list[str]) -> dict[str, Quote]:
    """批量获取实时行情：优先腾讯接口，失败回退 AkShare。

    Args:
        codes: 需要行情的证券代码列表

    Returns:
        dict[code, Quote]；未获取到的 code 不包含在内
    """
    if not codes:
        return {}

    # 1. 腾讯行情（轻量、按需取数）
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_fetch_tencent_quotes_sync, codes), timeout=15
        )
        if result:
            return result
        logger.warning("腾讯行情返回空，尝试 AkShare 备选")
    except asyncio.TimeoutError:
        logger.warning("腾讯行情超时，尝试 AkShare 备选")
    except Exception as e:  # noqa: BLE001
        logger.warning("腾讯行情失败 (%s)，尝试 AkShare 备选", e)

    # 2. AkShare 备选
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_fetch_akshare_quotes_sync, codes), timeout=60
        )
    except asyncio.TimeoutError:
        logger.error("AkShare 行情超时")
        return {}
    except Exception as e:  # noqa: BLE001
        logger.error("AkShare 行情失败: %s", e)
        return {}


# ════════════════════════════════════════════════════════════════════
#  大盘指数
# ════════════════════════════════════════════════════════════════════


def _fetch_tencent_indexes_sync() -> list[IndexQuote]:
    """同步：用 curl 调腾讯指数接口。"""
    symbols = [d["symbol"] for d in INDEX_DEFS]  # e.g. sh000001
    url = f"https://qt.gtimg.cn/q={','.join(symbols)}"
    try:
        resp = _curl_get(url, timeout=8)
    except Exception as e:  # noqa: BLE001
        logger.error("腾讯指数请求失败: %s", e)
        return []
    if resp.status_code != 200:
        return []

    text = resp.content.decode("gbk", errors="replace")
    parsed = _parse_tencent_response(text)

    name_map = {d["code"]: d["name"] for d in INDEX_DEFS}
    order = {d["code"]: i for i, d in enumerate(INDEX_DEFS)}
    result: list[IndexQuote] = []
    for d in INDEX_DEFS:
        fields = parsed.get(d["code"])
        if not fields or len(fields) < 35:
            continue
        try:
            result.append(
                IndexQuote(
                    code=d["code"],
                    name=name_map.get(d["code"], fields[1]),
                    price=_safe_float(fields[3]),
                    changePct=_safe_float(fields[32]),
                    changeAmt=_safe_float(fields[31]),
                    timestamp=_parse_tencent_timestamp(fields[30]) if len(fields) > 30 else 0,
                )
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("解析腾讯指数失败 code=%s: %s", d["code"], e)

    result.sort(key=lambda x: order.get(x.code, 999))
    return result


async def fetch_realtime_indexes() -> list[IndexQuote]:
    """获取预置大盘指数实时行情（腾讯接口）。"""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_fetch_tencent_indexes_sync), timeout=15
        )
    except asyncio.TimeoutError:
        logger.error("腾讯指数超时")
        return []
    except Exception as e:  # noqa: BLE001
        logger.error("腾讯指数失败: %s", e)
        return []


# ════════════════════════════════════════════════════════════════════
#  股票搜索
# ════════════════════════════════════════════════════════════════════


def _tencent_search_sync(keyword: str, limit: int = 20) -> list[dict[str, str]]:
    """同步：腾讯智能选股接口。"""
    if not keyword:
        return []
    url = f"https://smartbox.gtimg.cn/s3/?q={keyword}&t=all"
    try:
        resp = _curl_get(url, timeout=8)
    except Exception as e:  # noqa: BLE001
        logger.error("腾讯搜索请求失败: %s", e)
        return []
    if resp.status_code != 200:
        return []

    text = resp.content.decode("gbk", errors="replace")
    # v_hint="sh~600519~\u8d35\u5dde\u8305\u53f0~gzmt~GP-A";
    results: list[dict[str, str]] = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line.startswith("v_hint"):
            continue
        eq_pos = line.find("=")
        if eq_pos < 0:
            continue
        raw = line[eq_pos + 1:].strip().strip('"').strip(";").strip('"')
        if not raw:
            continue
        # 腾讯搜索返回可能含 \uXXXX 转义，解码为中文
        try:
            raw = raw.encode("utf-8").decode("unicode_escape")
        except (UnicodeDecodeError, ValueError):
            pass
        parts = raw.split("~")
        if len(parts) < 3:
            continue
        market_code, code, name = parts[0], parts[1], parts[2]
        if not code:
            continue
        market = "SH" if market_code.startswith("sh") else "SZ"
        results.append({"code": code, "name": name, "market": market, "industry": ""})
        if len(results) >= limit:
            break
    return results


def _akshare_search_sync(keyword: str, limit: int = 20) -> list[dict[str, str]]:
    """同步：AkShare 股票搜索（备选）。"""
    try:
        df = ak.stock_info_a_code_name()
    except Exception as e:  # noqa: BLE001
        logger.error("AkShare stock_info_a_code_name 调用失败: %s", e)
        return []
    if df is None or df.empty:
        return []

    results: list[dict[str, str]] = []
    for _, row in df.iterrows():
        code = str(row.get("code", "")).strip()
        name = str(row.get("name", "")).strip()
        if keyword in code or keyword in name:
            results.append({
                "code": code,
                "name": name,
                "market": _infer_market(code),
                "industry": "",
            })
            if len(results) >= limit:
                break
    return results


async def search_stocks(keyword: str, limit: int = 20) -> list[dict[str, str]]:
    """股票模糊搜索：优先腾讯接口，失败回退 AkShare。

    返回 list of {code, name, market, industry}。
    """
    keyword = keyword.strip()
    if not keyword:
        return []

    # 1. 腾讯搜索
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_tencent_search_sync, keyword, limit), timeout=10
        )
        if result:
            return result
    except asyncio.TimeoutError:
        logger.warning("腾讯搜索超时")
    except Exception as e:  # noqa: BLE001
        logger.warning("腾讯搜索失败: %s", e)

    # 2. AkShare 备选
    try:
        return await asyncio.to_thread(_akshare_search_sync, keyword, limit)
    except Exception as e:  # noqa: BLE001
        logger.error("AkShare 搜索失败: %s", e)
        return []


# ════════════════════════════════════════════════════════════════════
#  连通性检查
# ════════════════════════════════════════════════════════════════════


async def check_connectivity() -> bool:
    """检查数据源连通性（用 curl 直连腾讯行情接口）。"""
    try:
        resp = await asyncio.to_thread(
            _curl_get,
            "https://qt.gtimg.cn/q=sh000001",
            None,
            8,
        )
        return resp.status_code == 200
    except Exception as e:  # noqa: BLE001
        logger.warning("连通性检查失败: %s", e)
        return False


# ══════════════════════════════════════════════════════════════════════
#  日 K 线历史（腾讯 fqkline 前复权为主，AkShare 为备；长历史分段翻页）
# ══════════════════════════════════════════════════════════════════════


def _parse_tencent_kline_rows(
    data: dict[str, Any], tencent_code: str
) -> list[dict[str, Any]]:
    """解析腾讯 fqkline 响应为 K 线 dict 列表（按日期升序）。"""
    stock_data = data.get("data", {}).get(tencent_code, {})
    kline_list = stock_data.get("qfqday") or stock_data.get("day") or []

    result: list[dict[str, Any]] = []
    for item in kline_list:
        if not item or len(item) < 6:
            continue
        date_str = str(item[0]).strip()
        if not date_str:
            continue
        try:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            ts = int(dt.timestamp())
        except ValueError:
            continue
        result.append(
            {
                "time": ts,
                "date": date_str[:10],
                "open": _safe_float(item[1]),
                "close": _safe_float(item[2]),
                "high": _safe_float(item[3]),
                "low": _safe_float(item[4]),
                "volume": _safe_float(item[5]) if len(item) > 5 else 0.0,
            }
        )
    result.sort(key=lambda x: x["time"])
    return result


# 腾讯 fqkline 单段实际可取上限约 800 根
_TENCENT_KLINE_PAGE = 800
# 分段翻页安全上限（800 × 12 ≈ 38 年交易日，覆盖 A 股全部历史）
_TENCENT_KLINE_MAX_PAGES = 12


def _fetch_tencent_kline_sync(code: str, days: int = 250) -> list[dict[str, Any]]:
    """同步：腾讯日 K 线接口（主数据源，稳定可靠）。

    接口：https://web.ifzq.gtimg.cn/appstock/app/fqkline/get
    返回 list of {time, date, open, close, high, low, volume}，按日期升序。

    单段最多约 800 根；days 超过 800 时以段内最早日期为 end 向前翻页，
    按日期去重拼接（各段前复权基准一致，重叠日价格相同）。
    """
    tencent_code = _tencent_code(code)

    def _one_page(end_date: str) -> list[dict[str, Any]]:
        url = (
            "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
            f"?param={tencent_code},day,,{end_date},{_TENCENT_KLINE_PAGE},qfq"
        )
        try:
            resp = _curl_get(url, timeout=12)
        except Exception as e:  # noqa: BLE001
            logger.error("腾讯K线请求失败 code=%s end=%s: %s", code, end_date or "latest", e)
            return []
        if resp.status_code != 200:
            logger.warning(
                "腾讯K线 HTTP %d code=%s end=%s",
                resp.status_code, code, end_date or "latest",
            )
            return []
        try:
            data = resp.json()
        except Exception as e:  # noqa: BLE001
            logger.error("腾讯K线JSON解析失败 code=%s: %s", code, e)
            return []
        if not isinstance(data, dict):
            return []
        return _parse_tencent_kline_rows(data, tencent_code)

    # days <= 单段上限：一次请求即可
    if days <= _TENCENT_KLINE_PAGE:
        url = (
            "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
            f"?param={tencent_code},day,,,{days},qfq"
        )
        try:
            resp = _curl_get(url, timeout=10)
        except Exception as e:  # noqa: BLE001
            logger.error("腾讯K线请求失败 code=%s: %s", code, e)
            return []
        if resp.status_code != 200:
            logger.warning("腾讯K线 HTTP %d code=%s", resp.status_code, code)
            return []
        try:
            data = resp.json()
        except Exception as e:  # noqa: BLE001
            logger.error("腾讯K线JSON解析失败 code=%s: %s", code, e)
            return []
        if not isinstance(data, dict):
            return []
        return _parse_tencent_kline_rows(data, tencent_code)

    # 长历史：分段向前翻页，按日期去重
    by_date: dict[str, dict[str, Any]] = {}
    end_date = ""
    for _ in range(_TENCENT_KLINE_MAX_PAGES):
        page = _one_page(end_date)
        if not page:
            break
        added = 0
        for row in page:
            if row["date"] not in by_date:
                by_date[row["date"]] = row
                added += 1
        earliest = page[0]["date"]
        # 无新增日期 = 已到上市首日；拿够数量即停
        if added == 0 or len(by_date) >= days:
            break
        # 下一段以本段最早日期为结束日（含当天，衔接去重）
        if earliest == end_date:
            break
        end_date = earliest

    result = sorted(by_date.values(), key=lambda x: x["time"])
    return result[-days:] if days > 0 else result


def _fetch_akshare_kline_sync(
    code: str, days: int = 250
) -> list[dict[str, Any]]:
    """同步：AkShare 获取日 K 线数据。

    返回 list of {date, open, close, high, low, volume}，按日期升序。
    """
    from datetime import timedelta

    end = datetime.now()
    start = end - timedelta(days=days)
    try:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start.strftime("%Y%m%d"),
            end_date=end.strftime("%Y%m%d"),
            adjust="qfq",
        )
    except Exception as e:  # noqa: BLE001
        logger.error("AkShare K线获取失败 code=%s: %s", code, e)
        return []

    if df is None or df.empty:
        return []

    result: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        date_val = str(row.get("日期", "")).strip()
        if not date_val:
            continue
        # 日期格式 YYYY-MM-DD → 时间戳（秒）
        try:
            dt = datetime.strptime(date_val[:10], "%Y-%m-%d")
            ts = int(dt.timestamp())
        except ValueError:
            continue
        result.append(
            {
                "time": ts,
                "date": date_val[:10],
                "open": _safe_float(row.get("开盘")),
                "close": _safe_float(row.get("收盘")),
                "high": _safe_float(row.get("最高")),
                "low": _safe_float(row.get("最低")),
                "volume": _safe_float(row.get("成交量")),
            }
        )
    # 按时间升序
    result.sort(key=lambda x: x["time"])
    return result


async def fetch_daily_kline(code: str, days: int = 250) -> list[dict[str, Any]]:
    """异步获取日 K 线数据：优先腾讯接口，失败回退 AkShare。

    两个数据源均带重试逻辑，AkShare 偶发返回空数据时自动重试。
    """
    # 1. 腾讯接口（主）
    for attempt in range(2):
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(_fetch_tencent_kline_sync, code, days), timeout=15
            )
            if result:
                return result
            logger.warning("腾讯K线返回空 code=%s (尝试 %d/2)", code, attempt + 1)
            if attempt < 1:
                await asyncio.sleep(0.5)
        except asyncio.TimeoutError:
            logger.warning("腾讯K线超时 code=%s (尝试 %d/2)", code, attempt + 1)
            if attempt < 1:
                await asyncio.sleep(0.5)
        except Exception as e:  # noqa: BLE001
            logger.warning("腾讯K线失败 code=%s: %s (尝试 %d/2)", code, e, attempt + 1)
            if attempt < 1:
                await asyncio.sleep(0.5)

    # 2. AkShare 备选
    for attempt in range(3):
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(_fetch_akshare_kline_sync, code, days), timeout=30
            )
            if result:
                return result
            logger.warning("AkShare K线返回空 code=%s (尝试 %d/3)", code, attempt + 1)
            if attempt < 2:
                await asyncio.sleep(1)
        except asyncio.TimeoutError:
            logger.error("AkShare K线超时 code=%s (尝试 %d/3)", code, attempt + 1)
            if attempt < 2:
                await asyncio.sleep(1)
        except Exception as e:  # noqa: BLE001
            logger.error("AkShare K线失败 code=%s: %s (尝试 %d/3)", code, e, attempt + 1)
            if attempt < 2:
                await asyncio.sleep(1)
    return []


# ════════════════════════════════════════════════════════════════════
#  分时行情（当日 1 分钟）
# ════════════════════════════════════════════════════════════════════


def _eastmoney_secid(code: str) -> str:
    """股票代码 → 东方财富 secid：6/9 开头沪市 1.，其余（深市/北交所）0.。"""
    if code.startswith(("6", "9")):
        return f"1.{code}"
    return f"0.{code}"


def _fetch_eastmoney_intraday_sync(code: str) -> dict[str, Any]:
    """同步：东财 trends2 当日分时（1 分钟），含分钟均价。

    返回 {"preClose": float, "data": [{datetime,time,timestamp,price,avg,volume,amount}]}，
    volume 为当分钟成交量（手）。
    """
    params = urlencode(
        {
            "secid": _eastmoney_secid(code),
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
            "iscr": "0",
            "ndays": "1",
        }
    )
    url = f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?{params}"
    try:
        resp = _curl_get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:  # noqa: BLE001
        logger.warning("东财分时请求失败 code=%s: %s", code, e)
        return {"preClose": 0.0, "data": []}
    if resp.status_code != 200:
        logger.warning("东财分时 HTTP %d code=%s", resp.status_code, code)
        return {"preClose": 0.0, "data": []}
    try:
        payload = resp.json().get("data") or {}
    except Exception as e:  # noqa: BLE001
        logger.warning("东财分时 JSON 解析失败 code=%s: %s", code, e)
        return {"preClose": 0.0, "data": []}

    pre_close = _safe_float(payload.get("preClose"))
    points: list[dict[str, Any]] = []
    for line in payload.get("trends") or []:
        parts = line.split(",")
        if len(parts) < 8:
            continue
        # 格式：2026-10-09 09:31, 开, 收, 高, 低, 成交量(手), 成交额(元), 均价
        dt_str = parts[0]
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        points.append(
            {
                "datetime": dt_str,
                "time": dt_str[11:16],
                "timestamp": int(dt.timestamp()),
                "price": _safe_float(parts[2]),
                "avg": _safe_float(parts[7]),
                "volume": _safe_float(parts[5]),
                "amount": _safe_float(parts[6]),
            }
        )
    return {"preClose": pre_close, "data": points}


def _fetch_tencent_intraday_sync(code: str) -> dict[str, Any]:
    """同步：腾讯当日分时（兜底）。

    原始行为 "HHMM 价格 累计成交量(手) 累计成交额(元)"，
    分钟量/分钟额由累计值差分，均价 = 累计成交额 / (累计成交量 × 100)。
    """
    tc = _tencent_code(code)
    url = f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={tc}"
    try:
        resp = _curl_get(url, timeout=10)
    except Exception as e:  # noqa: BLE001
        logger.warning("腾讯分时请求失败 code=%s: %s", code, e)
        return {"preClose": 0.0, "data": []}
    if resp.status_code != 200:
        return {"preClose": 0.0, "data": []}
    try:
        payload = resp.json()
        node = (payload.get("data") or {}).get(tc) or {}
    except Exception as e:  # noqa: BLE001
        logger.warning("腾讯分时 JSON 解析失败 code=%s: %s", code, e)
        return {"preClose": 0.0, "data": []}

    qt = (node.get("qt") or {}).get(tc) or []
    # qt 数组第 5 项（index 4）为昨收价
    pre_close = _safe_float(qt[4]) if len(qt) > 4 else 0.0

    minute_node = node.get("data") or {}
    raw_lines = minute_node.get("data") or []
    date_str = str(minute_node.get("date", ""))  # YYYYMMDD
    points: list[dict[str, Any]] = []
    prev_vol = 0.0
    prev_amt = 0.0
    for line in raw_lines:
        parts = str(line).split()
        if len(parts) < 4 or len(date_str) != 8:
            continue
        hm, price_s, cum_vol_s, cum_amt_s = parts[0], parts[1], parts[2], parts[3]
        # 仅保留连续竞价时段（含收盘集合竞价 15:00），丢弃盘后零量补点
        if not ("0930" <= hm <= "1130" or "1300" <= hm <= "1500"):
            continue
        try:
            dt = datetime.strptime(date_str + hm, "%Y%m%d%H%M")
        except ValueError:
            continue
        cum_vol = _safe_float(cum_vol_s)
        cum_amt = _safe_float(cum_amt_s)
        price = _safe_float(price_s)
        minute_vol = max(cum_vol - prev_vol, 0.0)
        minute_amt = max(cum_amt - prev_amt, 0.0)
        avg = cum_amt / (cum_vol * 100) if cum_vol > 0 else price
        dt_str = dt.strftime("%Y-%m-%d %H:%M")
        points.append(
            {
                "datetime": dt_str,
                "time": dt_str[11:16],
                "timestamp": int(dt.timestamp()),
                "price": price,
                "avg": round(avg, 3),
                "volume": minute_vol,
                "amount": minute_amt,
            }
        )
        prev_vol, prev_amt = cum_vol, cum_amt
    return {"preClose": pre_close, "data": points}


async def fetch_intraday(code: str) -> dict[str, Any]:
    """异步获取当日分时：优先东财 trends2，失败回退腾讯。

    返回 {"preClose": float, "data": [...]}；两者均失败时 data 为空。
    """
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_fetch_eastmoney_intraday_sync, code), timeout=12
        )
        if result.get("data"):
            return result
    except asyncio.TimeoutError:
        logger.warning("东财分时超时 code=%s", code)
    except Exception as e:  # noqa: BLE001
        logger.warning("东财分时失败 code=%s: %s", code, e)

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_fetch_tencent_intraday_sync, code), timeout=12
        )
        if result.get("data"):
            return result
    except asyncio.TimeoutError:
        logger.warning("腾讯分时超时 code=%s", code)
    except Exception as e:  # noqa: BLE001
        logger.warning("腾讯分时失败 code=%s: %s", code, e)
    return {"preClose": 0.0, "data": []}


# ════════════════════════════════════════════════════════════════════
#  个股资金流向（AkShare - 东方财富）
# ════════════════════════════════════════════════════════════════════


def _fetch_fund_flow_sync(code: str, days: int = 30) -> list[dict[str, Any]]:
    """同步：获取个股资金流向历史数据（东方财富）。

    返回最近 days 天的数据，包含主力/超大单/大单/中单/小单净流入。
    """
    market = "sh" if code.startswith(("6", "9")) else "sz"
    try:
        df = ak.stock_individual_fund_flow(stock=code, market=market)
    except Exception as e:  # noqa: BLE001
        logger.error("资金流向获取失败 code=%s: %s", code, e)
        return []

    if df is None or df.empty:
        return []

    # 取最近 days 条
    df = df.tail(days)

    result: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        result.append(
            {
                "date": str(row.get("日期", ""))[:10],
                "close": _safe_float(row.get("收盘价")),
                "changePct": _safe_float(row.get("涨跌幅")),
                "mainNetInflow": _safe_float(row.get("主力净流入-净额")),
                "mainNetInflowRatio": _safe_float(row.get("主力净流入-净占比")),
                "superLargeNetInflow": _safe_float(row.get("超大单净流入-净额")),
                "superLargeNetInflowRatio": _safe_float(row.get("超大单净流入-净占比")),
                "largeNetInflow": _safe_float(row.get("大单净流入-净额")),
                "largeNetInflowRatio": _safe_float(row.get("大单净流入-净占比")),
                "mediumNetInflow": _safe_float(row.get("中单净流入-净额")),
                "mediumNetInflowRatio": _safe_float(row.get("中单净流入-净占比")),
                "smallNetInflow": _safe_float(row.get("小单净流入-净额")),
                "smallNetInflowRatio": _safe_float(row.get("小单净流入-净占比")),
            }
        )
    return result


async def fetch_fund_flow(code: str, days: int = 30) -> list[dict[str, Any]]:
    """异步获取个股资金流向数据。"""
    for attempt in range(3):
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(_fetch_fund_flow_sync, code, days), timeout=30
            )
            if result:
                return result
            logger.warning("资金流向返回空 code=%s (尝试 %d/3)", code, attempt + 1)
            if attempt < 2:
                await asyncio.sleep(1)
        except asyncio.TimeoutError:
            logger.error("资金流向超时 code=%s (尝试 %d/3)", code, attempt + 1)
            if attempt < 2:
                await asyncio.sleep(1)
        except Exception as e:  # noqa: BLE001
            logger.error("资金流向失败 code=%s: %s (尝试 %d/3)", code, e, attempt + 1)
            if attempt < 2:
                await asyncio.sleep(1)
    return []


# ════════════════════════════════════════════════════════════════════
#  板块资金流向（东方财富 push2 行情接口）
# ════════════════════════════════════════════════════════════════════


def _fetch_sector_fund_flow_sync(
    sector_type: str = "industry", limit: int = 50
) -> list[dict[str, Any]]:
    """同步：获取板块资金流向排名（东方财富 push2 行情接口）。

    数据源：push2.eastmoney.com/api/qt/clist/get，与东财网页版"板块资金流"
    （data.eastmoney.com/bkzj）同源，含板块涨跌幅，金额单位为元。

    Args:
        sector_type: 'industry' = 行业板块 (m:90+t:2),
                     'concept'  = 概念板块 (m:90+t:3)
        limit: 返回数量上限

    Returns:
        板块资金流向列表，按主力净流入降序排列
    """
    # 行业板块 m:90+t:2，概念板块 m:90+t:3
    fs = "m:90+t:3" if sector_type == "concept" else "m:90+t:2"
    fields = "f12,f14,f2,f3,f6,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87"
    pz = str(max(limit, 100))

    def _request(order: str) -> list[dict[str, Any]]:
        """order='1' 主力净流入降序（流入榜），'0' 升序（流出榜）。"""
        params = urlencode(
            {
                "pn": "1",
                "pz": pz,
                "po": order,
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "fid": "f62",  # 按主力净流入排序
                "fs": fs,
                "fields": fields,
            }
        )
        url = f"http://push2.eastmoney.com/api/qt/clist/get?{params}"
        try:
            resp = _curl_get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                logger.warning("板块资金流向 HTTP %d", resp.status_code)
                return []
            data = resp.json()
        except Exception as e:  # noqa: BLE001
            logger.error("板块资金流向请求失败: %s", e)
            return []
        return ((data.get("data") or {}).get("diff")) or []

    # 同时取流入榜与流出榜，按板块代码合并去重，保证两端 TOP 榜都有数据
    merged: dict[str, dict[str, Any]] = {}
    for item in (*_request("1"), *_request("0")):
        code = str(item.get("f12", ""))
        if not code or code in merged:
            continue
        merged[code] = {
            "code": code,
            "name": str(item.get("f14", "")).strip(),
            "price": _safe_float(item.get("f2")),
            "changePct": _safe_float(item.get("f3")),
            "mainNetInflow": _safe_float(item.get("f62")),
            "mainNetInflowRatio": _safe_float(item.get("f184")),
            "superLargeNetInflow": _safe_float(item.get("f66")),
            "superLargeNetInflowRatio": _safe_float(item.get("f69")),
            "largeNetInflow": _safe_float(item.get("f72")),
            "largeNetInflowRatio": _safe_float(item.get("f75")),
            "mediumNetInflow": _safe_float(item.get("f78")),
            "mediumNetInflowRatio": _safe_float(item.get("f81")),
            "smallNetInflow": _safe_float(item.get("f84")),
            "smallNetInflowRatio": _safe_float(item.get("f87")),
        }
    result = sorted(merged.values(), key=lambda x: x["mainNetInflow"], reverse=True)
    return result


async def fetch_sector_fund_flow(
    sector_type: str = "industry", limit: int = 50
) -> list[dict[str, Any]]:
    """异步获取板块资金流向排名。"""
    for attempt in range(2):
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(_fetch_sector_fund_flow_sync, sector_type, limit),
                timeout=15,
            )
            if result:
                return result
            logger.warning("板块资金流向返回空 (尝试 %d/2)", attempt + 1)
            if attempt < 1:
                await asyncio.sleep(0.5)
        except asyncio.TimeoutError:
            logger.warning("板块资金流向超时 (尝试 %d/2)", attempt + 1)
            if attempt < 1:
                await asyncio.sleep(0.5)
        except Exception as e:  # noqa: BLE001
            logger.warning("板块资金流向失败: %s (尝试 %d/2)", e, attempt + 1)
            if attempt < 1:
                await asyncio.sleep(0.5)
    return []
