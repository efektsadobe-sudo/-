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

def schedule_boss(boss, hours, minutes, death_dt):
    appear = death_dt + timedelta(hours=hours, minutes=minutes)
    warn = appear - timedelta(minutes=2)
    add_to_history(boss, death_dt)

    dw = max(0, (warn - datetime.now(MOSCOW)).total_seconds())
    df = (appear - datetime.now(MOSCOW)).total_seconds()

    if dw > 0:
        threading.Timer(dw, send, args=[f"⚠️ <b>{boss}</b> через 2 минуты!\n"
                                       f"⏰ ≈ {appear.strftime('%H:%M:%S')} (МСК)"]).start()
    threading.Timer(df, send, args=[f"<b>{boss} ПОЯВИЛСЯ!</b>\n"
                                   f"Время: {appear.strftime('%H:%M:%S')} (МСК)"]).start()

    return death_dt.strftime('%H:%M:%S')

@bot.message_handler(commands=['start', 'help'])
def start(m):
    bot.send_message(m.chat.id,
        "<b>Астарот 4:08 ⋆ Лилит 3:58</b>\n"
        "Время до секунд, строго МСК (UTC+3)\n"
        "Кнопки всегда внизу ↓",
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
        bot.reply_to(m, "Пришли время смерти Астарота (14:30:45)")
        bot.register_next_step_handler(m, ast_manual)

    elif txt == "Лилит — вручную":
        bot.reply_to(m, "Пришли время смерти Лилит (03:15:27)")
        bot.register_next_step_handler(m, lil_manual)

    elif txt == "История записей":
        text = "Последние смерти (МСК):\n" + ("\n".join(history) if history else "пусто")
        bot.reply_to(m, text, reply_markup=kb)

def ast_manual(m):
    try:
        h, mn, sec = map(int, m.text.split(':'))
        death = datetime.now(MOSCOW).replace(hour=h, minute=mn, second=sec, microsecond=0)
        schedule_boss("АСТАРОТ", 4, 8, death)
        bot.send_message(m.chat.id, f"Астарот записан на {m.text} (МСК) + 4ч 8мин", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "Формат ЧЧ:ММ:СС → 14:30:45", reply_markup=kb)

def lil_manual(m):
    try:
        h, mn, sec = map(int, m.text.split(':'))
        death = datetime.now(MOSCOW).replace(hour=h, minute=mn, second=sec, microsecond=0)
        schedule_boss("ЛИЛИТ", 3, 58, death)
        bot.send_message(m.chat.id, f"Лилит записана на {m.text} (МСК) + 3ч 58мин", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "Формат ЧЧ:ММ:СС → 03:15:27", reply_markup=kb)

bot.infinity_polling()
