import json
import time
import requests
import os

# =====================
# 配置文件和资源文件
# =====================
CONFIG_FILE = 'config.json'
WANTED_FILE = 'wanted.txt'
LOG_FILE = 'download.log'

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"[!] 配置文件不存在: {CONFIG_FILE}")

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

jackett_url = cfg['jackett_url'].rstrip("/")
jackett_key = cfg['jackett_api_key']
qb_url = cfg['qb_url'].rstrip("/")
qb_user = cfg['qb_user']
qb_pass = cfg['qb_pass']


# =====================
# 登录 qBittorrent
# =====================
def login_qb():
    session = requests.Session()
    login_url = f"{qb_url}/api/v2/auth/login"
    r = session.post(login_url, data={"username": qb_user, "password": qb_pass})
    if r.status_code == 200 and "Ok." in r.text:
        print("[+] 登录 qBittorrent 成功")
        return session
    else:
        print(f"[!] 登录失败: {r.status_code} {r.text}")
        raise SystemExit

session = login_qb()


# =====================
# 读取目标文件列表
# =====================
if not os.path.exists(WANTED_FILE):
    raise FileNotFoundError(f"[!] 文件不存在: {WANTED_FILE}")

with open(WANTED_FILE, 'r', encoding='utf-8') as f:
    keywords = [line.strip() for line in f if line.strip()]


# =====================
# 搜索并添加下载
# =====================
for kw in keywords:
    print(f"\n🎬 搜索: {kw}")
    try:
        # Jackett 搜索
        r = requests.get(
            f"{jackett_url}/api/v2.0/indexers/all/results",
            params={"apikey": jackett_key, "Query": kw},
            timeout=20
        )
        data = r.json()
        results = data.get('Results', [])
        if not results:
            print(f"[⚠] 未找到结果: {kw}")
            continue

        # 按做种数排序
        results.sort(key=lambda x: x.get('Seeders', 0), reverse=True)
        top = results[0]

        # 严格校验 MagnetUri
        magnet = top.get('MagnetUri')
        if not magnet or not magnet.startswith("magnet:?xt=urn:btih:"):
            print(f"[⚠] 无效 MagnetUri，跳过: {top.get('Title', '未知标题')}")
            # 可选择打印更多调试信息
            print(f"调试输出: MagnetUri={magnet}")
            continue

        size_gb = top.get('Size', 0) / (1024**3)
        print(f"[√] 发现: {top['Title']} | 做种数: {top.get('Seeders',0)} | 大小: {size_gb:.2f} GB")
        print(f"Magnet: {magnet}")

        # 添加到 qBittorrent
        add_url = f"{qb_url}/api/v2/torrents/add"
        resp = session.post(add_url, data={"urls": magnet})
        if resp.status_code == 200:
            print("[📥] 已添加到下载队列")
            log_status = "成功"
        else:
            print(f"[⚠] 添加失败: {resp.status_code} {resp.text}")
            log_status = "失败"

        # 写日志
        with open(LOG_FILE, 'a', encoding='utf-8') as logf:
            logf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [{log_status}] {kw} | {magnet}\n")

        time.sleep(2)

    except Exception as e:
        print(f"[❌] 搜索或下载失败 {kw}: {e}")

print("\n✅ 所有任务处理完成！")