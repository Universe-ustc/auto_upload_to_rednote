"""
Content automation module - Auto-generate and publish content
"""
import os
from openai import OpenAI
from utils.logger import setup_logger
import json
from pathlib import Path

logger = setup_logger()


class ContentAutomation:
    def __init__(self, config):
        self.config = config
        self.api_key = os.getenv('SILICONFLOW_API_KEY', '[YOUR_SILICONFLOW_API_KEY]')
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.siliconflow.cn/v1"
        )
        self.platforms = config['platforms']
        self.topics = config['topics']
        self.pending_dir = Path("data/pending_articles")
        self.pending_dir.mkdir(parents=True, exist_ok=True)

        self.archive_dir = Path("data/published_articles")
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def generate_article_from_news(self, news_items):
        """Generate article based on real news"""
        from modules.project_detail_fetcher import ProjectDetailFetcher
        fetcher = ProjectDetailFetcher()

        logger.info("Fetching project details...")
        enriched_items = []
        for item in news_items[:3]:
            enriched_item = fetcher.enrich_news_item(item)
            enriched_items.append(enriched_item)

        news_summary = "\n\n".join([
            f"【{item['source']}】{item['title']}\nDescription: {item['description']}\nDetails: {item.get('detail', 'N/A')}\nSource: {item['url']}"
            for item in enriched_items
        ])

        project_count = len(enriched_items)

        prompt = f"""Based on the following latest tech news, write an article suitable for social media platforms:

【Important】There are {project_count} projects/papers below. Numbers in title and opening must match this count!

{news_summary}

Core requirements:
1. Word count: 600-850 words
2. Casual and conversational language, but maintain professionalism
3. Only analyze real information provided, don't fabricate technical details
4. If information is insufficient, say "project is in early stage" or "detailed implementation not yet public"
5. Each project: 3-4 sentences detailed introduction (core features, technical highlights, use cases)
6. Blank lines between paragraphs, max 4 lines per paragraph
7. Strict word count control

Article structure:
🔥 Attractive title (must be diverse, avoid repetition!)
💡 Opening (1 paragraph, create resonance)
🚀 Project details (3-4 sentences per project)
⚡ Summary (1 paragraph, max 2 lines)
📚 References (must include original links!)

Writing style:
- Like chatting with friends, casual but professional
- Use "you", "we" more, avoid formal language
- Appropriate emoji usage, not excessive
- Guide interaction at the end
"""

        try:
            response = self.client.chat.completions.create(
                model="Qwen/Qwen3-8B",
                messages=[
                    {"role": "system", "content": "You are a tech blogger skilled at sharing tech news in an easy-to-understand way. Your articles are suitable for social media platforms with conversational language but maintain professionalism. You only analyze provided information without fabricating details."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3500
            )
            return response.choices[0].message.content, news_items
        except Exception as e:
            logger.error(f"Failed to generate article: {e}")
            return None, None

    def generate_article(self, topic):
        """Generate article using AI (backup method)"""
        prompt = f"""Write a high-quality article about "{topic}", requirements:
1. Word count: 800-1200 words
2. Suitable for social media platforms
3. Clear structure with subheadings
4. Strong practical value with concrete examples
5. Suitable for English readers
6. Valuable content that helps readers solve real problems"""

        try:
            response = self.client.chat.completions.create(
                model="Qwen/Qwen3-8B",
                messages=[
                    {"role": "system", "content": "You are a professional tech content creator skilled at writing clear and understandable technical articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to generate article: {e}")
            return None

    def save_for_review(self, topic, title, content, sources=None):
        """Save article for review"""
        import time
        timestamp = int(time.time())
        article_data = {
            'topic': topic,
            'title': title,
            'content': content,
            'sources': sources or [],
            'timestamp': timestamp,
            'status': 'pending'
        }

        file_path = self.pending_dir / f"article_{timestamp}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Article saved for review: {file_path}")
        return file_path

    def get_pending_articles(self):
        """Get list of pending articles"""
        articles = []
        for file_path in self.pending_dir.glob("article_*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('status') == 'pending':
                    data['file_path'] = str(file_path)
                    articles.append(data)
        return sorted(articles, key=lambda x: x['timestamp'], reverse=True)

    def approve_article(self, file_path):
        """Approve article for publishing"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data['status'] = 'approved'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    def reject_article(self, file_path, reason=""):
        """Reject article"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data['status'] = 'rejected'
        data['reject_reason'] = reason
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Article rejected: {reason}")

    def publish_to_xiaohongshu(self, title, content, images=None):
        """Publish to RedNote"""
        logger.info(f"Publishing to RedNote: {title}")
        from modules.xiaohongshu_playwright_publisher import publish_to_xiaohongshu_playwright
        import os

        phone = os.getenv('XIAOHONGSHU_PHONE', '[YOUR_PHONE_NUMBER]')
        return publish_to_xiaohongshu_playwright(phone, title, content, images)

    def publish_to_zhihu(self, title, content):
        """Publish to Zhihu"""
        logger.info(f"Publishing to Zhihu: {title}")
        return True

    def publish_to_medium(self, title, content):
        """Publish to Medium"""
        logger.info(f"Publishing to Medium: {title}")
        return True

    def publish_to_csdn(self, title, content):
        """Publish to CSDN"""
        logger.info(f"Publishing to CSDN: {title}")
        return True

    def generate_and_save(self, use_real_news=True):
        """Generate content and save for review"""
        import random

        if use_real_news:
            from modules.news_collector import NewsCollector
            collector = NewsCollector()

            logger.info("Collecting latest tech news...")
            news_items = collector.collect_all_news()

            if not news_items:
                logger.warning("No news collected, using backup plan")
                use_real_news = False
            else:
                logger.info(f"Collected {len(news_items)} articles, generating content...")
                article, sources = self.generate_article_from_news(news_items)
                if not article:
                    return None
                lines = article.strip().split('\n')
                title = lines[0].replace('🔥', '').replace('#', '').strip()
                file_path = self.save_for_review("Latest Tech News", title, article, sources)
                return {
                    'topic': "Latest Tech News",
                    'title': title,
                    'content': article,
                    'sources': sources,
                    'file_path': str(file_path)
                }

        topic = random.choice(self.topics)
        logger.info(f"Generating topic: {topic}")
        article = self.generate_article(topic)

        if not article:
            return None

        title = f"{topic} - Complete Guide"
        file_path = self.save_for_review(topic, title, article)
        return {
            'topic': topic,
            'title': title,
            'content': article,
            'file_path': str(file_path)
        }

    def publish_approved_article(self, file_path):
        """Publish approved article"""
        from datetime import datetime
        from modules.image_generator import generate_cover_image

        data = self.approve_article(file_path)
        title = data['title']
        content = data['content']

        logger.info("Generating AI cover image...")
        cover_image = generate_cover_image(self.api_key, title, content)

        images = []
        if cover_image:
            images.append(cover_image)
            logger.info(f"✓ AI cover image generated: {cover_image}")
        else:
            logger.warning("AI cover image generation failed")

        if 'sources' in data and data['sources']:
            for source in data['sources']:
                if 'image' in source and source['image']:
                    images.append(source['image'])

        publish_start_time = datetime.now()

        results = {}
        success_count = 0

        for platform in self.platforms:
            if platform == 'xiaohongshu':
                result = self.publish_to_xiaohongshu(title, content, images)
                results['xiaohongshu'] = result
                if result:
                    success_count += 1
            elif platform == 'zhihu':
                result = self.publish_to_zhihu(title, content)
                results['zhihu'] = result
                if result:
                    success_count += 1
            elif platform == 'medium':
                result = self.publish_to_medium(title, content)
                results['medium'] = result
                if result:
                    success_count += 1
            elif platform == 'csdn':
                result = self.publish_to_csdn(title, content)
                results['csdn'] = result
                if result:
                    success_count += 1

        if success_count > 0:
            self.archive_published_article(data, results, publish_start_time, images)
            logger.info(f"Article published to {success_count}/{len(self.platforms)} platforms")
        else:
            logger.error("All platforms failed to publish")

        return results

    def archive_published_article(self, article_data, publish_results, publish_time, images=None):
        """Archive published article"""
        archive_data = {
            'title': article_data['title'],
            'content': article_data['content'],
            'topic': article_data.get('topic', ''),
            'sources': article_data.get('sources', []),
            'images': images or [],
            'generated_at': article_data.get('timestamp'),
            'published_at': int(publish_time.timestamp()),
            'published_date': publish_time.strftime('%Y-%m-%d %H:%M:%S'),
            'platforms': list(publish_results.keys()),
            'publish_results': publish_results,
            'status': 'published'
        }

        date_str = publish_time.strftime('%Y%m%d')
        timestamp = int(publish_time.timestamp())

        archive_file = self.archive_dir / f"{date_str}_{timestamp}.json"
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)

        md_file = self.archive_dir / f"{date_str}_{timestamp}.md"
        self._save_markdown_archive(md_file, archive_data)

        logger.info(f"Article archived: {archive_file}")

    def _save_markdown_archive(self, file_path, data):
        """Save archive in Markdown format"""
        md_content = f"""# {data['title']}

**Published**: {data['published_date']}
**Topic**: {data['topic']}
**Platforms**: {', '.join(data['platforms'])}

---

## Content

{data['content']}

---

## Images

"""
        if data.get('images'):
            for i, img in enumerate(data['images'], 1):
                md_content += f"{i}. `{img}`\n"
        else:
            md_content += "No images\n"

        md_content += "\n---\n\n## References\n\n"

        if data.get('sources'):
            for i, source in enumerate(data['sources'], 1):
                md_content += f"{i}. [{source.get('title', 'Unknown')}]({source.get('url', '#')})\n"
                md_content += f"   - Source: {source.get('source', 'Unknown')}\n\n"
        else:
            md_content += "No source information\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

    def get_published_articles(self, limit=None):
        """Get list of published articles"""
        articles = []
        for file_path in self.archive_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['file_path'] = str(file_path)
                    articles.append(data)
            except Exception as e:
                logger.warning(f"Failed to read archive {file_path}: {e}")

        articles.sort(key=lambda x: x.get('published_at', 0), reverse=True)

        if limit:
            return articles[:limit]
        return articles

    def get_statistics(self):
        """Get publishing statistics"""
        articles = self.get_published_articles()

        stats = {
            'total_published': len(articles),
            'platforms': {},
            'by_date': {},
            'recent_articles': []
        }

        for article in articles:
            for platform in article.get('platforms', []):
                stats['platforms'][platform] = stats['platforms'].get(platform, 0) + 1

            date = article.get('published_date', '').split(' ')[0]
            if date:
                stats['by_date'][date] = stats['by_date'].get(date, 0) + 1

        stats['recent_articles'] = [
            {
                'title': a['title'],
                'date': a.get('published_date', ''),
                'platforms': a.get('platforms', [])
            }
            for a in articles[:5]
        ]

        return stats
