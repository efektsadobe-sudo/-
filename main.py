import os
import telebot
from datetime import datetime, timedelta
import threading
from collections import deque
import pytz

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

history = deque(maxlen=10)
MOSCOW = pytz.timezone("Europe/Moscow")

# вечная клавиатура
kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
kb.add("Астарот умер сейчас", "Лилит умерла сейчас")
kb.add("Астарот — вручную", "Лилит — вручную")
kb.add("История записей")

def add_to_history(boss, death_dt):
    history.append(death_dt.strftime('%H:%M:%S') + f" — {boss} умер")

def send(msg):
    bot.send_message(CHAT_ID, msg, parse_mode="HTML")

def schedule_boss(boss_name, hours, minutes, death_dt):
    appear = death_dt + timedelta(hours=hours, minutes=minutes)
    warn = appear - timedelta(minutes=2)
    add_to_history(boss_name, death_dt)

    dw = (warn - datetime.now(MOSCOW)).total_seconds()
    df = (appear - datetime.now(MOSCOW)).total_seconds()

    if dw > 0:
        threading.Timer(dw, send, args=[f" <b>{boss_name}</b> через 2 минуты!\n≈ {appear.strftime('%H:%M:%S')} (МСК)"]).start()
    threading.Timer(df, send, args=[f"<b>{boss_name} ПОЯВИЛСЯ!</b>\n{appear.strftime('%H:%M:%S')} (МСК)"]).start()

    return death_dt.strftime('%H:%M:%S')

@bot.message_handler(commands=['start', 'help'])
def start(m):
    bot.send_message(m.chat.id,
        "<b>Астарот 4:08 ⋆ Лилит 3:58</b>\nВремя до секунд, строго МСК\nКнопки всегда внизу ↓",
        parse_mode="HTML", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle(m):
    txt = m.text.strip()
    now = datetime.now(MOSCOW)

    if txt == "Астарот умер сейчас":
        death = schedule_boss("АСТАРОТ", 4, 8, now)
        bot.reply_to(m, f"Астарот записан на {death} (МСК) + 4ч 8мин", reply_markup=kb)

    elif txt == "Лилит умерла сейчас":
        death = schedule_boss("ЛИЛИТ", 3, 58, now)
        bot.reply_to(m, f"Лилит записана на {death} (МСК) + 3ч 58мин", reply_markup=kb)

    elif txt == "Астарот — вручную":
        bot.reply_to(m, "Время смерти Астарота\nФормат: 14:30 или 14:30:45")
        bot.register_next_step_handler(m, ast_manual)

    elif txt == "Лилит — вручную":
        bot.reply_to(m, "Время смерти Лилит\nФормат: 03:15 или 03:15:27")
        bot.register_next_step_handler(m, lil_manual)

    elif txt == "История записей":
        text = "Последние смерти (МСК):\n" + ("\n".join(history) if history else "пусто")
        bot.reply_to(m, text, reply_markup=kb)

# Универсальная функция для обоих боссов
def parse_and_schedule(m, boss_name, hours, minutes):
    try:
        parts = [int(x) for x in m.text.strip().split(':')]
        h = parts[0]
        mn = parts[1]
        sec = parts[2] if len(parts) == 3 else 0

        death = datetime.now(MOSCOW).replace(hour=h, minute=mn, second=sec, microsecond=0)
        schedule_boss(boss_name, hours, minutes, death)
        bot.send_message(m.chat.id, f"{boss_name} записан на {death.strftime('%H:%M:%S')} (МСК) + {hours}ч {minutes}мин", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "Неправильно! Пример: 22:55 или 22:55:00", reply_markup=kb)

def ast_manual(m):
    parse_and_schedule(m, "АСТАРОТ", 4, 8)

def lil_manual(m):
    parse_and_schedule(m, "ЛИЛИТ", 3, 58)

bot.infinity_polling()
