"""
RedNote auto-publishing module - Using Playwright (more stable)
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright, Page
from utils.logger import setup_logger

logger = setup_logger()


class XiaohongshuPlaywrightPublisher:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.cookie_file = Path("data/xiaohongshu_state.json")
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)

    async def cookie_auth(self):
        """Verify if cookie is valid"""
        if not self.cookie_file.exists():
            return False

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=str(self.cookie_file))
            page = await context.new_page()

            try:
                await page.goto("https://creator.xiaohongshu.com/publish/publish")
                await page.wait_for_url("https://creator.xiaohongshu.com/publish/publish", timeout=5000)

                if await page.get_by_text('Phone Login').count() or await page.get_by_text('Scan Login').count():
                    logger.warning("Cookie expired")
                    await context.close()
                    await browser.close()
                    return False

                logger.info("Cookie valid")
                await context.close()
                await browser.close()
                return True

            except Exception as e:
                logger.warning(f"Cookie verification failed: {e}")
                await context.close()
                await browser.close()
                return False

    async def login_and_save_cookie(self):
        """Manual login and save cookie"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://creator.xiaohongshu.com/")

            print("\n" + "="*60)
            print("[Manual Login]")
            print("="*60)
            print("Please complete login in the browser:")
            print("1. Enter phone number")
            print("2. Get and enter verification code")
            print("3. Complete login")
            print("\nAfter successful login, press Enter to continue...")
            print("="*60)

            await page.pause()

            await context.storage_state(path=str(self.cookie_file))
            logger.info("Cookie saved")

            await context.close()
            await browser.close()

    async def publish_article(self, title, content, images=None):
        """Publish article"""
        try:
            if not await self.cookie_auth():
                logger.info("Need to login again")
                await self.login_and_save_cookie()

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    viewport={"width": 1600, "height": 900},
                    storage_state=str(self.cookie_file)
                )
                page = await context.new_page()

                print("\n" + "="*60)
                print("[Starting Auto-Publishing]")
                print("="*60)

                await page.goto("https://creator.xiaohongshu.com/publish/publish", timeout=60000)
                await page.wait_for_load_state("networkidle")
                logger.info("Publishing page opened")

                try:
                    await page.evaluate("""
                        const buttons = Array.from(document.querySelectorAll('span.title'));
                        const uploadBtn = buttons.find(btn => btn.textContent.includes('Upload Article'));
                        if (uploadBtn) {
                            uploadBtn.click();
                        }
                    """)
                    logger.info("Clicked upload article button")
                    await asyncio.sleep(3)

                    await page.wait_for_load_state("networkidle", timeout=10000)
                except Exception as e:
                    logger.warning(f"Failed to click upload button: {e}, may already be on article publishing page")

                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(3)

                if not images or len(images) == 0:
                    logger.error("No images provided")
                    await context.close()
                    await browser.close()
                    return False

                valid_images = [img for img in images if Path(img).exists()]
                if not valid_images:
                    logger.error("No valid image paths")
                    await context.close()
                    await browser.close()
                    return False

                valid_images = valid_images[:9]
                logger.info(f"Preparing to upload {len(valid_images)} images")

                try:
                    upload_input = None
                    selectors = [
                        "input[type='file'][accept*='image']",
                        "input.upload-input[accept*='image']",
                        "div.upload-wrapper input[type='file']",
                        "input[type='file']"
                    ]

                    for selector in selectors:
                        try:
                            upload_input = page.locator(selector).first
                            if await upload_input.count() > 0:
                                logger.info(f"Found upload input: {selector}")
                                break
                        except:
                            continue

                    if not upload_input or await upload_input.count() == 0:
                        logger.error("Image upload input not found")
                        await context.close()
                        await browser.close()
                        return False

                    await upload_input.set_input_files(valid_images)
                    logger.info(f"✓ Uploaded {len(valid_images)} images")

                except Exception as e:
                    logger.error(f"Failed to upload images: {e}")
                    await context.close()
                    await browser.close()
                    return False

                await asyncio.sleep(5)

                truncated_title = title[:20] if len(title) > 20 else title
                if len(title) > 20:
                    logger.info(f"Title too long, truncated: {title} -> {truncated_title}")

                title_input = page.locator('input[placeholder*="Enter Title"]').first
                if await title_input.count():
                    await title_input.fill(truncated_title)
                    logger.info(f"✓ Title entered: {truncated_title}")
                else:
                    logger.warning("Title input not found")

                content_editor = page.locator("div.tiptap.ProseMirror").first
                if await content_editor.count():
                    await content_editor.click()
                    await content_editor.fill(content)
                    logger.info("✓ Content entered")
                else:
                    logger.warning("Content editor not found")

                await asyncio.sleep(3)

                publish_button = page.locator("button:has-text('Publish')")
                if await publish_button.count():
                    await publish_button.click()
                    logger.info("✓ Clicked publish button")
                    await asyncio.sleep(5)
                    logger.info("✅ Article published successfully!")
                    print("="*60)

                    await context.close()
                    await browser.close()
                    return True
                else:
                    logger.error("Publish button not found")
                    await context.close()
                    await browser.close()
                    return False

        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def publish_to_xiaohongshu_playwright(phone_number, title, content, images=None):
    """Publish to RedNote using Playwright"""
    publisher = XiaohongshuPlaywrightPublisher(phone_number)
    return asyncio.run(publisher.publish_article(title, content, images))
