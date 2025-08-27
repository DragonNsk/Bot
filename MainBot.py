import os
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    CallbackQueryHandler
)

# Включим логирование, чтобы видеть ошибки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Проверяем, что токен установлен
if not BOT_TOKEN:
    raise ValueError("Не установлен BOT_TOKEN в переменных окружения!")

# Определяем состояния (шаги) разговора
NAME, SOURCE, FINISH = range(3)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        return
    
    await update.message.reply_text(
        "Привет! Добро пожаловать! 😊\n"
        "Как тебя зовут?"
    )
    return NAME

# Обработчик ответа с именем
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    context.user_data['name'] = user_name
    
    reply_keyboard = [
        ['От друзей', 'В рекламе'],
        ['По просьбе']
    ]
    
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Приятно познакомиться, {user_name}! 🤗\n"
        "Откуда ты узнал(а) обо мне?",
        reply_markup=markup
    )
    return SOURCE

# Обработчик выбора источника
async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    source = update.message.text
    context.user_data['source'] = source
    
    await update.message.reply_text(
        f"Спасибо за ответ! 📝",
        reply_markup=ReplyKeyboardRemove()
    )
    
    keyboard = [
        [InlineKeyboardButton("Подписаться на канал 📢", url="https://t.me/kamenoptstore")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Обязательно подпишись на наш канал @kamenoptstore, "
        "там много полезной информации и акций!",
        reply_markup=reply_markup
    )
    
    logger.info(f"Пользователь {context.user_data.get('name')} узнал о боте: {source}")
    
    return ConversationHandler.END

# Обработчик отмены диалога
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Диалог прерван. Если захочешь пообщаться снова, напиши /start',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Обработчик для приветствия новых участников в группе
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for new_member in update.message.new_chat_members:
        if new_member.id == context.bot.id:
            await update.message.reply_text(
                "Спасибо, что добавили меня в группу! 😊\n"
                "Для начала работы напишите мне в личные сообщения @ваш_бот."
            )
        else:
            await update.message.reply_text(
                f"Добро пожаловать, {new_member.first_name}! 🎉\n"
                f"Напиши мне в личные сообщения @{context.bot.username}, чтобы познакомиться!"
            )

# Главная функция
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_source)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(conv_handler)
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()