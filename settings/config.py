import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from settings.local_config import *

DEBUG = DEBUG

if DEBUG is True:
    token = DEB_TOKEN
    community_id = str(abs(DEB_COMMUNITY))
else:
    token = TOKEN
    community_id = str(abs(COMMUNITY))

# Настройки лонгпул для сообщества
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, community_id)

# Настройки для аккаунта вк
vk_user_session = vk_api.VkApi(LOGIN, PASSWORD)
vk_user_session.auth()
upload = vk_api.VkUpload(vk_user_session)

# Настройки для базы данных
database_user = DATABASE_USER
database_password = DATABASE_PASSWORD
database_name = DATABASE_NAME
