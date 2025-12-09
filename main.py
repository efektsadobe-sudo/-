import os
import telebot
from datetime import datetime, timedelta
import time
import pytz
from collections import deque

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

MOSCOW = pytz.timezone("Europe/Moscow")
history = deque(maxlen=10)

# Список активных таймеров: (время появления, босс)
timers = []

kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
kb.add("Астарот умер сейчас", "Лилит умерла сейчас")
kb.add("Астарот — вручную", "Лилит — вручную")
kb.add("История записей")

def add_to_history(boss, death, appear):
    history.append(f"{death} → {appear} {boss}")

def send(msg):
    bot.send_message(CHAT_ID, msg, parse_mode="HTML")

def schedule_boss(boss_name, hours, minutes, death_dt):
    appear = death_dt + timedelta(hours=hours, minutes=minutes)
    timers.append((appear, boss_name, death_dt))
    add_to_history(boss_name, death_dt.strftime('%H:%M:%S'), appear.strftime('%H:%M:%S'))
    return death_dt.strftime('%H:%M:%S'), appear.strftime('%H:%M:%S')

# === ФОНОВАЯ ПРОВЕРКА ТАЙМЕРОВ (никогда не умирает) ===
def timer_loop():
    while True:
        now = datetime.now(MOSCOW)
        for appear, boss, death in timers[:]:
            if now >= appear - timedelta(minutes=2) and now < appear - timedelta(minutes=1, seconds=50):
                send(f"<b>{boss}</b> через 2 минуты!\n≈ {appear.strftime('%H:%M:%S')} МСК")
                timers.remove((appear, boss, death))
            elif now >= appear:
                send(f"<b>{boss} ПОЯВИЛСЯ!</b>\n{appear.strftime('%H:%M:%S')} МСК")
                timers.remove((appear, boss, death))
        time.sleep(5)  # проверяем каждые 5 сек

import threading
threading.Thread(target=timer_loop, daemon=True).start()

# === Остальной код без изменений ===
@bot.message_handler(commands=['start', 'help'])
def start(m):
    bot.send_message(m.chat.id, "<b>Астарот 4:08 ⋆ Лилит 3:58</b>\nМСК · до секунд · 24/7", parse_mode="HTML", reply_markup=kb)

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
        bot.reply_to(m, "Время смерти Астарота")
        bot.register_next_step_handler(m, lambda x: parse_time(x, "АСТАРОТ", 4, 8))

    elif txt == "Лилит — вручную":
        bot.reply_to(m, "Время смерти Лилит")
        bot.register_next_step_handler(m, lambda x: parse_time(x, "ЛИЛИТ", 3, 58))

    elif txt == "История записей":
        text = "<b>Последние респы:</b>\n" + ("\n".join(history) if history else "пусто")
        bot.reply_to(m, text, parse_mode="HTML", reply_markup=kb)

def parse_time(m, boss_name, h, mnt):
    try:
        cleaned = ''.join(c for c in m.text if c.isdigit() or c == ':')
        parts = [int(x) for x in cleaned.split(':') if x]
        hour, minute = parts[0], parts[1]
        second = parts[2] if len(parts) == 3 else 0
        death = datetime.now(MOSCOW).replace(hour=hour, minute=minute, second=second, microsecond=0)
        death_str, appear_str = schedule_boss(boss_name, h, mnt, death)
        bot.send_message(m.chat.id, f"{boss_name} записан на {death_str}\nПоявится в {appear_str} МСК", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "Неправильно! Пример: 22:58 или 22:58:00", reply_markup=kb)

bot.infinity_polling()
