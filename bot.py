import os
from utils import write_message, keyboard, get_city_vk, keyboard_with_payload
from settings.config import upload, DEBUG
from database.models import User, db, Room
import requests
import json


MENU = ['поиск', 'поиск по полу', 'поиск по городу', 'стоп']

# Кнопки в беседе
conversation_buttons = {'Стоп': '/stop',
                        'Поделиться вашим профилем вк': '/sharing_vk'}

#  кнопка стоп
STOP = {'Стоп': '/stop'}


# Функция очистки бота
def clear_bot():
    u = User.query.delete()
    r = Room.query.delete()


def get_user(vk_id):
    """
        Получаем или создаем пользователя
        :vk_id: id пользователя вконтакте
    """
    user = User.query.filter_by(vk_id=vk_id).first()
    if user is None:
        user = User(vk_id=vk_id)
        db.session.add(user)
    return user


def new_profile(user, message):
    """
        Функция заполняет начальными данными профиль
    """
    if user.gender is None:
        if message in ['мужчина', 'женщина']:
            user.gender = message[0]
            user.city = get_city_vk(user.vk_id)
            return False
        else:
            write_message(user.vk_id, 'Привет, прежде чем начать, тебе придется ответить на 1 вопрос.\nКто ты?', keyboard(['Мужчина', 'Женщина']))
            return True
    else:
        return False


def get_vk_id_partner(room, user_vk_id):
    """
        Функция отдает vk id собеседника
    """
    if room.first_user_vk_id == user_vk_id:
        return room.second_user_vk_id
    else:
        return room.first_user_vk_id


def search_room(user, city=None, search_gender=None, gender_first_user=None):
    """
        Функция поиска комнаты общения
    """
    room = None
    created_room = Room.query.filter_by(first_user_vk_id=user.vk_id).first()
    found_room = Room.query.filter_by(second_user_vk_id=user.vk_id).first()
    if created_room and not found_room:
        room = created_room
    elif not created_room and found_room:
        room = found_room
    elif not created_room and not found_room:
        # Ищем доступную комнату
        if city is not None:
            write_message(user.vk_id, f'Поиск собеседника по городу {city.title()}\nЯ оповещу как найдет', keyboard_with_payload(STOP))
            room = Room.query.filter_by(second_user_vk_id=None,
                                        city=city).first()
        elif search_gender is not None and gender_first_user is not None:
            write_message(user.vk_id, f'Поиск собеседника по полу\nЯ оповещу как найдет', keyboard_with_payload(STOP))
            room = Room.query.filter_by(second_user_vk_id=None,
                                        city=city,
                                        search_gender=search_gender,
                                        gender_first_user=gender_first_user).first()
        else:
            write_message(user.vk_id, f'Поиск случайного собеседника\nЯ оповещу как найдет', keyboard_with_payload(STOP))
            room = Room.query.filter_by(second_user_vk_id=None).first()
        if room:
            room.second_user_vk_id = user.vk_id
            write_message(room.first_user_vk_id, 'Собеседник найден, можете начать общаться =)', keyboard_with_payload(STOP))
            write_message(room.second_user_vk_id, 'Собеседник найден, можете начать общаться =)', keyboard_with_payload(STOP))
        #  Создаем новую комнату
        elif room is None:
            room = Room(first_user_vk_id=user.vk_id,
                        city=city,
                        search_gender=user.search_gender,
                        gender_first_user=user.gender)
        db.session.add(room)
    user.state = 'беседа'  # обновим состояние пользователя
    return room


def delete_room(room, user_vk_id):
    """
        Функция останавливает беседу
    """
    partner = User.query.filter_by(vk_id=get_vk_id_partner(room, user_vk_id)).first()
    partner.state = None
    partner.search_gender = None
    write_message(get_vk_id_partner(room, user_vk_id), 'Ваш собеседник отключился', keyboard(MENU[:3]))
    db.session.delete(room)
    return True


def get_attachment(attachment):
    """
        Функция обрабатывает вложения в сообщении, если они присутствуют
    """
    if not attachment:
        return False
    else:
        attachment_type = attachment[0]['type']
        a_owner_id = attachment[0][attachment_type]['owner_id']
        a_id = attachment[0][attachment_type]['id']
        a_key = ''
        if 'access_key' in attachment[0][attachment_type]:
            a_key = attachment[0][attachment_type]['access_key']
        else:
            a_key = a_key
        if attachment_type == 'doc':
            pass
        elif attachment_type == 'audio_message':
            audio_message_link = attachment[0][attachment_type]['link_ogg']
            r = requests.get(audio_message_link)
            with open('message.ogg', 'wb') as file:
                file.write(r.content)
            audio_message = upload.audio_message(os.path.abspath("message.ogg"),
                                                 group_id=str(abs(-173031746)))
            attachments = f'doc{audio_message[0]["owner_id"]}_{audio_message[0]["id"]}'
        else:
            attachments = f'{attachment_type}{a_owner_id}_{a_id}_{a_key}'
        print(attachments)
        return attachments


def bot(obj):
    print(obj)
    payload = None
    if 'payload' in obj:
        payload = json.loads(obj['payload'])['command']
    attachment = obj['attachments']
    base_message = obj['text']  # Сообщение без обработки
    message = obj['text'].lower()
    user = get_user(obj['from_id'])
    if message == 'удалить' and DEBUG is True:  # Для разработки
        clear_bot()
    else:
        if new_profile(user, message) is False:
            if payload:
                if payload == '/stop':
                    room = search_room(user)
                    user.state = None
                    user.search_gender = None
                    try:
                        # Остановка поиска, если пользователь уже в беседе
                        delete_room(room, user.vk_id)
                        write_message(user.vk_id, 'Вы остановили поиск', keyboard(MENU[:3]))
                    except BaseException:
                        # Остановка поиска, если пользователь только начал поиск
                        db.session.delete(room)
                        write_message(user.vk_id, 'Вы остановили поиск', keyboard(MENU[:3]))
                elif payload == '/sharing_vk':
                    room = search_room(user)
                    try:
                        write_message(get_vk_id_partner(room, user.vk_id),
                                      f'Ваш собеседник поделился своей страницей: vk.com/id{user.vk_id}')
                    except BaseException:
                        write_message(user.vk_id, 'Не удалось отпрвить сообщение')
            else:
                if message in MENU[0:3]:
                    user.state = message
                elif user.state is None:
                    write_message(user.vk_id, 'Выбери в меню чем займемся', keyboard(MENU[:3]))
                if user.state == 'поиск':
                    if message == 'поиск':
                        search_room(user)
                elif user.state == 'поиск по полу':
                    if message == 'м' or message == 'ж' and user.search_gender is None:
                        user.search_gender = message
                        search_room(user,
                                    search_gender=user.gender,
                                    gender_first_user=message)
                    elif user.search_gender is None:
                        write_message(user.vk_id, 'Кого вы хотите найти', keyboard(['м', 'ж']))
                elif user.state == 'поиск по городу':
                        search_room(user, city=user.city)
                elif user.state == 'беседа':
                    room = search_room(user)
                    try:
                        write_message(get_vk_id_partner(room, user.vk_id),
                                      f'От собеседника:\n{base_message}',
                                      keyboard_with_payload(conversation_buttons),
                                      get_attachment(attachment))
                    except BaseException:
                        write_message(user.vk_id, 'Собеседник еще не найден, подождите чуть-чуть пожалуйста',
                                      keyboard_with_payload(conversation_buttons))
        else:
            pass
    db.session.commit()
