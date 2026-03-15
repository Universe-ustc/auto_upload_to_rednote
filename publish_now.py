#!/usr/bin/env python3
"""
Publish article immediately
"""
import yaml
from pathlib import Path
from dotenv import load_dotenv
from modules.content_automation import ContentAutomation
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger()


def main():
    """Generate and publish article immediately"""
    try:
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        content_automation = ContentAutomation(config['content_automation'])

        logger.info("Generating content...")
        result = content_automation.generate_and_save(use_real_news=True)

        if result:
            logger.info(f"Content generated successfully")
            logger.info(f"Title: {result['title']}")
            logger.info(f"File: {result['file_path']}")
            logger.info("Article saved for review")
        else:
            logger.error("Failed to generate content")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
