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
    history.append(death_dt.strftime('%H:%M:%S') + f" — {boss} умер → {appear_dt.strftime('%H:%M:%S')}")

def send(msg):
    bot.send_message(CHAT_ID, msg, parse_mode="HTML")

def schedule_boss(boss_name, hours, minutes, death_dt):
    appear = death_dt + timedelta(hours=hours, minutes=minutes)
    warn = appear - timedelta(minutes=2)

    add_to_history(boss_name, death_dt, appear)

    # за 2 минуты
    dw = (warn - datetime.now(MOSCOW)).total_seconds()
    if dw > 0:
        threading.Timer(dw, send, args=[f"<b>{boss_name}</b> через 2 минуты!\n"
                                       f"Появится в {appear.strftime('%H:%M:%S')} (МСК)"]).start()

    # точный респ
    df = (appear - datetime.now(MOSCOW)).total_seconds()
    threading.Timer(df, send, args=[f"<b>{boss_name} ПОЯВИЛСЯ!</b>\n"
                                   f"Время: {appear.strftime('%H:%M:%S')} (МСК)"]).start()

    death_str = death_dt.strftime('%H:%M:%S')
    appear_str = appear.strftime('%H:%M:%S')
    return death_str, appear_str

@bot.message_handler(commands=['start', 'help'])
def start(m):
    bot.send_message(m.chat.id,
        "<b>Астарот 4:08 ⋆ Лилит 3:58</b>\n"
        "Время до секунд, строго МСК\n"
        "Оповещение за 2 мин + точный респ\n"
        "Кнопки всегда внизу ↓",
        parse_mode="HTML", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle(m):
    txt = m.text.strip()
    now = datetime.now(MOSCOW)

    if txt == "Астарот умер сейчас":
        death, appear = schedule_boss("АСТАРОТ", 4, 8, now)
        bot.reply_to(m, f"Астарот записан на {death} (МСК)\nПоявится в {appear} (МСК)", reply_markup=kb)

    elif txt == "Лилит умерла сейчас":
        death, appear = schedule_boss("ЛИЛИТ", 3, 58, now)
        bot.reply_to(m, f"Лилит записана на {death} (МСК)\nПоявится в {appear} (МСК)", reply_markup=kb)

    elif txt == "Астарот — вручную":
        bot.reply_to(m, "Время смерти Астарота\nПримеры: 14:30 · 22:58:00")
        bot.register_next_step_handler(m, ast_manual)

    elif txt == "Лилит — вручную":
        bot.reply_to(m, "Время смерти Лилит\nПримеры: 03:15 · 22:58:00")
        bot.register_next_step_handler(m, lil_manual)

    elif txt == "История записей":
        text = "Последние смерти (МСК):\n" + ("\n".join(history) if history else "пусто")
        bot.reply_to(m, text, reply_markup=kb)

def parse_time(m, boss_name, h, mnt):
    try:
        cleaned = re.sub(r"[^\d:]", "", m.text.strip())
        parts = [int(x) for x in cleaned.split(":") if x]
        hour = parts[0]
        minute = parts[1]
        second = parts[2] if len(parts) >= 3 else 0

        death = datetime.now(MOSCOW).replace(hour=hour, minute=minute, second=second, microsecond=0)
        death_str, appear_str = schedule_boss(boss_name, h, mnt, death)
        bot.send_message(m.chat.id, f"{boss_name} записан на {death_str} (МСК)\nПоявится в {appear_str} (МСК)", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "Ошибка!\nПримеры: 22:58 или 22:58:00", reply_markup=kb)

def ast_manual(m): parse_time(m, "АСТАРОТ", 4, 8)
def lil_manual(m): parse_time(m, "ЛИЛИТ", 3, 58)

bot.infinity_polling()
