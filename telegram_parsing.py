
#====================================================================================================
import asyncio
from collections import Counter

import configparser

# класс для работы с сообщениями
from telethon import types
from telethon.sync import TelegramClient
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