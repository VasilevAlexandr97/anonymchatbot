from settings.config import vk_session
import json


def get_city_vk(vk_id):
    """
         Функция получения города пользователя из vk
    """
    r = vk_session.method('users.get', {'user_ids': vk_id,
                                        'fields': 'city'})
    return r[0]['city']['title'].lower()


# Функция отправки сообщения
def write_message(user_id, msg=None, keyboard=None, attachment=None):
    vk_session.method('messages.send', {
                      'user_id': user_id,
                      'message': msg,
                      'keyboard': keyboard,
                      'attachment': attachment})


# Функция создает json клавиатуры для вк бота
# Функция принимает на вход список с названиями кнопок
def keyboard(buttons):
    KEYBOARD = {'one_time': False}
    BUTTONS = []
    COUNT_BUTTONS = len(buttons)
    for button in buttons:
        BUTTONS.append([{'action': {'type': 'text', 'label': button.capitalize()},'color': 'primary'}])
    KEYBOARD['buttons'] = BUTTONS
    return json.dumps(KEYBOARD, ensure_ascii=False)
