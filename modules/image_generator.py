"""
AI image generation module - Generate cover images for articles
"""
import requests
import base64
import random
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

IMAGE_STYLES = [
    "futuristic holographic interface, neon blue and cyan accents",
    "abstract neural network visualization, purple and gold gradient",
    "minimalist tech dashboard, dark mode with orange highlights",
    "geometric AI brain concept, teal and coral colors",
    "floating 3D cubes and spheres, gradient mesh style",
    "digital data streams, emerald green and silver",
    "cyberpunk cityscape silhouette, magenta and blue",
    "organic circuit patterns, warm amber and deep blue",
]


class ImageGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1/images/generations"

    def generate_cover_image(self, title, description=""):
        """
        Generate cover image

        Args:
            title: Article title
            description: Article description or summary

        Returns:
            str: Path to generated image, None if failed
        """
        prompt = self._build_prompt(title, description)

        logger.info(f"Generating cover image, prompt: {prompt[:100]}...")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "Kwai-Kolors/Kolors",
                "prompt": prompt,
                "image_size": "1024x1024",
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "negative_prompt": "low quality, blurry, distorted, ugly, bad anatomy, watermark, text, signature",
                "batch_size": 1
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"Image generation failed: {response.status_code} - {response.text}")
                return None

            result = response.json()

            if 'images' in result and len(result['images']) > 0:
                image_data = result['images'][0]

                image_path = self._save_image(image_data, title)

                if image_path:
                    logger.info(f"Cover image generated: {image_path}")
                    return image_path
                else:
                    logger.error("Failed to save image")
                    return None
            else:
                logger.error("No image in API response")
                return None

        except Exception as e:
            logger.error(f"Failed to generate cover image: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _build_prompt(self, title, description):
        """Build prompt for image generation"""
        style = random.choice(IMAGE_STYLES)

        content_for_prompt = (description or "").strip()
        if len(content_for_prompt) > 600:
            content_for_prompt = content_for_prompt[:600] + "..."

        if content_for_prompt:
            base_prompt = f"A cover image for a tech blog post. The article content: {content_for_prompt}. "
        else:
            base_prompt = f"A cover image for a tech blog post titled: {title}. "

        base_prompt += f"Visual style: {style}. "
        base_prompt += "Clean design, professional look, suitable for social media, "
        base_prompt += "high quality, 4k resolution, minimalist style, no text or watermarks"

        return base_prompt

    def _save_image(self, image_data, title):
        """Save image locally"""
        try:
            save_dir = Path("data/images/generated")
            save_dir.mkdir(parents=True, exist_ok=True)

            import time
            timestamp = int(time.time())
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:30]
            filename = f"cover_{safe_title}_{timestamp}.png"
            file_path = save_dir / filename

            if isinstance(image_data, dict):
                if 'url' in image_data:
                    img_response = requests.get(image_data['url'], timeout=30)
                    if img_response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            f.write(img_response.content)
                        return str(file_path)
                elif 'b64_json' in image_data:
                    img_bytes = base64.b64decode(image_data['b64_json'])
                    with open(file_path, 'wb') as f:
                        f.write(img_bytes)
                    return str(file_path)
            elif isinstance(image_data, str):
                if image_data.startswith('http'):
                    img_response = requests.get(image_data, timeout=30)
                    if img_response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            f.write(img_response.content)
                        return str(file_path)
                else:
                    img_bytes = base64.b64decode(image_data)
                    with open(file_path, 'wb') as f:
                        f.write(img_bytes)
                    return str(file_path)

            return None

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return None


def generate_cover_image(api_key, title, description=""):
    """Convenience function to generate cover image"""
    generator = ImageGenerator(api_key)
    return generator.generate_cover_image(title, description)
