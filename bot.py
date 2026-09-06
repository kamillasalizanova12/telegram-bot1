import os
import time
import logging
import threading

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- НАСТРОЙКИ (токен берём из переменной окружения, чтобы не светить в коде) ---
TOKEN = os.environ.get("BOT_TOKEN", "8903154676:AAFoPH7FLvaf57XMZjoNZ8svftN9aYlHSHH0")
CHANNEL_ID = "@progressguest"
TEST_URL = "https://test-production-7310.up.railway.app/"

bot = telebot.TeleBot(TOKEN)
telebot.apihelper.REQUEST_TIMEOUT = 60


# ---- ПРОВЕРКА ПОДПИСКИ ----
def is_subscribed(chat_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, chat_id)
        return member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False


# ---- ОТПРАВКА СООБЩЕНИЯ ----
def send_message_safe(chat_id, text, reply_markup=None):
    for attempt in range(5):
        try:
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
        except Exception as e:
            logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
            time.sleep(3)
    return None


# ---- ФИНАЛЬНОЕ СООБЩЕНИЕ ----
def send_final_message(chat_id):
    time.sleep(10)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📅 ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ →", url="https://t.me/arj_grow"))
    for attempt in range(5):
        try:
            bot.send_message(
                chat_id,
                "🎯 Теперь ты знаешь, какие ИИ-инструменты могут быть полезны именно твоему бизнесу.\n\n"
                "🔥 Но самое главное — понять, какие задачи стоит автоматизировать в первую очередь\n"
                "и как внедрить ИИ именно в твои процессы.\n\n"
                "Если хочешь разобрать свой бизнес и подобрать решения под конкретные задачи — "
                "приглашаю на консультацию.",
                reply_markup=markup
            )
            return
        except Exception as e:
            logger.warning(f"Финальное сообщение, попытка {attempt + 1}: {e}")
            time.sleep(3)


# ---- КОМАНДА /start ----
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 ПОДПИСАТЬСЯ НА КАНАЛ", url="https://t.me/progressguest"))
    markup.add(InlineKeyboardButton("✅ ПРОВЕРИТЬ ПОДПИСКУ", callback_data="check_sub"))
    send_message_safe(
        chat_id,
        "👋 Привет! Я подготовил для тебя бесплатный тест «Какой ИИ нужен вашему бизнесу?»\n"
        "Ответь на несколько вопросов — и в конце получишь персональный список ИИ-инструментов.\n\n"
        "⚠️ Чтобы получить доступ к тесту, сначала подпишись на канал (если ещё не подписан):",
        reply_markup=markup
    )


# ---- ПРОВЕРКА ПОДПИСКИ ----
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    chat_id = call.message.chat.id
    if is_subscribed(chat_id):
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🚀 ПРОЙТИ ТЕСТ →", url=TEST_URL))
        send_message_safe(
            chat_id,
            "✅ Отлично! Подписка подтверждена.\n\n"
            "Теперь тебе доступен тест.\n"
            "Нажми на кнопку ниже, чтобы пройти тест и получить персональную подборку ИИ-инструментов:",
            reply_markup=markup
        )
        threading.Thread(target=send_final_message, args=(chat_id,), daemon=True).start()
    else:
        bot.answer_callback_query(
            call.id,
            "❌ Подписка не найдена! Подпишись на канал и нажми кнопку снова.",
            show_alert=True
        )


# ---- ЗАПУСК ----
if __name__ == "__main__":
    print("=" * 50)
    print("📢 Канал:", CHANNEL_ID)
    print("🔗 Тест:", TEST_URL)
    print("=" * 50)

    while True:
        try:
            logger.info("🤖 Бот запущен, начинаю polling...")
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            logger.error(f"❌ Ошибка polling: {e}")
            logger.info("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)
