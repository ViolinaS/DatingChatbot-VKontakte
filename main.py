import configdata
import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.exceptions import VkApiError
from vktools import Keyboard, ButtonColor, Text
import random
from sqlalchemy.sql import select, delete
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from postgreSQL_db import engine, Base, User, Wanted_user, Black_list


"""Клавиатуры и константы для работы в чате
"""
FUTUREDATE = datetime.now() + timedelta(days=10)

RELATION_DATA_RULE = ["в активном поиске", "не женат/не замужем", "все сложно"]
RELATION_KEYBOARD = Keyboard(one_time=True, inline=False, button=[
    [

        Text("в активном поиске", ButtonColor.POSITIVE),
        Text("не женат/не замужем", ButtonColor.PRIMARY)

    ],
    [
        Text("все сложно", ButtonColor.NEGATIVE)
    ]
]
).add_keyboard()

ACTIVATION_KEYBOARD = Keyboard(one_time=True, inline=False, button=[
    [
        Text("STOP", ButtonColor.NEGATIVE),
        Text("START", ButtonColor.POSITIVE)

    ],
]
).add_keyboard()

YES_OR_NO_KEYBOARD = Keyboard(one_time=True, inline=False, button=[
    [
        Text("ДА", ButtonColor.POSITIVE),
        Text("НЕТ", ButtonColor.NEGATIVE),
        Text("ОТМЕНА", ButtonColor.PRIMARY)

    ],
]
).add_keyboard()


"""Стартовые Хендлеры
"""


def send_message(peer_id, message=None, attachment=None, keyboard=None, payload=None):
    bot_1.messages.send(peer_id=peer_id, message=message, random_id=randrange(10 ** 7),
                        attachment=attachment, keyboard=keyboard, payload=payload)


def get_current_user_id():
    print("Напишите боту в чат Vkontakte слово 'Привет', это активирует бота")
    for event in longpoll_1.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request == "привет":
                    user = bot_1.users.get(user_ids=event.user_id)
                    user_id = user[0]['id']
                    return user_id


def name_from_id(user_id):
    user = bot_1.users.get(user_ids=user_id)
    return user[0]['first_name'] + ' ' + user[0]['last_name']


def vkinder_say_hi(user_id):
    send_message(user_id, f'Привет, {name_from_id(user_id)}\n'
                 f"Если ты хочешь сходить на свидание или просто поболтать, то Я,"
                 f"скромный, но очень талантливый\nБОТ для знакомств готов тебе помочь."
                 f"Я профессионал, поэтому подберу тебе идеальную пару в твоем городе.\n"
                 f"Минуточку....я кое-что проверю")
    print("Бот Vkinder успешно запустился в Vkontakte.")


"""Бот проверяет профиль пользователя на наличие данных о городе, поле, дате рождения, семейном положении.
"""


def get_user_data(user_id):
    try:
        user_data = bot_1.users.get(
            user_ids=user_id, fields="city, sex, bdate, relation")
    except VkApiError as e:
        print("Ошибка", e.code)
    else:
        return user_data


"""Бот собирает информацию о городе проживания.
   Если информация не указана, Бот запрашивает ее у пользователя
   и вычисляет ID города в базе VK
"""


def get_city_from_data():
    city_data = get_user_data(user_id=user_id)

    if "city" not in city_data[0].keys():
        send_message(user_id, f'Уточните в каком городе ищем пару?')
        for event in longpoll_1.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and user_id == event.user_id:
                request_city = event.text.capitalize()
                break

        user_city_title = request_city
        user_country_search = bot_2.database.getCountries(code="RU")
        get_country = [country['id']
                       for country in user_country_search['items']]
        user_country_id = get_country[0]
        user_city_check = bot_2.database.getCities(
            country_id=user_country_id, q=user_city_title, need_all=0, count=1)
        user_city = [city['id'] for city in user_city_check['items']]
        user_city_id = user_city[0]
        send_message(user_id, f"Будем искать где-то здесь: {user_city_check}")
        return user_city_id

    else:
        user_city = city_data[0]["city"]
        user_city_id = user_city["id"]
        user_city_title = user_city["title"]
        send_message(user_id, f"Будем искать в городе: {user_city_title}")
        return user_city_id


"""Бот уточняет пол пользователя.
   Пола в VK не может не быть указано => без условий проверки.
   Пару Бот подбирает пользователю противоположного пола
"""


