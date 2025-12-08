import os
import telebot
from datetime import datetime, timedelta
import threading
from collections import deque
import pytz
import re

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

history = deque(maxlen=10)
MOSCOW = pytz.timezone("Europe/Moscow")

kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
kb.add("Астарот умер сейчас", "Лилит умерла сейчас")
kb.add("Астарот — вручную", "Лилит — вручную")
kb.add("История записей")

def add_to_history(boss, death_dt, appear_dt):
    history.append(f"{death_dt.strftime('%H:%M:%S')} → {appear_dt.strftime('%H:%M:%S')} {boss}")

def send(msg):
    bot.send_message(CHAT_ID, msg, parse_mode="HTML")

def schedule_boss(boss_name, hours, minutes, death_dt):
    appear = death_dt + timedelta(hours=hours, minutes=minutes)
    warn = appear - timedelta(minutes=2)
    add_to_history(boss_name, death_dt, appear)

    dw = (warn - datetime.now(MOSCOW)).total_seconds()
    df = (appear - datetime.now(MOSCOW)).total_seconds()

    if dw > 0:
        threading.Timer(dw, send, args=[f"<b>{boss_name}</b> через 2 минуты!\n≈ {appear.strftime('%H:%M:%S')} МСК"]).start()
    threading.Timer(df, send, args=[f"<b>{boss_name} ПОЯВИЛСЯ!</b>\n{appear.strftime('%H:%M:%S')} МСК"]).start()

    return death_dt.strftime('%H:%M:%S'), appear.strftime('%H:%M:%S')

@bot.message_handler(commands=['start', 'help'])
def start(m):
    bot.send_message(m.chat.id,
        "<b>Астарот 4:08 ⋆ Лилит 3:58</b>\nМСК · до секунд · 24/7",
        parse_mode="HTML", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle(m):
    txt = m.text.strip()
    now = datetime.now(MOSCOW)

    if txt == "Астарот умер сейчас":
        death, appear = schedule_boss("АСТАРОТ", 4, 8, now)
        bot.reply_to(m, f"АСТАРОТ записан на {death}\nПоявится в {appear} МСК", reply_markup=kb)

    elif txt == "Лилит умерла сейчас":
        death, appear = schedule_boss("ЛИЛИТ", 3, 58, now)
        bot.reply_to(m, f"ЛИЛИТ записана на {death}\nПоявится в {appear} МСК", reply_markup=kb)

    elif txt == "Астарот — вручную":
        bot.reply_to(m, "Время смерти Астарота (14:30 или 22:58:00)")
        bot.register_next_step_handler(m, ast_manual)

    elif txt == "Лилит — вручную":
        bot.reply_to(m, "Время смерти Лилит (03:15 или 22:58:00)")
        bot.register_next_step_handler(m, lil_manual)

    elif txt == "История записей":
        if history:
            bot.reply_to(m, "<b>Последние респы:</b>\n" + "\n".join(history), parse_mode="HTML", reply_markup=kb)
        else:
            bot.reply_to(m, "История пуста", reply_markup=kb)

def parse_time(m, boss_name, h, mnt):
    try:
        cleaned = re.sub(r"[^\d:]", "", m.text.strip())
        parts = [int(x) for x in cleaned.split(":") if x]
        hour = parts[0]
        minute = parts[1]
        second = parts[2] if len(parts) >= 3 else 0

        death = datetime.now(MOSCOW).replace(hour=hour, minute=minute, second=second, microsecond=0)
        death_str, appear_str = schedule_boss(boss_name, h, mnt, death)
        bot.send_message(m.chat.id, f"{boss_name} записан на {death_str}\nПоявится в {appear_str} МСК", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "Неправильно! Введи: 22:58 или 22:58:00", reply_markup=kb)

def ast_manual(m): parse_time(m, "АСТАРОТ", 4, 8)
def lil_manual(m): parse_time(m, "ЛИЛИТ", 3, 58)

bot.infinity_polling()
