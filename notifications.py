import asyncio
from telegram import Bot
from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

class TelegramNotifier:
    def __init__(self):
        self.bot = Bot(TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID
        self.machine_status = {}  # Keep track of machine status

    async def send_message(self, message):
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

    def notify_status_change(self, hostname, status, timestamp):
        previous_status = self.machine_status.get(hostname, {}).get('online', True)
        current_status = status.get('online', True)
        
        # Update stored status
        self.machine_status[hostname] = status
        
        # If machine goes offline
        if previous_status and not current_status:
            message = f"⚠️ ALERT: {hostname} went OFFLINE!\n"
            message += f"Time: {timestamp}"
            
            # Use asyncio to send the message
            asyncio.run(self.send_message(message))
            
        # If machine comes back online
        elif not previous_status and current_status:
            message = f"✅ RECOVERED: {hostname} is back ONLINE!\n"
            message += f"Time: {timestamp}"
            
            # Use asyncio to send the message
            asyncio.run(self.send_message(message))
