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
tz = pytz.timezone("Europe/Moscow")

# === ВЕЧНАЯ КЛАВИАТУРА ===
kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
kb.add("Астарот умер сейчас", "Лилит умерла сейчас")
kb.add("Астарот — вручную", "Лилит — вручную")
kb.add("История записей")

def add_to_history(boss):
    history.append(f"{datetime.now(tz).strftime('%H:%M')} — {boss} умер")

def send(msg):
    bot.send_message(CHAT_ID, msg, parse_mode="HTML")

def schedule_boss(boss, hours, minutes, death_time=None):
    if death_time is None:
        death_time = datetime.now(tz)
    appear = death_time + timedelta(hours=hours, minutes=minutes)
    warn = appear - timedelta(minutes=2)
    add_to_history(boss)

    dw = (warn - datetime.now(tz)).total_seconds()
    df = (appear - datetime.now(tz)).total_seconds()
    if dw > 0:
        threading.Timer(dw, send, args=[f"⚠️ <b>{boss}</b> через 2 минуты!\n⏰ ≈ {appear.strftime('%H:%M:%S')}"]).start()
    threading.Timer(df, send, args=[f"АСТАРОТ ПОЯВИЛСЯ!\nВремя: {appear.strftime('%H:%M:%S')}"]).start()

    return death_time.strftime('%H:%M')

@bot.message_handler(commands=['start', 'help'])
def start(m):
    bot.send_message(m.chat.id,
        "<b>Астарот 4:08 ⋆ Лилит 3:58</b>\n"
        "Кнопки всегда внизу ↓\n"
        "▫️ оповещение за 2 минуты + точный пинг",
        parse_mode="HTML", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def all(m):
    txt = m.text.strip()

    if "Астарот умер сейчас" in txt:
        death = schedule_boss("АСТАРОТ", 4, 8)
        bot.reply_to(m, f"Астарот записан на {death} + 4ч 8мин", reply_markup=kb)

    elif "Лилит умерла сейчас" in txt:
        death = schedule_boss("ЛИЛИТ", 3, 58)
        bot.reply_to(m, f"Лилит записана на {death} + 3ч 58мин", reply_markup=kb)

    elif "Астарот — вручную" in txt:
        bot.reply_to(m, "Пришли время смерти Астарота (14:30)")
        bot.register_next_step_handler(m, ast_manual)

    elif "Лилит — вручную" in txt:
        bot.reply_to(m, "Пришли время смерти Лилит (03:15)")
        bot.register_next_step_handler(m, lil_manual)

    elif "История записей" in txt:
        bot.reply_to(m, "Последние смерти:\n" + ("\n".join(history) if history else "пусто"), reply_markup=kb)

def ast_manual(m):
    try:
        h, min_ = map(int, m.text.split(':'))
        death = datetime.now(tz).replace(hour=h, minute=min_, second=0, microsecond=0)
        schedule_boss("АСТАРОТ", 4, 8, death)
        bot.send_message(m.chat.id, f"Астарот записан на {m.text} + 4ч 8мин", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "Неправильно, попробуй ещё (14:30)", reply_markup=kb)

def lil_manual(m):
    try:
        h, min_ = map(int, m.text.split(':'))
        death = datetime.now(tz).replace(hour=h, minute=min_, second=0, microsecond=0)
        schedule_boss("ЛИЛИТ", 3, 58, death)
        bot.send_message(m.chat.id, f"Лилит записана на {m.text} + 3ч 58мин", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "Неправильно, попробуй ещё (03:15)", reply_markup=kb)

bot.infinity_polling()

