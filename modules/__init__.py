"""
Modules package
"""

from .news_collector import NewsCollector
from .content_automation import ContentAutomation
from .image_generator import ImageGenerator, generate_cover_image

__all__ = [
    'NewsCollector',
    'ContentAutomation',
    'ImageGenerator',
    'generate_cover_image',
]
