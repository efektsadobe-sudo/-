import os
import telebot
from datetime import datetime, timedelta
import threading
from collections import deque
import pytz

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # можно через запятую несколько ID или ID группы

bot = telebot.TeleBot(TOKEN)

# История последних 10 записей
history = deque(maxlen=10)
tz = pytz.timezone("Europe/Kiev")  # меняй на свой пояс, если надо

def add_to_history(boss):
    now = datetime.now(tz).strftime('%H:%M')
    history.append(f"{now} — {boss} умер")

def send_message(text):
    bot.send_message(CHAT_ID, text, parse_mode="HTML")

def schedule_boss(boss, hours, minutes):
    death_time = datetime.now(tz)
    appear_time = death_time + timedelta(hours=hours, minutes=minutes)
    warning_time = appear_time - timedelta(minutes=2)

    add_to_history(boss)

    # оповещение за 2 минуты
    delay_warning = (warning_time - datetime.now(tz)).total_seconds()
    if delay_warning > 0:
        threading.Timer(delay_warning, send_message,
                        args=[f"⚠️ <b>{boss}</b> появится через 2 минуты!\n⏰ ≈ {appear_time.strftime('%H:%M:%S')}"]).start()

    # оповещение точно в момент появления
    delay_full = (appear_time - datetime.now(tz)).total_seconds()
    threading.Timer(delay_full, send_message,
                    args=[f"⚔️ <b>{boss} ПОЯВИЛСЯ!</b>\nВремя: {appear_time.strftime('%H:%M:%S')}"]).start()

    appear_str = appear_time.strftime('%H:%M')
    return f"{boss} умер в {death_time.strftime('%H:%M')}\nПоявится в ≈ {appear_str}"

# ================= Клавиатура =================
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn1 = telebot.types.KeyboardButton("🦇 Астарот умер сейчас")
btn2 = telebot.types.KeyboardButton("👹 Лилит умерла сейчас")
btn3 = telebot.types.KeyboardButton("✍ Астарот — вручную")
btn4 = telebot.types.KeyboardButton("✍ Лилит — вручную")
btn5 = telebot.types.KeyboardButton("📜 История записей")
markup.add(btn1, btn2, btn3, btn4, btn5)

# ================= Обработка =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
                     "Привет! Я бот-таймер для Астарота и Лилит\n"
                     "Выбирай кнопку или пиши время смерти вручную:\n"
                     "астарот 14:30\n"
                     "лилит 03:15", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    text = message.text.strip()

    # Кнопки «умер сейчас»
    if "Астарот умер сейчас" in text:
        reply = schedule_boss("АСТАРОТ", 4, 8)
        bot.reply_to(message, reply, reply_markup=markup)

    elif "Лилит умерла сейчас" in text:
        reply = schedule_boss("ЛИЛИТ", 3, 58)
        bot.reply_to(message, reply, reply_markup=markup)

    # Кнопки «вручную»
    elif text in ["✍ Астарот — вручную", "астарот вручную"]:
        bot.reply_to(message, "Отправь время смерти Астарота в формате 14:30")
        bot.register_next_step_handler(message, astaroth_manual)

    elif text in ["✍ Лилит — вручную", "лилит вручную"]:
        bot.reply_to(message, "Отправь время смерти Лилит в формате 03:15")
        bot.register_next_step_handler(message, lilith_manual)

    # История
    elif "История записей" in text:
        if history:
            hist = "\n".join(history)
            bot.reply_to(message, f"📜 Последние записи:\n{hist}", reply_markup=markup)
        else:
            bot.reply_to(message, "История пуста", reply_markup=markup)

    # Ручная запись через текст (астарот 14:30)
    else:
        try:
            cmd = text.lower().split()
            time_str = cmd[-1]
            t = datetime.strptime(time_str, "%H:%M")
            if "астарот" in text:
                appear = (datetime.now(tz).replace(hour=t.hour, minute=t.minute, second=0, microsecond=0) +
                          timedelta(hours=4, minutes=8))
                bot.reply_to(message, f"Астарот появится ≈ {appear.strftime('%H:%M')}")
                schedule_boss("АСТАРОТ", 4, 8)
            elif "лилит" in text:
                appear = (datetime.now(tz).replace(hour=t.hour, minute=t.minute, second=0, microsecond=0) +
                          timedelta(hours=3, minutes=58))
                bot.reply_to(message, f"Лилит появится ≈ {appear.strftime('%H:%M')}")
                schedule_boss("ЛИЛИТ", 3, 58)
        except:
            bot.reply_to(message, "Не понял. Используй кнопки или формат:\nастарот 14:30", reply_markup=markup)

def astaroth_manual(message):
    try:
        t = datetime.strptime(message.text.strip(), "%H:%M")
        schedule_boss("АСТАРОТ", 4, 8)
        bot.send_message(message.chat.id, f"Астарот записан на {message.text} + 4ч 8мин", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "Неправильный формат, попробуй ещё раз (14:30)", reply_markup=markup)

def lilith_manual(message):
    try:
        t = datetime.strptime(message.text.strip(), "%H:%M")
        schedule_boss("ЛИЛИТ", 3, 58)
        bot.send_message(message.chat.id, f"Лилит записана на {message.text} + 3ч 58мин", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "Неправильный формат, попробуй ещё раз (03:15)", reply_markup=markup)

bot.infinity_polling()