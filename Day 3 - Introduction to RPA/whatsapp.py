
import asyncio
from playwright.async_api import async_playwright

# Contact details
CONTACTS = [
    {"phone": "919884552537", "name": "Pradeepraj"},
    {"phone": "917397368376", "name": "Andal"}
]


# Main function to run WhatsApp automation
async def run_bot():

    async with async_playwright() as p:

        print("Launching Microsoft Edge...")

        # Open Microsoft Edge with a separate browser session
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./whatsapp_session",
            channel="msedge",
            headless=False
        )

        # Open a new browser tab
        page = await context.new_page()

        print("Opening WhatsApp Web...")

        # Navigate to WhatsApp Web
        await page.goto("https://web.whatsapp.com")

        print("Please scan the QR code if required.")

        try:
            # Wait for WhatsApp chat list to load
            await page.wait_for_selector(
                'div[data-testid="chat-list"]',
                timeout=60000
            )

            print("Logged in successfully!")

            # Send messages to the contacts
            for contact in CONTACTS:

                try:
                    print("Opening chat with " + contact["name"])

                    # Open the contact's WhatsApp chat
                    target_url = (
                        "https://web.whatsapp.com/send/?phone="
                        + contact["phone"]
                    )

                    await page.goto(target_url)

                    # Wait for the message input box
                    input_box = (
                        'div[data-testid="conversation-compose-box-input"]'
                    )

                    await page.wait_for_selector(
                        input_box,
                        timeout=20000
                    )

                    # Prepare the personalized message
                    message = (
                        "Hello " + contact["name"]
                        + ", this is a test message from my automation bot."
                    )

                    # Type the message
                    await page.locator(input_box).fill(message)

                    # Send the message
                    await page.keyboard.press("Enter")

                    print("Message sent to " + contact["name"])

                    # Wait before moving to the next contact
                    await asyncio.sleep(4)

                except Exception as error:
                    print(
                        "Could not send to "
                        + contact["name"]
                        + ": "
                        + str(error)
                    )

        except Exception as error:
            print("WhatsApp login or loading failed:", error)

        finally:
            # Close the browser session
            await context.close()


# Start the program
if __name__ == "__main__":
    asyncio.run(run_bot())
