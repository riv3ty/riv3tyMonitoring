import asyncio
from telegram import Bot
from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

class TelegramNotifier:
    def __init__(self):
        self.bot = Bot(TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID
        self.machine_status = {}  # Keep track of machine status
        self.alert_threshold = 80  # Percentage threshold for resource alerts
        self.alert_cooldown = {}  # Cooldown for resource alerts

    async def send_message(self, message):
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

    def check_resource_threshold(self, hostname, metrics, timestamp):
        # Get current time for cooldown check
        current_time = datetime.now()
        
        # Initialize cooldown for this host if not exists
        if hostname not in self.alert_cooldown:
            self.alert_cooldown[hostname] = {
                'ram': None,
                'cpu': None,
                'disk': None
            }
        
        alerts = []
        
        # Check RAM usage
        ram_percent = metrics.get('ram', {}).get('percent', 0)
        if ram_percent > self.alert_threshold:
            last_alert = self.alert_cooldown[hostname]['ram']
            if not last_alert or (current_time - last_alert).total_seconds() > 300:  # 5 minutes cooldown
                alerts.append(f"🔴 RAM usage critical: {ram_percent}%")
                self.alert_cooldown[hostname]['ram'] = current_time
        
        # Check CPU usage
        cpu_percent = metrics.get('cpu', {}).get('usage', 0)
        if cpu_percent > self.alert_threshold:
            last_alert = self.alert_cooldown[hostname]['cpu']
            if not last_alert or (current_time - last_alert).total_seconds() > 300:  # 5 minutes cooldown
                alerts.append(f"🔴 CPU usage critical: {cpu_percent}%")
                self.alert_cooldown[hostname]['cpu'] = current_time
        
        # Check Disk usage
        disk_percent = metrics.get('disk_usage', {}).get('percent', 0)
        if disk_percent > self.alert_threshold:
            last_alert = self.alert_cooldown[hostname]['disk']
            if not last_alert or (current_time - last_alert).total_seconds() > 3600:  # 1 hour cooldown
                alerts.append(f"🔴 Disk usage critical: {disk_percent}%")
                self.alert_cooldown[hostname]['disk'] = current_time
        
        # Send combined alert if any thresholds exceeded
        if alerts:
            message = f"⚠️ Resource Alert for {hostname}\n"
            message += "\n".join(alerts)
            message += f"\nTime: {timestamp}"
            asyncio.run(self.send_message(message))
    
    def notify_status_change(self, hostname, status, timestamp, metrics=None):
        previous_status = self.machine_status.get(hostname, {}).get('online', True)
        current_status = status.get('online', True)
        
        # Update stored status
        self.machine_status[hostname] = status
        
        # If machine goes offline
        if previous_status and not current_status:
            message = f"⚠️ ALERT: {hostname} went OFFLINE!\n"
            message += f"Time: {timestamp}"
            asyncio.run(self.send_message(message))
        
        # If machine comes back online
        elif not previous_status and current_status:
            message = f"✅ RECOVERED: {hostname} is back ONLINE!\n"
            message += f"Time: {timestamp}"
            asyncio.run(self.send_message(message))
        
        # Check resource usage if metrics provided and system is online
        if metrics and current_status:
            self.check_resource_threshold(hostname, metrics, timestamp)
