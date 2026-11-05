from playwright.sync_api import sync_playwright
from datetime import datetime

print("Starting the Playwright automation script...")
print(f"Script started at: {datetime.now()}")

# Daily Weather Report Bot
# Chromium -> weather site -> Extract the report -> Screenshot -> final text file
with sync_playwright() as p:
    print("Launching the Chromium browser...")
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Navigating to the AccuWeather website...")
    page.goto("https://accuweather.com")
    page.screenshot(path="accuweather.png")

    print("Extracting the weather report...")
    weather_report = page.inner_text("div.current-weather-card")
    print(f"Current Weather Report: {weather_report}")

    print("Saving the weather report to a text file...")
    with open("weather_report.txt", "w") as file:
        file.write(f"Weather Report for Chennai on {datetime.now()}:\n\n")
        file.write(weather_report)

    print("Closing the browser...")
    browser.close()
    print(f"Script completed at: {datetime.now()}")
