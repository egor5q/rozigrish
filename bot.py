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
admins = [441399484, 864442319]


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
            'c_channel':None,
            'c_event':None,
            'c_option':None
        })
        x = users.find_one({'id':user.id})
    return x
    

def create_tg_channel(channel):
    return {
        'id':channel.id,
        'title':channel.title,
        'username':channel.username
    }
        
  

def randomid():
    alls = []
    symbols = ['1', '2', '3', '4', '5', '6', '7']
    for ids in channels.find({}):
        print(ids)
        for idss in ids['current_messages']:
            print(idss)
            alls.append(ids['current_messages'][idss]['id'])
            
    text=''
    while len(text)<5:
        text+=random.choice(symbols)
    while text in alls:
        text=''
        while len(text)<5:
            text+=random.choice(symbols)
    return text
    

def createmessage():
    id=randomid()
    return {id:{
        'id':id,
        'kb':None,
        'msg_text':None,
        'button_text':None,
        'msg_id':None,
        'max_users':None,
        'name':id,
        'clicked_users':[]
    }}

  

@bot.message_handler(commands=['select_container'])
def select_containerr(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        x = m.text.split(' ')
        if len(x)>1:
            name = x[1]
            cont = channels.find_one({'name':name})
            if cont == None:
                bot.send_message(m.chat.id, 'Контейнера с таким именем не существует! Для просмотра всех контейнеров нажмите '+
                                 '/select_container.')
            else:
                users.update_one({'id':user['id']},{'$set':{'c_container':name}})
                bot.send_message(m.chat.id, 'Успешно изменён текущий контейнер!')
        else:
            text = 'Список контейнеров:\n'
            for ids in channels.find({}):
                text += '`'+ids['name']+'`\n'
            text+='\nДля выбора контейнера введите:\n/select\_container имя\nГде имя - имя контейнера.' 
            bot.send_message(m.chat.id, text, parse_mode = 'markdown')
            
            
@bot.message_handler(commands=['select_event'])
def select_event(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_container'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте контейнер (/add)!')
            return
        x = m.text.split(' ')
        if len(x)>1:
            name = x[1]
            cont = channels.find_one({'name':user['c_container']})
            
            if name not in cont['current_messages']:
                bot.send_message(m.chat.id, 'События с таким айди не существует! Нажмите /select_event для просмотра всех событий.')
            
            else:
                users.update_one({'id':user['id']},{'$set':{'c_event':name}})
                bot.send_message(m.chat.id, 'Успешно изменено текущее событие!')
        else:
            text = 'Список событий:\n'
            for ids in channels.find_one({'name':user['c_container']})['current_messages']:
                text += '`'+ids['id']+'` (имя события: "'+ids['name']+'")\n'
            text+='\nДля выбора события введите:\n/select\_event id\nГде id - айди события.' 
            bot.send_message(m.chat.id, text, parse_mode = 'markdown')
            
    
@bot.message_handler(commands=['add_event'])
def add_event(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_container'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте контейнер (/add)!')
            return
        cont = channels.find_one({'name':user['c_container']})
        x = createmessage()
        for ids in x:
            y=ids
        channels.update_one({'name':cont['name']},{'$set':{'current_messages.'+y:x[y]}})
        users.update_one({'id':user['id']},{'$set':{'c_event':y['id']}})
        bot.send_message(m.chat.id, 'Успешно создано событие! Его имя: '+y['name']+'. Теперь настройте его:\n'+
                         '/set_e_name - имя события;\n'+
                         '/set_e_text - текст сообщения с розыгрышем;\n'+
                         '/set_e_button - текст кнопки с розыгрышем;\n'+
                         '/set_e_max_users - максимальное число участников розыгрыша.\n')
        

@bot.message_handler(commands=['set_e_name'])  
def nameevent(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_event'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте событие (/add_event)!')
            return
        x = m.text.split(' ')
        if len(x)>1:
            alls=[]
            name = x[1]
            for ids in channels.find({}):
                for idss in ids['current_messages']:
                    alls.append(ids['current_messages'][idss]['name'])
            if name not in alls:
                channels.update_one({'name':user['c_container']},{'$set':{'current_messages.'+user['c_event']+'.name':name}})
                bot.send_message(m.chat.id, 'Вы успешно сменили имя события на "'+name+'"!')
            else:
                bot.send_message(m.chat.id, 'Событие с таким именем уже существует!')
        else:
            bot.send_message(m.chat.id, 'Для изменения имени события используйте формат:\n/set_e_name имя\nГде имя - имя события.')
            
            
            
@bot.message_handler(commands=['set_e_text'])  
def nameevent(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_event'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте событие (/add_event)!')
            return
        x = m.text.split(' ')
        if len(x)>1:
            text = x[1]
            event = channels.find_one({'name':user['c_container']})['current_messages'][user['c_event']]['name']
            channels.update_one({'name':user['c_container']},{'$set':{'current_messages.'+user['c_event']+'.msg_text':text}})
            bot.send_message(m.chat.id, 'Успешно изменён текст сообщения события "'+event+'"!')
        else:
            bot.send_message(m.chat.id, 'Для изменения текста сообщения события используйте формат:\n/set_e_text текст\nГде текст - текст события.')
        
@bot.message_handler(commands=['set_e_button'])  
def nameevent(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_event'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте событие (/add_event)!')
            return
        x = m.text.split(' ')
        if len(x)>1:
            text = x[1]
            event = channels.find_one({'name':user['c_container']})['current_messages'][user['c_event']]['name']
            channels.update_one({'name':user['c_container']},{'$set':{'current_messages.'+user['c_event']+'.button_text':text}})
            bot.send_message(m.chat.id, 'Успешно изменён текст кнопки события "'+event+'"!')
        else:
            bot.send_message(m.chat.id, 'Для изменения текста сообщения события используйте формат:\n/set_e_text текст\nГде текст - текст события.')
        
        
@bot.message_handler(commands=['set_e_max_users'])  
def nameevent(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_event'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте событие (/add_event)!')
            return
        x = m.text.split(' ')
        if len(x)>1:
            try:
                text = int(x[1])
            except:
                bot.send_message(m.chat.id, 'Для изменения максимального количества участников события используйте формат:\n/set_e_max_users число\nГде число - максимальное число юзеров.')
                return
            event = channels.find_one({'name':user['c_container']})['current_messages'][user['c_event']]['name']
            channels.update_one({'name':user['c_container']},{'$set':{'current_messages.'+user['c_event']+'.max_users':text}})
            bot.send_message(m.chat.id, 'Успешно изменено максимальное количество юзеров события "'+event+'"!')
        else:
            bot.send_message(m.chat.id, 'Для изменения максимального количества участников события используйте формат:\n/set_e_max_users число\nГде число - максимальное число юзеров.')
        
        
        

@bot.message_handler(commands=['current_container_info'])
def cinfo(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_container'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте контейнер (/add)!')
            return
        cont = channels.find_one({'name':user['c_container']})
        if cont != None:
            fchat = None
            if cont['first'] != None:
                fchat = cont['first']['title']
            schat = None
            if cont['second'] != None:
                schat = cont['second']['title']
            text=''
            text += 'Текущий контейнер: `'+user['c_container']+'`;\n'
            text += 'Первый чат (в котором будет кнопка): '+str(fchat)+';\n'
            text += 'Второй чат (на который надо подписаться): '+str(schat)+'.\n'
            bot.send_message(m.chat.id, text, parse_mode="markdown")
    

@bot.message_handler(commands=['add'])
def addd(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        ch = createchannel()
        channels.insert_one(ch)
        users.update_one({'id':user['id']},{'$set':{'c_container':ch['name']}})
        bot.send_message(m.chat.id, 'Я создал новый контейнер! Его название - `'+ch['name']+'`. Теперь настройте его:\n'+
                         'Для установки своего названия введите `/set_name имя`, где имя - название контейнера;\n'
                         'Для установки первого канала введите `/set_first`;\n'+
                         'Для установки второго канала введите `/set_second`, или оставьте пустым, если условия (подписки на второй канал) нет.\n',
                        parse_mode="markdown")
        
@bot.message_handler(commands=['set_name'])
def set_namee(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_container'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте контейнер (/add)!')
            return
        x = m.text.split(' ')
        if len(x)>1:
            nextt = False
            name = x[1]
            alls = []
            for ids in channels.find({}):
                alls.append(ids['name'])
            if name not in alls:
                channels.update_one({'name':user['c_container']},{'$set':{'name':name}})
                users.update_one({'id':user['id']},{'$set':{'c_container':name}})
                bot.send_message(m.chat.id, 'Имя контейнера успешно изменено!')
            else:
                bot.send_message(m.chat.id, 'Контейнер с таким именем уже существует!')
        else:
            bot.send_message(m.chat.id, 'Для установки своего названия введите `/set_name имя`, где имя - название контейнера;\n'+
                            'Ваш текущий контейнер: '+str(user['c_container'])+'.', parse_mode="markdown")
            
            
@bot.message_handler(commands=['set_first'])
def setfirst(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_container'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте контейнер (/add)!')
            return
        x = m.text.split(' ')
        if len(x) > 1:
            if x[1].lower() == 'none':
                channels.update_one({'name':user['c_container']},{'$set':{'first':None}})
                bot.send_message(m.chat.id, 'Успешно отменён канал!')
                users.update_one({'id':user['id']},{'$set':{'c_channel':None}})
                return
        users.update_one({'id':user['id']},{'$set':{'c_channel':'first'}})
        bot.send_message(m.chat.id, 'Теперь пришлите мне форвард с первого канала (на котором будет пост с кнопкой), к которому хотите привязать меня.')
        
        
@bot.message_handler(commands=['set_second'])
def setsecond(m):
    user = createuser(m.from_user)
    if m.from_user.id in admins:
        if user['c_container'] == None:
            bot.send_message(m.chat.id, 'Сначала создайте контейнер (/add)!')
            return
        x = m.text.split(' ')
        if len(x) > 1:
            if x[1].lower() == 'none':
                channels.update_one({'name':user['c_container']},{'$set':{'second':None}})
                bot.send_message(m.chat.id, 'Успешно отменён канал!')
                users.update_one({'id':user['id']},{'$set':{'c_channel':None}})
                return
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
        if m.forward_from_chat != None and m.chat.id == m.from_user.id:
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

