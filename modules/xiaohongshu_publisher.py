"""
RedNote publisher module - Semi-automated publishing (more reliable)
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import setup_logger
import pyperclip

logger = setup_logger()


class XiaohongshuPublisher:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.driver = None

    def init_browser(self):
        """Initialize browser"""
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-data-dir=./chrome_data')

        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        logger.info("Browser started")

    def manual_login_guide(self):
        """Manual login guide"""
        self.driver.get("https://creator.xiaohongshu.com/")
        logger.info("Opened RedNote creator platform")

        print("\n" + "="*60)
        print("[RedNote Login Guide]")
        print("="*60)
        print("1. Browser has opened RedNote creator platform")
        print("2. Please complete login manually (scan QR code or verification code)")
        print("3. After successful login, press Enter to continue...")
        print("="*60)
        input()

        logger.info("User has completed login")

    def publish_article_semi_auto(self, title, content, images=None):
        """Semi-automated article publishing (supports images)"""
        try:
            wait = WebDriverWait(self.driver, 20)

            print("\n" + "="*60)
            print("[Starting Publishing Process]")
            print("="*60)

            try:
                time.sleep(3)

                publish_selectors = [
                    "//button[contains(text(), 'Publish Note')]",
                    "//button[contains(text(), 'Publish')]",
                    "//a[contains(@href, 'publish')]",
                    "//*[contains(text(), 'Create')]"
                ]

                publish_btn = None
                for selector in publish_selectors:
                    try:
                        publish_btn = self.driver.find_element(By.XPATH, selector)
                        if publish_btn:
                            break
                    except:
                        continue

                if publish_btn:
                    publish_btn.click()
                    logger.info("Clicked publish button")
                    time.sleep(2)
                else:
                    print("⚠️  Publish button not found, please click [Publish Note] manually")
                    input("After clicking, press Enter to continue...")

            except Exception as e:
                logger.warning(f"Failed to auto-click publish button: {e}")
                print("⚠️  Please click [Publish Note] manually")
                input("After clicking, press Enter to continue...")

            full_content = f"{title}\n\n{content}"
            try:
                pyperclip.copy(full_content)
                print("\n✅ Content copied to clipboard")
            except:
                print("\n⚠️  Unable to auto-copy, please manually copy the following content:")
                print("-" * 60)
                print(full_content)
                print("-" * 60)

            print("\n[Publishing Steps]")
            print("1. Paste content in RedNote editor (Ctrl+V)")

            if images and len(images) > 0:
                print(f"\n2. Add images (total {len(images)} images):")
                for i, img_path in enumerate(images, 1):
                    print(f"   Image {i}: {img_path}")
                print("   Tip: You can drag and drop images to the editor")
            else:
                print("\n2. Add cover image (optional)")

            print("\n3. Add topic tags (recommended: #AI #Agent #Tech)")
            print("4. Click [Publish] button")
            print("5. Press Enter after completion...")
            print("="*60)

            input()

            logger.info("Article published successfully")
            return True

        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            return False

    def close(self):
        """Close browser"""
        if self.driver:
            print("\nClose browser? (y/n): ", end='')
            choice = input().strip().lower()
            if choice == 'y':
                self.driver.quit()
                logger.info("Browser closed")
            else:
                print("Browser remains open")


def publish_to_xiaohongshu(phone_number, title, content, images=None):
    """Convenient function to publish to RedNote (semi-automated, supports images)"""
    publisher = XiaohongshuPublisher(phone_number)

    try:
        publisher.init_browser()

        publisher.manual_login_guide()

        result = publisher.publish_article_semi_auto(title, content, images)
        return result

    finally:
        publisher.close()
