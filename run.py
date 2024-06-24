# run.py
import os
from threading import Thread
from dotenv import load_dotenv
from dashboard import create_app
from bot import bot

# Load environment variables
load_dotenv()

# Retrieve necessary info from .env
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SECRET_KEY = os.getenv('SECRET_KEY')

def run_flask():
    app = create_app(SECRET_KEY)
    app.run(debug=True, use_reloader=False)

def run_discord_bot():
    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    discord_thread = Thread(target=run_discord_bot)

    flask_thread.start()
    discord_thread.start()

    flask_thread.join()
    discord_thread.join()
