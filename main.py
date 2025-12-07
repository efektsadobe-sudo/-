import os
import telebot
from datetime import datetime, timedelta
import threading

TOKEN = 8584229142:AAFIEO4WeA-nLyq8fATKroyYBBxnoQIVBn0
CHAT_ID = os.getenv("CHAT_ID")  # твой личный чат или группа

bot = telebot.TeleBot(TOKEN)

def schedule_notification(delay_hours, delay_minutes, boss_name):
    delay = timedelta(hours=delay_hours, minutes=delay_minutes)
    target_time = datetime.now() + delay
    
    def notify():
        bot.send_message(CHAT_ID, f"⚔️ {boss_name} ПОЯВИЛСЯ! БЕГИТЕ! ⚔️\nВремя: {datetime.now().strftime('%H:%M:%S')}")
    
    timer = threading.Timer(delay.total_seconds(), notify)
    timer.start()
    return target_time.strftime('%H:%M:%S')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Отправь время смерти босса в формате:\nастарот 14:30\nлилит 02:15")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    try:
        if "астарот" in text:
            time_str = text.split()[-1]
            t = datetime.strptime(time_str, "%H:%M")
            target = schedule_notification(4, 6, "АСТАРОТ")
            bot.reply_to(message, f"Астарот умер в {time_str}\nПоявится в ≈ {target}")
            
        elif "лилит" in text:
            time_str = text.split()[-1]
            t = datetime.strptime(time_str, "%H:%M")
            target = schedule_notification(3, 56, "ЛИЛИТ")
            bot.reply_to(message, f"Лилит умерла в {time_str}\nПоявится в ≈ {target}")
    except:
        bot.reply_to(message, "Пиши нормально: астарот 14:30 или лилит 03:45")

bot.infinity_polling()