def get_sex_from_data():
    user_sex_info = get_user_data(user_id=user_id)[0]["sex"]
    if user_sex_info == 1:
        user_sex = 2  # меняем пол на противоположный
    else:
        user_sex = 1  # меняем пол на противоположный

    return user_sex


"""
Дата рождения в VK может быть скрыта полностью или только скрыт год.
Выполняется проверка на количество символов в строке даты рождения, при формате D.MM.YYYY
Выполняется проверка на наличие ключа 'bdate'
"""


def get_bdate_from_data():
    user_bdate = get_user_data(user_id=user_id)
    if "bdate" not in user_bdate[0].keys() or len(user_bdate[0]["bdate"]) < 9:

        while True:
            send_message(
                user_id, f'Укажите дату вашего рождения в формате D.M.YYYY: ?')
            for event in longpoll_1.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and user_id == event.user_id:
                    user_bdate = event.text
                    break

            try:
                datetime.strptime(user_bdate, '%m.%d.%Y').date()
                break

            except ValueError:
                send_message(user_id, f'Вы неверно указали дату рождения!')
            continue

    else:
        user_bdate = user_bdate[0]["bdate"]
    return user_bdate


def get_user_age():
    birth_year_data = bdate
    birth_year_number = birth_year_data[-4:]
    birth_year_int = int(birth_year_number)
    current_year = FUTUREDATE.year
    user_age = current_year - birth_year_int
    return user_age


"""VK_API
   relation (integer) Семейное положение.
   Возможные значения:
   1 — не женат/не замужем; 2 — есть друг/есть подруга;
   3 — помолвлен/помолвлена; 4 — женат/замужем;
   5 — всё сложно; 6 — в активном поиске;
   7 — влюблён/влюблена; 8 — в гражданском браке;
   0 — не указано.

   Выполняется проверка, если статус не указан или по логике требуется уточнение,
   например если статус пользователя 'влюблён/влюблена', 'помолвлен/помолвлена', женат/замужем,
   кого еще он/она себе дополнительно ищет?
"""


def get_user_relation_data():
    user_relation = get_user_data(user_id=user_id)[0]["relation"]
    if user_relation in [0, 8, 7, 4, 3, 2]:
        send_message(user_id, f"Укажите семейное положение (личный статус) искомого человека на клавиатуре",
                     keyboard=RELATION_KEYBOARD)
        for event in longpoll_1.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and user_id == event.user_id:
                user_relation = event.text.lower()
                break

        while user_relation not in RELATION_DATA_RULE:
            send_message(
                user_id, f"Неверный выбор, выберите личный статус искомого человека на клавиатуре еще раз", keyboard=RELATION_KEYBOARD)
            for event in longpoll_1.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and user_id == event.user_id:
                    user_relation = event.text.lower()
                    break

        else:
            user_relation = user_relation
            if user_relation == "в активном поиске":
                user_relation = 6
            elif user_relation == "не женат/не замужем":
                user_relation = 1
            else:
                user_relation = 5
            return user_relation
    else:
        return user_relation


"""Выполняется запуск поиска по базе VK на основе полученных данных у пользователя Бота.
   ID популярных и подходящих по параметрам пользователю кандидатов сохраняются во временном
   списке. Из списка кандидатов извлекаются рандомно кандидаты, их имена, фамилии, фотографии.
   Выполняется отбор самых популярных по likes 3 фото каждого кандидата.
"""


def execute_search():
    wanted_users = bot_2.users.search(sort=0, offset=0, count=1000, is_closed=0, has_photo=1, country_id=1,
                                      status=relation, age_from=user_age, age_to=user_age, city_id=city, sex=sex)
    if 'items' in wanted_users.keys():
        users_ids = [user['id'] for user in wanted_users['items']]
        return users_ids
    else:
        raise Exception("Сервер вернул неверный объект")
    # Объект должен содержать число результатов в поле count и массив объектов в поле items


def choose_random_babe(babe_list):
    while True:  # Бот ищет закрытый профиль, если находит, то выбирает другого кандидата
        show_babe = random.choice(babe_list)
        show_babe_casting = bot_2.users.get(user_ids=show_babe)
        ready_to_cast = show_babe_casting[0]['is_closed']
        print(ready_to_cast)

        try:
            ready_to_cast = show_babe_casting[0]['is_closed']
            if ready_to_cast == 0:

                break

        except ValueError:
            pass

        continue

    return show_babe


