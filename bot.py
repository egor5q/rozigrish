# -*- coding: utf-8 -*-
import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)


client=MongoClient(os.environ['database'])
db=client.
users=db.users

test_channel = -1001435448112

@bot.message_handler(commands=['tests'])
def tstst(m):
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='a', callback_data='test'))   
    bot.send_message(-1001395267877, 'beee!', reply_markup=kb)

    
@bot.callback_query_handler(func=lambda call:True)
def inline(call): 
    if call.data == 'test':
            user = bot.get_chat_member(test_channel, call.from_user.id)
            if user.status != 'left':
                bot.send_message(test_channel, 'Юзер '+call.from_user.first_name+' нажал и подписался!')
            else:
                bot.send_message(test_channel, 'Юзер '+call.from_user.first_name+' нажал, но не подписался!')



def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)   

print('7777')
bot.polling(none_stop=True,timeout=600)

