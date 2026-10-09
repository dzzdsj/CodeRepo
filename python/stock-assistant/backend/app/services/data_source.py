"""AkShare 数据源适配层：实时行情、大盘指数、股票模糊搜索。

AkShare 是同步库，所有调用通过 asyncio.to_thread 放到线程中执行，避免阻塞事件循环。

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
#  日 K 线历史
# ══════════════════════════════════════════════════════════════════════


def _fetch_tencent_kline_sync(code: str, days: int = 60) -> list[dict[str, Any]]:
    """同步：腾讯日 K 线接口（主数据源，稳定可靠）。

    接口：https://web.ifzq.gtimg.cn/appstock/app/fqkline/get
    返回 list of {time, date, open, close, high, low, volume}，按日期升序。
    """
    tencent_code = _tencent_code(code)
    url = (
        f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
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

    # 数据结构：{"data": {"sh600519": {"qfqday": [["2024-01-02","1300",...],...]}}}
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
                "volume": _safe_float(item[5]) if len(item) > 5 else 0,
            }
        )
    result.sort(key=lambda x: x["time"])
    return result


def _fetch_akshare_kline_sync(
    code: str, days: int = 60
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


async def fetch_daily_kline(code: str, days: int = 60) -> list[dict[str, Any]]:
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
#  板块资金流向（东方财富 datacenter-web）
# ════════════════════════════════════════════════════════════════════


def _fetch_sector_fund_flow_sync(
    sector_type: str = "industry", limit: int = 50
) -> list[dict[str, Any]]:
    """同步：获取板块资金流向排名（东方财富数据中心接口）。

    数据源：datacenter-web.eastmoney.com 的 RPT_FUNDFLOW_BOARD 报表，
    返回今日所有板块的资金流向数据（单位：万元）。

    Args:
        sector_type: 'industry' = 行业板块, 'concept' = 概念板块
                     （注：当前接口不区分行业/概念，返回全部板块）
        limit: 返回数量上限

    Returns:
        板块资金流向列表，按主力净流入降序排列
    """
    today = datetime.now().strftime("%Y-%m-%d")
    filter_str = f"(TRADE_DATE>='{today}')"
    params = urlencode(
        {
            "reportName": "RPT_FUNDFLOW_BOARD",
            "columns": "ALL",
            "filter": filter_str,
            "pageNumber": "1",
            "pageSize": str(max(limit, 100)),
            "sortColumns": "NET_INFLOW",
            "sortTypes": "-1",
        }
    )
    url = f"http://datacenter-web.eastmoney.com/api/data/v1/get?{params}"
    try:
        resp = _curl_get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:  # noqa: BLE001
        logger.error("板块资金流向请求失败: %s", e)
        return []

    if resp.status_code != 200:
        logger.warning("板块资金流向 HTTP %d", resp.status_code)
        return []

    try:
        data = resp.json()
    except Exception as e:  # noqa: BLE001
        logger.error("板块资金流向 JSON 解析失败: %s", e)
        return []

    if not data.get("success"):
        logger.warning("板块资金流向接口返回失败: %s", data.get("message"))
        return []

    rows = ((data.get("result") or {}).get("data")) or []
    result: list[dict[str, Any]] = []
    for item in rows:
        # 接口单位为万元，转换为元
        main_net = _safe_float(item.get("NET_INFLOW"))
        if main_net is not None:
            main_net *= 10000
        super_large = _safe_float(item.get("SUPERDEAL_AMOUNT"))
        if super_large is not None:
            super_large *= 10000
        large = _safe_float(item.get("BIGDEAL_AMOUNT"))
        if large is not None:
            large *= 10000
        medium = _safe_float(item.get("MIDDEAL_AMOUNT"))
        if medium is not None:
            medium *= 10000
        small = _safe_float(item.get("SMALLDEAL_AMOUNT"))
        if small is not None:
            small *= 10000
        amount = _safe_float(item.get("AMOUNT"))
        if amount is not None:
            amount *= 10000

        # 粗略区分行业/概念板块：名称含"概念/风格/指数/组合"归为概念板块
        name = str(item.get("BOARD_NAME", "")).strip()
        concept_keywords = ("概念", "风格", "指数", "组合", "茅", "宁", "经济")
        is_concept = any(kw in name for kw in concept_keywords)
        if sector_type == "industry" and is_concept:
            continue
        if sector_type == "concept" and not is_concept:
            continue

        result.append(
            {
                "code": str(item.get("BOARD_CODE1", "")),
                "name": name,
                "price": amount,  # 成交额作为 price 字段展示
                "changePct": 0.0,  # 该接口无涨跌幅
                "mainNetInflow": main_net,
                "mainNetInflowRatio": _safe_float(item.get("INFLOW_RATIO")),
                "superLargeNetInflow": super_large,
                "superLargeNetInflowRatio": 0.0,
                "largeNetInflow": large,
                "largeNetInflowRatio": 0.0,
                "mediumNetInflow": medium,
                "mediumNetInflowRatio": 0.0,
                "smallNetInflow": small,
                "smallNetInflowRatio": 0.0,
            }
        )
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
