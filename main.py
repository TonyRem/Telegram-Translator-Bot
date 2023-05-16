import os
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from gtts import gTTS
from googletrans import Translator

from dotenv import load_dotenv

load_dotenv()

updater = Updater(
    token=os.getenv('token'), use_context=True
)
dispatcher = updater.dispatcher


def translate_text(text, src, dest):
    translator = Translator()
    translated_text = translator.translate(text, src=src, dest=dest).text
    return translated_text


def start(update, context):
    buttons = ReplyKeyboardMarkup(
        [["ru-en"], ["en-ru"]], one_time_keyboard=True, resize_keyboard=True
    )
    reply_markup = buttons
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Выбери направление перевода:",
        reply_markup=reply_markup,
    )


def ru_en_handler(update, context):
    context.user_data["translation_direction"] = ("ru", "en")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Выбрано направление перевода: русский -> английский. "
              "Отправь мне текст, который нужно перевести.")
    )


def en_ru_handler(update, context):
    context.user_data["translation_direction"] = ("en", "ru")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Выбрано направление перевода: английский -> русский. "
            "Отправь мне текст, который нужно перевести."
        ),
    )


def text_message(update, context):
    text = update.message.text

    if "translation_direction" in context.user_data:
        src, dest = context.user_data["translation_direction"]
        translated_text = translate_text(text, src, dest)

        tts_translation = gTTS(text=translated_text, lang=dest)
        tts_translation.save("audio_translation.mp3")

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Перевод: {}".format(translated_text)
        )
        context.bot.send_audio(
            chat_id=update.effective_chat.id,
            audio=open("audio_translation.mp3", "rb")
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("Сначала выбери направление перевода, "
                  "нажав на одну из кнопок /start.")
        )


start_handler = CommandHandler("start", start)
ru_en_handler = MessageHandler(Filters.regex("^ru-en$"), ru_en_handler)
en_ru_handler = MessageHandler(Filters.regex("^en-ru$"), en_ru_handler)
text_handler = MessageHandler(Filters.text & (~Filters.command), text_message)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(ru_en_handler)
dispatcher.add_handler(en_ru_handler)
dispatcher.add_handler(text_handler)

updater.start_polling()
updater.idle()
