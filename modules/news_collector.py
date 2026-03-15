"""
News collection module - Collect latest tech news from multiple sources
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.logger import setup_logger
import json
from pathlib import Path

logger = setup_logger()


class NewsCollector:
    def __init__(self):
        self.sources = {
            'github_trending': 'https://github.com/trending',
            'hacker_news': 'https://news.ycombinator.com/',
            'reddit_ai': 'https://www.reddit.com/r/artificial/hot.json',
        }
        self.keywords = ['agent', 'ai agent', 'autonomous agent', 'llm agent', 'multi-agent']

    def search_github_trending(self):
        """Search GitHub trending projects"""
        articles = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(f"{self.sources['github_trending']}/python", headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            repos = soup.find_all('article', class_='Box-row')[:10]
            for repo in repos:
                try:
                    title_elem = repo.find('h2')
                    if not title_elem:
                        continue

                    repo_name = title_elem.get_text().strip().replace('\n', '').replace(' ', '')
                    desc_elem = repo.find('p', class_='col-9')
                    description = desc_elem.get_text().strip() if desc_elem else ''

                    text = (repo_name + ' ' + description).lower()
                    if any(kw in text for kw in self.keywords):
                        articles.append({
                            'title': repo_name,
                            'description': description,
                            'url': f"https://github.com/{repo_name}",
                            'source': 'GitHub Trending',
                            'date': datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.error(f"Failed to parse GitHub project: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to fetch GitHub trending: {e}")

        return articles

    def search_arxiv(self):
        """Search arXiv papers"""
        articles = []
        try:
            base_url = "http://export.arxiv.org/api/query"
            query = "search_query=all:agent+AND+all:llm&sortBy=submittedDate&sortOrder=descending&max_results=10"
            response = requests.get(f"{base_url}?{query}", timeout=10)

            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.content)

            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                link = entry.find('{http://www.w3.org/2005/Atom}id').text
                published = entry.find('{http://www.w3.org/2005/Atom}published').text

                articles.append({
                    'title': title,
                    'description': summary[:300] + '...',
                    'url': link,
                    'source': 'arXiv',
                    'date': published
                })

        except Exception as e:
            logger.error(f"Failed to fetch arXiv papers: {e}")

        return articles

    def search_reddit(self):
        """Search Reddit AI discussions"""
        articles = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.sources['reddit_ai'], headers=headers, timeout=10)

            if response.status_code != 200:
                logger.warning(f"Reddit returned status code: {response.status_code}")
                return articles

            content_type = response.headers.get('Content-Type', '')
            if 'json' not in content_type:
                logger.warning(f"Reddit returned non-JSON format: {content_type}")
                return articles

            data = response.json()

            for post in data['data']['children'][:10]:
                post_data = post['data']
                text = (post_data['title'] + ' ' + post_data.get('selftext', '')).lower()

                if any(kw in text for kw in self.keywords):
                    articles.append({
                        'title': post_data['title'],
                        'description': post_data.get('selftext', '')[:300],
                        'url': f"https://reddit.com{post_data['permalink']}",
                        'source': 'Reddit r/artificial',
                        'date': datetime.fromtimestamp(post_data['created_utc']).isoformat()
                    })

        except requests.exceptions.RequestException as e:
            logger.warning(f"Reddit network request failed: {e}")
        except ValueError as e:
            logger.warning(f"Reddit response parsing failed: {e}")
        except Exception as e:
            logger.warning(f"Failed to fetch Reddit content: {e}")

        return articles

    def search_google_news(self, query="AI Agent"):
        """Search Google News (using RSS)"""
        articles = []
        try:
            url = f"https://news.google.com/rss/search?q={query}+when:7d&hl=en-US&gl=US&ceid=US:en"
            response = requests.get(url, timeout=10)

            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.content)

            for item in root.findall('.//item')[:10]:
                title = item.find('title').text
                link = item.find('link').text
                pub_date = item.find('pubDate').text
                description = item.find('description').text if item.find('description') is not None else ''

                articles.append({
                    'title': title,
                    'description': description[:300],
                    'url': link,
                    'source': 'Google News',
                    'date': pub_date
                })

        except Exception as e:
            logger.error(f"Failed to fetch Google News: {e}")

        return articles

    def collect_all_news(self):
        """Collect news from all sources"""
        logger.info("Starting to collect tech news...")

        all_articles = []

        github_articles = self.search_github_trending()
        all_articles.extend(github_articles)
        logger.info(f"GitHub: {len(github_articles)} articles")

        arxiv_articles = self.search_arxiv()
        all_articles.extend(arxiv_articles)
        logger.info(f"arXiv: {len(arxiv_articles)} articles")

        reddit_articles = self.search_reddit()
        if reddit_articles:
            all_articles.extend(reddit_articles)
            logger.info(f"Reddit: {len(reddit_articles)} articles")

        news_articles = self.search_google_news("AI Agent")
        all_articles.extend(news_articles)
        logger.info(f"Google News: {len(news_articles)} articles")

        logger.info(f"Total collected: {len(all_articles)} articles")

        news_dir = Path("data/news")
        news_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = news_dir / f"news_{timestamp}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)

        logger.info(f"News saved to: {file_path}")
        return all_articles
