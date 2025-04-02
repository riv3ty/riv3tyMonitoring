import asyncio
from telegram import Bot
from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def test_telegram():
    try:
        print(f"Using Bot Token: {TELEGRAM_BOT_TOKEN}")
        print(f"Using Chat ID: {TELEGRAM_CHAT_ID}")
        
        bot = Bot(TELEGRAM_BOT_TOKEN)
        
        # Test connection
        print("\nTesting bot connection...")
        me = await bot.get_me()
        print(f"Bot info: {me.first_name} (@{me.username})")
        
        # Send test message
        print("\nSending test message...")
        message = "🔧 Test message from Riv3ty Monitoring"
        sent = await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print(f"Message sent successfully: {sent.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if "Unauthorized" in str(e):
            print("\nPossible solutions:")
            print("1. Check if your bot token is correct")
            print("2. Create a new bot with @BotFather and get a new token")
        elif "Chat not found" in str(e):
            print("\nPossible solutions:")
            print("1. Make sure you've started a chat with the bot")
            print("2. Check if your chat ID is correct")
            print("3. Send a message to @userinfobot to get your correct chat ID")

async def main():
    print("Starting Telegram test...")
    await test_telegram()

if __name__ == "__main__":
    asyncio.run(main())
