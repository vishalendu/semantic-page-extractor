import asyncio
import json

from playwright.async_api import async_playwright

from semantic_page_extractor import extract_page_semantics


async def main() -> None:
    html = """
    <html><body>
      <h1>Login</h1>
      <form>
        <label for='email'>Email</label><input id='email' type='email' required>
        <label for='pwd'>Password</label><input id='pwd' type='password'>
        <button type='submit'>Sign in</button>
      </form>
      <a href='/help'>Help</a>
    </body></html>
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html)
        summary = await extract_page_semantics(page)
        print(json.dumps(summary.model_dump(mode="json"), indent=2, sort_keys=True))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
