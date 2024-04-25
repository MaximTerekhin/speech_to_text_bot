import math
import telebot
import logging
from config import BOT_TOKEN, TABLE_NAME
from speech import speech_to_text
from data_bases import insert_info, get_blocks, create_table
from telebot.types import Message, ReplyKeyboardMarkup



bot = telebot.TeleBot(BOT_TOKEN)

MAX_BLOCKS = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",encoding='utf-8',
    filename="log_file.txt",
    filemode="w",
)

def create_reyboard(buttons):
    keyboard = ReplyKeyboardMarkup(row_width=2,
                                   resize_keyboard=True,
                                   one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard
user_history = {}


def duraction_voice(message, duractoin):
    user_id = message.from_user.id
    audio_blocks = math.ceil(duractoin/15)

    all_blocks = len(get_blocks(user_id)) + audio_blocks

    if all_blocks > MAX_BLOCKS:
        bot.send_message(user_id, 'У вас закончились попытки!')
        return
    if duractoin > 30:
        bot.send_message(user_id, 'Ваше гс слишком большое.\n'
                                  'Вы должны говорить не более 30 секунд!')
        bot.send_message(user_id, 'Говорите...')
        bot.register_next_step_handler(message,get_voice)
        return
    return audio_blocks




@bot.message_handler(commands=['start'])
def strt_message(message: Message):
    create_table(TABLE_NAME)
    user_id = message.from_user.id
    user_history['user_id'] = user_id
    user_history[user_id] = {}
    user_name = message.from_user.first_name
    bot.send_message(user_id, f'Привет {user_name}!\n'
                              f'Я бот-переводчик голоса в текст.\n'
                              f'Воспользуйся мной и ты узнаешь на что я способен! /stt', reply_markup=create_reyboard(['/stt']))
    logging.info('Приветственное сообщение.')

@bot.message_handler(commands=['stt'])
def stt(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Говорите...')
    logging.info('Бот запросил гс.')
    bot.register_next_step_handler(message, get_voice)

def get_voice(message):
    user_id = message.from_user.id

    if not message.voice:
        bot.send_message(user_id, 'Ваше сообщение - не голос!\n\n\n'
                                  'Гооврите...')
        logging.info('Пользователь ошибся с запросом.')
        bot.register_next_step_handler(message, get_voice)
        return
    blocks = duraction_voice(message, message.voice.duration)
    print(blocks)
    if blocks:
        logging.info('Сохранение запроса..')
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status, text = speech_to_text(file)
        print(text)
        logging.info('Запрос произведен.')
        count_token_text = int(len(text))
        user_history[user_id]['count_token'] = count_token_text
        if status:
            bot.send_message(user_id, text, reply_to_message_id=message.id, reply_markup=create_reyboard(['/count_tokens_text',
                                                                                                          '/debug', '/restart']))
            logging.info('Запрос успешен.')
            insert_info([user_id, text, count_token_text, blocks])
        else:
            bot.send_message(user_id, text)
            logging.info('Ошибка в запросе!')


@bot.message_handler(commands=['count_tokens_text'])
def count(message):
    user_id = message.from_user.id
    bot.send_message(user_id, f'Вы получили текст длиной {user_history[user_id]["count_token"]}')

@bot.message_handler(commands=['debug'])
def debug(message):
    user_id = message.from_user.id
    with open('log_file.txt', encoding='utf-8') as file:
        bot.send_document(user_id, file)

@bot.message_handler(commands=['restart'])
def resturt(message):
    strt_message(message)

bot.polling()