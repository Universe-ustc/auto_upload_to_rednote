#!/usr/bin/env python3
"""
Review and manage pending articles
"""
import yaml
import json
from pathlib import Path
from dotenv import load_dotenv
from modules.content_automation import ContentAutomation
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger()


def display_article(article):
    """Display article details"""
    print("\n" + "="*80)
    print(f"Title: {article['title']}")
    print(f"Topic: {article['topic']}")
    print(f"Status: {article['status']}")
    print(f"Created: {article.get('timestamp', 'N/A')}")
    print("-"*80)
    print(f"Content:\n{article['content'][:500]}...")
    print("="*80)


def main():
    """Review pending articles"""
    try:
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        content_automation = ContentAutomation(config['content_automation'])

        pending_articles = content_automation.get_pending_articles()

        if not pending_articles:
            logger.info("No pending articles")
            return

        logger.info(f"Found {len(pending_articles)} pending articles")

        for i, article in enumerate(pending_articles, 1):
            display_article(article)

            while True:
                choice = input("\nAction (a=approve, r=reject, s=skip, q=quit): ").lower()

                if choice == 'a':
                    content_automation.approve_article(article['file_path'])
                    logger.info("Article approved")
                    break
                elif choice == 'r':
                    reason = input("Rejection reason: ")
                    content_automation.reject_article(article['file_path'], reason)
                    logger.info("Article rejected")
                    break
                elif choice == 's':
                    logger.info("Skipped")
                    break
                elif choice == 'q':
                    return
                else:
                    print("Invalid choice")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
