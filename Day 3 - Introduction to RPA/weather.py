import os
import re
import datetime
from playwright.sync_api import sync_playwright
from openpyxl import Workbook, load_workbook

def get_weather_data() -> str:
    # Uses Playwright to drive Microsoft Edge and scan the raw text elements for the temperature.
    with sync_playwright() as p:
        print("Opening AccuWeather in Microsoft Edge...")
        browser = p.chromium.launch(channel="msedge", headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Accesses the target web portal and waits for the page structure to settle.
        page.goto("https://www.accuweather.com/", wait_until="networkidle")
        
        print("Scanning the webpage content for any temperature markers...")
        # Extracts all visible inner text from the root HTML body.
        page.wait_for_selector("body")
        full_page_text = page.locator("body").inner_text()
        
        # Search the page text for a standard temperature string (e.g., 29° or 29°C).
        match = re.search(r"(\d+°C?)", full_page_text)
        
        if match:
            clean_temp = match.group(1)
            print(f"Dynamic text scan successful. Captured: {clean_temp}")
        else:
            # Fallback text tracking: Look for prominent temperature nodes directly by layout query matching.
            print("Regex pattern not found immediately. Scanning direct layout text frames...")
            temp_elements = page.locator('span:has-text("°"), div:has-text("°")').all_inner_texts()
            # Filters out long text blocks, leaving only the short text strings like "29°".
            valid_temps = [t.strip() for t in temp_elements if t.strip() and len(t.strip()) <= 5 and any(char.isdigit() for char in t)]
            
            if valid_temps:
                clean_temp = valid_temps[0]
                print(f"Layout node scan successful. Captured: {clean_temp}")
            else:
                raise ValueError("Could not find any visible text strings matching a temperature pattern ('°') on the page canvas.")
        
        context.close()
        browser.close()
        return clean_temp

def update_excel_report(temperature: str):
    # Generates a dynamic file name bound explicitly to today's date.
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"daily_report_{today_date}.xlsx"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Opens a pre-existing workbook or starts a fresh data sheet if none exists.
    if os.path.exists(filename):
        wb = load_workbook(filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        # Creates the column header layout.
        ws.append(["Date & Time", "Fetched Temperature", "Comments"])
    
    # Selects an operational comment based on the extracted data.
    if any(char in temperature for char in ["2", "3"]):
        comment = "Good for outdoor activities."
    else:
        comment = "Normal weather conditions."
        
    # Injects the data row into the spreadsheet sheet template.
    ws.append([current_time, temperature, comment])
    
    wb.save(filename)
    print(f"Excel report file successfully updated and saved: {filename}")

if __name__ == "__main__":
    try:
        live_site_temp = get_weather_data()
        update_excel_report(live_site_temp)
    except Exception as error:
        print("\n------------------------------------------------------------")
        print(f"Automation execution failed: {str(error)}")
        print("The script was unable to pull the data because the page elements were blocked.")
        print("------------------------------------------------------------\n")