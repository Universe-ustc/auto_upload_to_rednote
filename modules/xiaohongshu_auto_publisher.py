"""
RedNote auto-publishing module - Fully automated publishing based on cookies
"""
import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.logger import setup_logger

logger = setup_logger()


class XiaohongshuAutoPublisher:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.driver = None
        self.cookie_file = Path("data/xiaohongshu_cookies.json")
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)

    def init_browser(self):
        """Initialize browser"""
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })

        logger.info("Browser started")

    def load_cookies(self):
        """Load cookies"""
        if not self.cookie_file.exists():
            return False

        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)

            self.driver.get("https://creator.xiaohongshu.com/")
            time.sleep(2)

            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Failed to add cookie: {e}")

            self.driver.refresh()
            time.sleep(3)

            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".name-box"))
                )
                logger.info("Cookie login successful")
                return True
            except TimeoutException:
                logger.warning("Cookie expired")
                return False

        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False

    def save_cookies(self):
        """Save cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            logger.info("Cookies saved")
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")

    def login_with_phone(self):
        """Phone verification code login"""
        try:
            self.driver.get("https://creator.xiaohongshu.com/login")
            time.sleep(3)

            phone_input = None
            phone_selectors = [
                ".css-1hguu2q",
                "input[type='text']",
                "input[placeholder*='phone']",
                ".phone-input",
                "input.input"
            ]

            for selector in phone_selectors:
                try:
                    phone_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if phone_input and phone_input.is_displayed():
                        break
                except:
                    continue

            if not phone_input:
                logger.warning("Phone input not found, switching to manual login mode")
                return self._manual_login()

            try:
                phone_input.send_keys("[YOUR_PHONE_NUMBER]")
                logger.info(f"Phone number entered")
            except Exception as e:
                logger.warning(f"Failed to auto-enter phone number: {e}, switching to manual login mode")
                return self._manual_login()

            send_code_selectors = [
                'div.css-14tu84b:nth-child(1) > div:nth-child(2) > div:nth-child(3)',
                'button:contains("Send Code")',
                '.send-code-btn',
                'button[class*="send"]'
            ]

            send_code_btn = None
            for selector in send_code_selectors:
                try:
                    send_code_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if send_code_btn and send_code_btn.is_displayed():
                        break
                except:
                    continue

            if not send_code_btn:
                logger.warning("Send code button not found, switching to manual login mode")
                return self._manual_login()

            try:
                send_code_btn.click()
                logger.info("Verification code sent")
            except Exception as e:
                logger.warning(f"Failed to click send code button: {e}, switching to manual login mode")
                return self._manual_login()

            print("\n" + "="*60)
            print("[Verification Code Login]")
            print("="*60)
            print(f"Verification code sent to phone: [YOUR_PHONE_NUMBER]")
            code = input("Please enter 6-digit verification code: ").strip()
            print("="*60)

            code_input = None
            code_selectors = [
                "#page > div > div.content > div.con > div.login-box-container > div > div > div > div > div:nth-child(2) > div.css-6oq7i4 > div:nth-child(1) > div:nth-child(2) > input",
                "input[type='text'][maxlength='6']",
                "input[placeholder*='code']",
                ".code-input"
            ]

            for selector in code_selectors:
                try:
                    code_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if code_input and code_input.is_displayed():
                        break
                except:
                    continue

            if not code_input:
                logger.error("Verification code input not found")
                return False

            code_input.send_keys(code)

            login_btn = None
            login_selectors = [
                "#page > div > div.content > div.con > div.login-box-container > div > div > div > div > div:nth-child(2) > button",
                "button[type='submit']",
                "button:contains('Login')",
                ".login-btn"
            ]

            for selector in login_selectors:
                try:
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_btn and login_btn.is_displayed():
                        break
                except:
                    continue

            if not login_btn:
                logger.error("Login button not found")
                return False

            login_btn.click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".name-box"))
            )

            name = self.driver.find_element(By.CSS_SELECTOR, ".name-box").text
            logger.info(f"Login successful: {name}")

            self.save_cookies()
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def _manual_login(self):
        """Fully manual login mode"""
        print("\n" + "="*60)
        print("[Manual Login Mode]")
        print("="*60)
        print("Automated login failed, please complete the following in the browser:")
        print("1. Enter phone number")
        print("2. Click send verification code")
        print("3. Enter verification code")
        print("4. Click login")
        print("\nAfter login, press Enter to continue...")
        print("="*60)
        input()

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".name-box"))
            )
            name = self.driver.find_element(By.CSS_SELECTOR, ".name-box").text
            logger.info(f"Manual login successful: {name}")
            self.save_cookies()
            return True
        except:
            logger.error("Manual login failed, login status not detected")
            return False

    def publish_article(self, title, content, images=None):
        """Auto-publish article (enhanced with JavaScript)"""
        try:
            self.driver.get("https://creator.xiaohongshu.com/publish/publish")
            time.sleep(5)

            print("\n" + "="*60)
            print("[Starting Auto-Publishing]")
            print("="*60)

            if not images or len(images) == 0:
                logger.error("No images provided, cannot publish article")
                return False

            valid_images = [img for img in images if Path(img).exists()]

            if not valid_images:
                logger.error("No valid image paths")
                return False

            valid_images = valid_images[:9]
            logger.info(f"Preparing to upload {len(valid_images)} images")

            find_upload_js = """
            var inputs = document.querySelectorAll('input[type="file"]');
            for (var i = 0; i < inputs.length; i++) {
                if (inputs[i].accept && inputs[i].accept.includes('image')) {
                    return inputs[i];
                }
            }
            return inputs[0];
            """

            upload_input = self.driver.execute_script(find_upload_js)

            if not upload_input:
                logger.error("Image upload input not found")
                return False

            images_path = "\n".join(valid_images)

            try:
                upload_input.send_keys(images_path)
                logger.info(f"✓ Uploaded {len(valid_images)} images")
                time.sleep(10)
            except Exception as e:
                logger.error(f"Failed to upload images: {e}")
                return False

            fill_title_js = f"""
            var titleInputs = document.querySelectorAll('input[type="text"]');
            for (var i = 0; i < titleInputs.length; i++) {{
                var placeholder = titleInputs[i].placeholder || '';
                if (placeholder.includes('Title') || titleInputs[i].className.includes('title')) {{
                    titleInputs[i].value = `{title.replace('`', '\\`')}`;
                    titleInputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    return true;
                }}
            }}
            return false;
            """

            title_filled = self.driver.execute_script(fill_title_js)
            if title_filled:
                logger.info(f"✓ Title entered: {title[:30]}...")
            else:
                logger.warning("⚠ Title input not found")

            content_escaped = content.replace('\\', '\\\\').replace('`', '\\`').replace('\n', '\\n')

            fill_content_js = f"""
            var textareas = document.querySelectorAll('textarea');
            for (var i = 0; i < textareas.length; i++) {{
                if (textareas[i].offsetParent !== null) {{
                    textareas[i].value = `{content_escaped}`;
                    textareas[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    return true;
                }}
            }}
            return false;
            """

            content_filled = self.driver.execute_script(fill_content_js)
            if content_filled:
                logger.info("✓ Content entered")
            else:
                logger.warning("⚠ Content input not found")

            logger.info("Waiting for image processing...")
            time.sleep(8)

            click_publish_js = """
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                var btnText = buttons[i].textContent || buttons[i].innerText;
                if (btnText.includes('Publish') && buttons[i].offsetParent !== null) {
                    buttons[i].click();
                    return true;
                }
            }
            return false;
            """

            publish_clicked = self.driver.execute_script(click_publish_js)

            if publish_clicked:
                logger.info("✓ Clicked publish button")
                time.sleep(5)
                logger.info("✅ Article published successfully!")
                print("="*60)
                return True
            else:
                logger.error("✗ Publish button not found")
                return False

        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def close(self):
        """Close browser"""
        if self.driver:
            time.sleep(3)
            self.driver.quit()
            logger.info("Browser closed")


def publish_to_xiaohongshu_auto(phone_number, title, content, images=None):
    """Convenient function for auto-publishing to RedNote"""
    publisher = XiaohongshuAutoPublisher(phone_number)

    try:
        publisher.init_browser()

        if not publisher.load_cookies():
            logger.info("Cookie expired, phone verification login required")
            if not publisher.login_with_phone():
                logger.error("Login failed")
                return False

        result = publisher.publish_article(title, content, images)
        return result

    except Exception as e:
        logger.error(f"Publishing process error: {e}")
        return False
    finally:
        publisher.close()
