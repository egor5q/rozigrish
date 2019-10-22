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
db=client.base1
users=db.users
channels = db.channels

test_channel = -1001435448112
admins = [441399484]


def randomgen():
    alls = []
    symbols = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    for ids in channels.find({}):
        alls.append(ids['name'])
    text=''
    while len(text)<5:
        text+=random.choice(symbols)
    while text in alls:
        text=''
        while len(text)<5:
            text+=random.choice(symbols)
    return text

def createchannel():
    return {
        'name':randomgen(),
        'first':None,
        'second':None,
        'current_messages':{}
    }

def createuser(user):
    x = users.find_one({'id':user.id})
    if x == None:
        users.insert_one({
            'id':user.id,
            'name':user.first_name,
            'username':user.username,
            'c_container':None,
            'c_channel':None
        })
        x = users.find_one({'id':user.id})
    return x
    

def create_tg_channel(channel):
    return {
        'id':channel.id,
        'title':channel.title,
        'username':channel.username
    }
        
    
    

@bot.message_handler(commands=['current_container_info'])
def cinfo(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        fchat = None
        if user['first'] != None:
            fchat = user['first']['title']
        schat = None
        if user['second'] != None:
            schat = user['second']['title']
        text=''
        text += 'Текущий контейнер: `'+user['c_container']+'`;\n'
        text += 'Первый чат (в котором будет кнопка): '+fchat+';\n'
        text += 'Второй чат (на который надо подписаться): '+schat+'.\n'
    

@bot.message_handler(commands=['add'])
def addd(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        ch = createchannel()
        channels.insert_one(ch)
        users.update_one({'id':user['id']},{'$set':{'c_container':ch['name']}})
        bot.send_message(m.chat.id, 'Я создал новый контейнер! Его название - `'+ch['name']+'`. Теперь настройте его:\n'+
                         'Для установки своего названия введите `/set\_name имя`, где имя - название контейнера;\n'
                         'Для установки первого канала введите `/set\_first`;\n'+
                         'Для установки второго канала введите `/set\_second`, или оставьте пустым, если условия (подписки на второй канал) нет.\n',
                        parse_mode="markdown")
        
@bot.message_handler(commands=['set_name'])
def set_namee(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        x = m.text.split(' ')
        if len(x)>1:
            nextt = False
            name = x[1]
            alls = []
            for ids in channels.find({}):
                alls.append(ids['name'])
            if name not in alls:
                channels.update_one({'name':user['c_container']},{'$set':{'name':name}})
                bot.send_message(m.chat.id, 'Имя контейнера успешно изменено!')
            else:
                bot.send_message(m.chat.id, 'Контейнер с таким именем уже существует!')
        else:
            bot.send_message(m.chat.id, 'Для установки своего названия введите `/set\_name имя`, где имя - название контейнера;\n'+
                            'Ваш текущий контейнер: '+str(user['c_container']))+'.')
            
            
@bot.message_handler(commands=['set_first'])
def setfirst(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        users.update_one({'id':user['id']},{'$set':{'c_channel':'first'}})
        bot.send_message(m.chat.id, 'Теперь пришлите мне форвард с первого канала (на котором будет пост с кнопкой), к которому хотите привязать меня.')
        
        
@bot.message_handler(commands=['set_second'])
def setsecond(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        users.update_one({'id':user['id']},{'$set':{'c_channel':'second'}})
        bot.send_message(m.chat.id, 'Теперь пришлите мне форвард со второго канала (на который нужно подписаться для участия), к которому хотите привязать меня.')
        
        

@bot.message_handler(commands=['tests'])
def tstst(m):
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='a', callback_data='test'))   
    bot.send_message(-1001395267877, 'beee!', reply_markup=kb)
    
    
    
@bot.message_handler(content_types=['text'])
def forwards(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if m.forwarded_from != None and m.chat.id == m.from_user.id:
            if user['c_channel'] != None:
                try:
                    chat = bot.get_chat(m.forward_from_chat.id)
                    if chat.type == 'channel':
                        channels.update_one({'name':user['c_container']},{'$set':{user['c_channel']:create_tg_channel(m.forward_from_chat)}})
                        users.update_one({'id':user['id']},{'$set':{'c_channel':None}})
                        bot.send_message(m.chat.id, 'Успешно! Канал привязан к контейнеру!')
                    else:
                        bot.send_message(m.chat.id, 'Перешлите сообщение из канала, а не из чата!')
                except:
                    bot.send_message(m.chat.id, 'Для начала нужно сделать меня администратором канала!')

    
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

