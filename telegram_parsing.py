
#====================================================================================================
import asyncio
from collections import Counter
from telethon.tl.functions.messages import GetHistoryRequest
from telethon import types

import configparser

from telethon.sync import TelegramClient

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest
#====================================================================================================


#====================================================
# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, api_id, api_hash)
#====================================================


#========================================================================================================
async def get_post_comments(channel_username, post_id, commentators, commentators_id):
    current_comment = {}
    try:
        async for message in client.iter_messages(channel_username, reply_to = post_id, reverse = True):
            print(str(post_id))
            sender = message.sender
            sender_id = message.from_id.user_id if message.from_id else None
            print(message.date, ':', message.text)
            if isinstance(sender, types.User):
                sender_name = sender.first_name if sender.first_name else "Unknown User"
                print(message.date, sender_name, ':', message.text)
                current_comment = {"date": message.date, "sender_name": sender_name, "message.text": message.text}
            elif sender is not None:
                sender_title = getattr(sender, 'title', 'Unknown Channel/Group')
                print(message.date, sender_title, ':', message.text)
                current_comment = {"date": message.date, "sender_name": sender_title, "message.text": message.text}
            else:
                print(message.date, 'Unknown Sender:', message.text)
                current_comment = {"date": message.date, "sender_name": 'Unknown Sender', "message.text": message.text}

            commentators.append(str(current_comment['sender_name']))
            commentators_id.append(str(sender_id))

            # Открытие файла в режиме добавления (append mode)
            with open('comments.txt', 'a') as file:
                file.write(
                        str(current_comment['date'])
                        + "  "
                        + str(current_comment['sender_name'])
                        + "  "
                        + str(current_comment['message.text'])
                        + '\n'
                        )
                
    except Exception as e:
        print(f'Error: {e}')

    finally:
        pass
#========================================================================================================



#=================================================================================
async def dump_all_messages(channel):
    offset_msg = 0    # номер записи, с которой начинается считывание
    limit_msg = 100   # максимальное число записей, передаваемых за один раз

    all_messages = []   # список всех сообщений
    all_messages_ids = []
    total_messages = 0
    total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

    while True:
        history = await client(GetHistoryRequest(
            peer = channel,
            offset_id = offset_msg,
            offset_date = None, add_offset=0,
            limit = limit_msg, max_id = 0, min_id = 0,
            hash = 0))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            message2dict = message.to_dict()
            # сохраняем все НЕПУСТЫЕ посты
            if 'message' in message2dict:
                message_data = {
                        'message': message2dict['message'],
                        'date': message2dict['date'],
                        'id': message2dict['id']
                     }
                all_messages.append(message_data)
            # сохраняем все id 
            if 'id' in message2dict:
                message_id = {
                        'id': message2dict['id']
                     }
                all_messages_ids.append(message_id)
                
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
#=================================================================================



async def main():
    url = 'https://t.me/bogda2na_beads'
    await client.start()
    commentators = []
    commentators_id = []

    tasks = []
    for id in range(0, 481):
        tasks.append(get_post_comments(url, id, commentators, commentators_id))

    await asyncio.gather(*tasks)
    print("Запросы отправлены и ответы получены")
    counter = Counter(commentators)
    print(counter)
    counter_ids = Counter(commentators_id)
    print(counter_ids)

    # Открываем файл для добавления
    with open('commentators.txt', 'a', encoding='utf8') as file:
        for key, value in counter.items():
            file.write(f'{key} – {value}\n')

    # Открываем файл для добавления
    with open('commentators.txt', 'a', encoding='utf8') as file:
        for key, value in counter_ids.items():
            file.write(f'{key} – {value}\n')

with client:
    client.loop.run_until_complete(main())



