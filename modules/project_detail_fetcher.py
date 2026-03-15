"""
Project detail fetching module - Deep retrieval of GitHub project technical information and images
"""
import requests
from bs4 import BeautifulSoup
from utils.logger import setup_logger
import os
from pathlib import Path

logger = setup_logger()


class ProjectDetailFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.images_dir = Path("data/images")
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def fetch_github_readme(self, repo_url):
        """Fetch README content from GitHub project"""
        try:
            if 'github.com' in repo_url:
                parts = repo_url.replace('https://github.com/', '').split('/')
                if len(parts) >= 2:
                    owner, repo = parts[0], parts[1]
                    readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"

                    response = requests.get(readme_url, headers=self.headers, timeout=10)
                    if response.status_code == 404:
                        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
                        response = requests.get(readme_url, headers=self.headers, timeout=10)

                    if response.status_code == 200:
                        return response.text[:3000]

        except Exception as e:
            logger.warning(f"Failed to fetch README {repo_url}: {e}")

        return None

    def fetch_github_image(self, repo_url):
        """Fetch image from GitHub project (prioritize social preview image)"""
        try:
            if 'github.com' not in repo_url:
                return None

            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) < 2:
                return None

            owner, repo = parts[0], parts[1]

            social_preview_url = f"https://opengraph.githubassets.com/1/{owner}/{repo}"
            img_path = self.download_image(social_preview_url, f"{owner}_{repo}_social")
            if img_path:
                logger.info(f"Using GitHub social preview image: {owner}/{repo}")
                return img_path

            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
            response = requests.get(readme_url, headers=self.headers, timeout=10)

            if response.status_code == 404:
                readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
                response = requests.get(readme_url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                readme_text = response.text
                import re

                img_pattern = r'!\[(.*?)\]\((.*?)\)'
                matches = re.findall(img_pattern, readme_text)

                badge_keywords = ['badge', 'shield', 'svg', 'logo', 'icon', 'star', 'fork', 'license', 'build', 'coverage', 'version']
                good_keywords = ['demo', 'screenshot', 'preview', 'architecture', 'diagram', 'example', 'workflow']

                for alt_text, img_url in matches:
                    alt_lower = alt_text.lower()
                    url_lower = img_url.lower()

                    if any(kw in url_lower or kw in alt_lower for kw in badge_keywords):
                        continue

                    if any(kw in url_lower or kw in alt_lower for kw in good_keywords):
                        full_url = self._resolve_image_url(img_url, owner, repo)
                        img_path = self.download_image(full_url, f"{owner}_{repo}")
                        if img_path and self._is_valid_image_size(img_path):
                            logger.info(f"Using high-quality README image: {alt_text}")
                            return img_path

                for alt_text, img_url in matches:
                    alt_lower = alt_text.lower()
                    url_lower = img_url.lower()

                    if any(kw in url_lower or kw in alt_lower for kw in badge_keywords):
                        continue

                    full_url = self._resolve_image_url(img_url, owner, repo)
                    img_path = self.download_image(full_url, f"{owner}_{repo}")
                    if img_path and self._is_valid_image_size(img_path):
                        logger.info(f"Using README image: {alt_text}")
                        return img_path

        except Exception as e:
            logger.warning(f"Failed to fetch GitHub image {repo_url}: {e}")

        return None

    def _resolve_image_url(self, img_url, owner, repo):
        """Resolve image URL (handle relative paths)"""
        if img_url.startswith('http'):
            return img_url
        elif img_url.startswith('/'):
            return f"https://raw.githubusercontent.com/{owner}/{repo}/main{img_url}"
        else:
            return f"https://raw.githubusercontent.com/{owner}/{repo}/main/{img_url}"

    def _is_valid_image_size(self, img_path, min_size_kb=5):
        """Check if image size is appropriate (filter out too small icons)"""
        try:
            file_size = Path(img_path).stat().st_size / 1024
            return file_size >= min_size_kb
        except:
            return True

    def fetch_arxiv_image(self, arxiv_url):
        """Fetch image from arXiv paper (use default academic image)"""
        try:
            import re
            match = re.search(r'arxiv.org/abs/(\d+\.\d+)', arxiv_url)
            if match:
                arxiv_id = match.group(1)
                preview_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                return self.get_default_academic_image()
        except Exception as e:
            logger.warning(f"Failed to fetch arXiv image {arxiv_url}: {e}")

        return self.get_default_academic_image()

    def fetch_generic_image(self, url):
        """Fetch generic image for non-GitHub/arXiv sources"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    img_url = og_image['content']
                    img_path = self.download_image(img_url, f"generic_{hash(url)}")
                    if img_path:
                        return img_path

                first_img = soup.find('img', src=True)
                if first_img:
                    img_url = first_img['src']
                    if not img_url.startswith('http'):
                        from urllib.parse import urljoin
                        img_url = urljoin(url, img_url)
                    img_path = self.download_image(img_url, f"generic_{hash(url)}")
                    if img_path:
                        return img_path

        except Exception as e:
            logger.warning(f"Failed to fetch generic image {url}: {e}")

        return self.get_default_tech_image()

    def get_default_academic_image(self):
        """Get default academic image"""
        default_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/ArXiv_logo_2022.svg/1200px-ArXiv_logo_2022.svg.png"
        img_path = self.download_image(default_url, "default_arxiv")
        if img_path:
            return img_path
        return None

    def get_default_tech_image(self):
        """Get default tech image"""
        default_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Octicons-mark-github.svg/1200px-Octicons-mark-github.svg.png"
        img_path = self.download_image(default_url, "default_tech")
        if img_path:
            return img_path
        return None

    def download_image(self, url, name):
        """Download image to local storage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    return None

                ext = '.png'
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'

                safe_name = "".join(c for c in name if c.isalnum() or c in ('_', '-'))
                img_path = self.images_dir / f"{safe_name}{ext}"

                with open(img_path, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Image downloaded successfully: {img_path}")
                return str(img_path)

        except Exception as e:
            logger.warning(f"Failed to download image {url}: {e}")

        return None

    def fetch_arxiv_abstract(self, arxiv_url):
        """Fetch abstract from arXiv paper"""
        try:
            response = requests.get(arxiv_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                abstract = soup.find('blockquote', class_='abstract')
                if abstract:
                    return abstract.get_text().replace('Abstract:', '').strip()[:1000]

        except Exception as e:
            logger.warning(f"Failed to fetch arXiv abstract {arxiv_url}: {e}")

        return None

    def enrich_news_item(self, item):
        """Enrich news item with detailed information and images"""
        url = item.get('url', '')
        source = item.get('source', '')

        detail = None
        image = None

        if 'github.com' in url:
            detail = self.fetch_github_readme(url)
            image = self.fetch_github_image(url)
        elif 'arxiv.org' in url:
            detail = self.fetch_arxiv_abstract(url)
            image = self.fetch_arxiv_image(url)
        else:
            image = self.fetch_generic_image(url)

        if detail:
            item['detail'] = detail
            logger.info(f"Successfully fetched details: {item['title'][:30]}...")

        if image:
            item['image'] = image
            logger.info(f"Successfully fetched image: {item['title'][:30]}...")
        else:
            default_img = self.get_default_tech_image()
            if default_img:
                item['image'] = default_img
                logger.info(f"Using default image: {item['title'][:30]}...")

        return item
