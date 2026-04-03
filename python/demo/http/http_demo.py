import requests

def http_get():
    url = 'https://cn.javd.me/movies/search?'
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    params = {
        "q": "美女",
        "page": 6
    }
    resp = requests.get(url,headers=headers,params=params,timeout=10,verify=False)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    html = resp.text
    print(html)

if __name__ == '__main__':
    http_get()