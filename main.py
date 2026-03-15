#!/usr/bin/env python3
"""
Auto Upload to RedNote - Main entry point
Automatically collect tech news, generate content, and publish to RedNote
"""
import schedule
import time
import yaml
from pathlib import Path
from dotenv import load_dotenv

from modules.content_automation import ContentAutomation
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger()


class AutoUploadSystem:
    def __init__(self, config_path="config.yaml"):
        if not Path(config_path).exists():
            logger.error(f"Config file not found: {config_path}")
            logger.info("Please copy config.yaml.example to config.yaml and configure it")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.modules = {}
        self._init_modules()

    def _init_modules(self):
        """Initialize modules"""
        if self.config.get('content_automation', {}).get('enabled'):
            self.modules['content'] = ContentAutomation(self.config['content_automation'])

    def run_content_automation(self):
        """Run content automation"""
        logger.info("Starting content automation task")
        try:
            result = self.modules['content'].generate_and_save()
            if result:
                logger.info(f"Content generated: {result['title']}")
            else:
                logger.warning("Failed to generate content")
        except Exception as e:
            logger.error(f"Content automation error: {e}")

    def schedule_tasks(self):
        """Schedule all tasks"""
        schedule.every().day.at("09:00").do(self.run_content_automation)
        logger.info("Task scheduling configured")

    def run(self):
        """Start the system"""
        logger.info("Auto Upload System started")
        self.schedule_tasks()

        logger.info("System running. Press Ctrl+C to stop.")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                logger.info("System stopped by user")
                break
            except Exception as e:
                logger.error(f"System error: {e}")
                time.sleep(60)


if __name__ == "__main__":
    try:
        system = AutoUploadSystem()
        system.run()
    except Exception as e:
        logger.error(f"Failed to start system: {e}")
        exit(1)
