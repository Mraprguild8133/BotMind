import os
import logging
from telegram.ext import Application

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.application = None
        
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
            return
            
        self.application = Application.builder().token(self.token).build()
        logger.info("Telegram bot initialized successfully")
    
    def is_available(self):
        """Check if bot is properly configured"""
        return self.application is not None
    
    async def get_bot_info(self):
        """Get bot information"""
        if not self.application:
            return None
            
        try:
            bot_info = await self.application.bot.get_me()
            return {
                "id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "is_bot": bot_info.is_bot
            }
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None