def get_random_babe_name(babe_id):
    global babe_info
    babe_info = bot_1.users.get(user_ids=babe_id)
    babe_name = babe_info[0]['first_name']
    return babe_name


def get_random_babe_surname():
    babe_surname = babe_info[0]['last_name']
    return babe_surname


def get_wanted_3_photos(babe_id):
    babe_photo_album = bot_2.photos.get(
        owner_id=babe_id, album_id="profile", extended=1)
    try:
        if 'items' in babe_photo_album.keys():
            babe_photos = babe_photo_album['items']
    except VkApiError as e:
        print("Возникла ошибка", e.code)

    else:
        best_likes_photo_dict = {}
        for photo in babe_photos:
            likes = photo['likes']['count']
            ids = photo['id']
            for size in photo['sizes']:
                if size['type'] == 'x':
                    url = size['url']

            best_likes_photo_dict[url] = likes, ids

    best3_photos = sorted(best_likes_photo_dict.items(),
                          key=lambda x: x[1], reverse=True)[0:3]
    return best3_photos


"""Формирование вывода на экран в чате VK данных о кандидатах пользователю.
   Бот показывает максимально 3 лучших фото из профиля кандидата, если у кандидата
   менее 3-х фото в профиле, то Бот покажет сколько есть. Выбор кандидата происходит
   произвольно каждый раз из новой (+-) 1000 человек, предсказать сколько
   у него/ее окажется фото в профиле и кто окажется им/ей невозможно.
"""


class Wanted:

    def __init__(self, babe_id, babe_name, babe_surname):
        self.babe_id = babe_id
        self.babe_name = babe_name
        self.babe_surname = babe_surname
        self.link = f"https://vk.com/id{babe_id}"

    def __repr__(self):
        return f"{self.babe_name} {self.babe_surname}"

    def __str__(self):
        return f"ID: {self.babe_id} {self.babe_name} {self.babe_surname} {self.link}"


def prepare_tostart_show():
    babe_for_show = Wanted(
        babe_id=babe_id, babe_name=babe_name, babe_surname=babe_surname)
    photos_to_show = get_wanted_3_photos(babe_id)

    if len(photos_to_show) >= 3:

        photo_1 = photos_to_show[0][1][1]
        photo_2 = photos_to_show[1][1][1]
        photo_3 = photos_to_show[2][1][1]

        send_message(user_id, f"{babe_for_show}", attachment=[f"photo{babe_id}_{photo_1}",
                                                              f"photo{babe_id}_{photo_2}",
                                                              f"photo{babe_id}_{photo_3}"])

    elif len(photos_to_show) == 2:
        photo_1 = photos_to_show[0][1][1]
        photo_2 = photos_to_show[1][1][1]
        send_message(user_id, f"{babe_for_show}", attachment=[f"photo{babe_id}_{photo_1}",
                                                              f"photo{babe_id}_{photo_2}"])
    elif len(photos_to_show) == 1:
        photo_1 = photos_to_show[0][1][1]
        send_message(user_id, f"{babe_for_show}",
                     attachment=f"photo{babe_id}_{photo_1}")

    else:
        send_message(
            user_id, f"{babe_for_show}, Данный кандидат не предоставил фотоальбом")
    
    

