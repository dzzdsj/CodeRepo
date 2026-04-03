from curl_cffi import requests
def test():
    resp = requests.get(
       "https://cn.javd.me/movies/search",
        params={"q": "美女", "page": 6},
        impersonate="chrome120"
    )

    print(resp.status_code)
    print(resp.text[:500])

if __name__ == '__main__':
    test()