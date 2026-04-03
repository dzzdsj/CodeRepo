from playwright.sync_api import sync_playwright

def test():
    url = "https://cn.javd.me/movies/search?q=美女&page=6"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, wait_until="domcontentloaded")

        # 等 Cloudflare 校验结束
        page.wait_for_function(
            "document.title !== 'Just a moment...'",
            timeout=60000
        )

        html = page.content()
        print(html[:500])

        browser.close()

if __name__ == '__main__':
    test()