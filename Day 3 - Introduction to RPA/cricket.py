from playwright.sync_api import sync_playwright

def get_live_score():
    # Initializes the Playwright context manager.
    with sync_playwright() as p:
        # Launches Microsoft Edge by explicitly specifying the msedge execution channel.
        browser = p.chromium.launch(channel="msedge", headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Navigating to cricbuzz.com using Microsoft Edge...")
        # Directs the Edge browser instance to the targeted live score page URL.
        page.goto("https://cricbuzz.com", wait_until="domcontentloaded")
        
        # Defines the target CSS selectors for the match display cards.
        score_selector = "li.cb-match-lst, div.cb-mtch-blk, a.cb-mat-mnu-itm"
        
        print("Waiting for any available live score element to load...")
        try:
            # Instructs the framework thread to wait dynamically for a maximum of 10 seconds.
            page.wait_for_selector(score_selector, timeout=10000)
            
            # Extracts the raw text string value from the first matched element layout block.
            first_score_element = page.locator(score_selector).first
            score_text = first_score_element.inner_text()
            
            # Formats and cleans newline variations to present clean output chunks on your system console.
            clean_score = " | ".join([line.strip() for line in score_text.splitlines() if line.strip()])
            
            print("\n--- Live Score Text Captured ---")
            print(clean_score)
            print("--------------------------------\n")
            
            # Automatically flushes the visible screen canvas viewport state out to a PNG image file.
            page.screenshot(path="score.png")
            print("Screenshot successfully saved as 'score.png'")
            
        except Exception:
            # Catches the timeout exception gracefully and prints the fallback message instead of crashing.
            print("\n--------------------------------")
            print("No score information found")
            print("--------------------------------\n")
            
            # Saves a screenshot of the current page state to help diagnose why it failed to load.
            page.screenshot(path="error_page.png")
            print("Saved diagnostic image as 'error_page.png'")
        
        # Releases browser processes and cleans memory tracking vectors gracefully.
        context.close()
        browser.close()

if __name__ == "__main__":
    # Provides an operational runtime entry boundary framework for direct execution routines.
    get_live_score()