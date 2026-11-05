from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Launch the browser and open a new page
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Navigation
    page.goto("https://accuweather.com")
    page.screenshot(path="accuweather.png")

    # Clicking
    page.click("text=Full Forecast")
    page.screenshot(path="full_forecast.png")

    # Typing
    page.fill("input[name='q']", "Playwright")
    page.press("input[name='q']", "Enter")
    page.screenshot(path="search_results.png")

    # Waiting for elements
    page.wait_for_selector("text=Playwright: Fast and reliable end-to-end testing")
    page.screenshot(path="search_results_loaded.png")

    # Extracting the data
    title = page.title()
    print(f"Page title: {title}")

    # Clean up
    browser.close()
