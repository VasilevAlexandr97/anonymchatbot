from vk_api.bot_longpoll import VkBotEventType
from settings.config import longpoll
from bot import bot


for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        bot(event.obj)