if __name__ == '__main__':
  
  """Бот крутится в цикле через кнопки 'START' 'STOP', активация после 'STOP' слово в чат 'Привет'
     Внутри цикла есть возможность остановить поиск, это кнопка 'ОТМЕНА' во время шоу кандидатов в чате пользователя.
     Выбор кандидата происходит произвольно каждый раз из новой (+-) 1000 человек, предсказать
     кто окажется им/ей невозможно. Бот крутит колесо фортуны:)))...
     Бот будет предлагать варианты пока пользователю не надоест смотреть шоу 
     или сервер VK не отключит бота.
     Бот не будет предлагать повторно то, что пользователь уже видел, для этого
     у Бота есть 2 списка: избранное для лучших и черный список для остальных...
     Новую команду 'Привет' после кнопок 'ОТМЕНА' и 'STOP' Бот определяет как нового пользователя,
     так как это перезапуск программы.
  """  
  
  while True: # Крутим бота в бесконечном цикле
      
    session_1 = vk_api.VkApi(token=configdata.setting["group_token"])
    session_2 = vk_api.VkApi(token=configdata.access_token)
    longpoll_1 = VkLongPoll(session_1, group_id=configdata.setting["group_id"])
    bot_1 = session_1.get_api()
    bot_2 = session_2.get_api()
    
    """получение ID юзера из сообщения"""
    user_id = get_current_user_id()
      
    """для работы с базой"""
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    add_current_user = User()
    add_current_user.id_user = user_id
    session.add(add_current_user)
    session.commit()
  
   
    """получение имени юзера из сообщения и запуск Бота Вконтакте"""  
    name_from_id(user_id=user_id)
    vkinder_say_hi(user_id)
  
  
    """Данные для запуска поиска через users.search"""
    get_user_data(user_id=user_id)
    city = get_city_from_data()
    bdate = get_bdate_from_data()
    user_age = get_user_age()
    sex = get_sex_from_data()
    relation = get_user_relation_data()
    send_message(user_id, f"Согласно вашему профилю, Я буду искать для Вас пару:\n"
                 f"в городе по ID: {city}, по вашей дате рождения: {bdate},\n возраст кандидатов: {user_age}\n"
                 f"противоположного пола [Мужской - ID 2, Женский - ID 1]: {sex},\n искомый статус: {relation}")
  
    """Поиск и выдача и результатов:"""
    send_message(user_id, f"Готов(а) приступить к поиску? Жми 'START' или 'STOP', если нет", keyboard=ACTIVATION_KEYBOARD)
    for event in longpoll_1.listen():
      if event.type == VkEventType.MESSAGE_NEW and event.to_me and user_id == event.user_id:
        yes_no = event.text.upper()
        break
    
    #Крутим колесо Фортуны ботом:
    if yes_no == "START":
      send_message(user_id, f"Активирую поиск....")
    
      while True:
        babe_list = execute_search()
        babe_id = choose_random_babe(babe_list)
      
        babe_name = get_random_babe_name(babe_id)
        babe_surname = get_random_babe_surname()
        get_wanted_3_photos(babe_id)
        
        q1_wanted_request = select(Wanted_user.id_wanted_user).where(
                    Wanted_user.user_id == user_id)
        q2_blacklist_request = select(Black_list.id_notwanted_user).where(
                    Black_list.user_id == user_id)
        q1_result = session.execute(q1_wanted_request)
        q2_result = session.execute(q2_blacklist_request)
        if q1_result or q2_result == True:
          prepare_tostart_show()
          send_message(user_id, f"Нравится?, жми на клавиатуре ДА либо НЕТ", keyboard=YES_OR_NO_KEYBOARD)
          for event in longpoll_1.listen():
             if event.type == VkEventType.MESSAGE_NEW and event.to_me and user_id == event.user_id:
                choice = event.text.upper()
                break
        
          if choice == "ДА":
            send_message(user_id, f"Отлично, добавляем его/ее в избранное")
            good_babe = Wanted_user()
            good_babe.id_wanted_user = babe_id
            good_babe.user_id = user_id
            
            try:
              session.add(good_babe)
              session.commit()
            except exc.IntegrityError:
              session.rollback()
              print('unique/foreign key exists')
            else:
              continue
            
          elif choice == "НЕТ":
            send_message(user_id, f"Убираем его/ее в список неудачников!")
            bad_babe = Black_list()
            bad_babe.id_notwanted_user = babe_id
            bad_babe.user_id = user_id
            
            try:
              session.add(bad_babe)
              session.commit()
            except exc.IntegrityError:
              session.rollback()
              print('unique/foreign key exists')
            else:
              continue
            
          else:
            send_message(user_id, f"Очень жаль, я ухожу из чата. Напиши привет, когда вернешься.")
            session.close_all()
            Base.metadata.drop_all(bind=engine, tables=[User.__table__, Wanted_user.__table__, Black_list.__table__])
            Base.metadata.create_all(engine)
            break         
        
        else:
          continue
    else:
      send_message(user_id, f'Очень жаль, буду рад помочь в другой раз')
      Base.metadata.drop_all(bind=engine, tables=[User.__table__, Wanted_user.__table__, Black_list.__table__])
      Base.metadata.create_all(engine)
      continue
