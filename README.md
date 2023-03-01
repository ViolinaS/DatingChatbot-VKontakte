# Чат Бот для знакомств в Vkontakte
![Python](https://img.shields.io/badge/PYTHON-3.8.6-yellow/?style=for-the-badge&color=9cf&logo=python&labelColor=brown) ![vkapi](https://img.shields.io/badge/Vkontakte-VkAPI-informational/?style=for-the-badge&color=informational&logo=vkontakte) ![Postgres](https://img.shields.io/badge/Database-PostgreSQL-orange/?style=for-the-badge&color=red&logo=postgresql&labelColor=black&link=https://www.postgresql.org) ![alchemy](https://img.shields.io/badge/-SQLALCHEMY-yellowgreen/?style=for-the-badge&color=darkslategrey&logo=python)
## Dating Chat Bot for Vkontakte social network
### Задачи которые выполняет Бот:
1. Ищет людей, подходящих под условия, на основании информации о пользователе из VK:

* Возраст, пол, город, семейное положение.

*  Если информации недостаточно Бот дополнительно уточнит её у пользователя.

2. У тех людей, которые подошли по требованиям пользователю на основании профиля и запрошенных данных, получает топ-3 популярных фотографии профиля и отправляет их пользователю в чат вместе со ссылкой на найденного человека. Популярность определяется по количеству лайков к фото.

3. Добавляет человека в избранный список, используя БД PostgreSQL.

4. Добавляет человека в черный список используя БД PostgreSQL.

5. Люди не повторяюся при повторном поиске.

--------
### Для работы Бота в чате в Vkontakte Вам понадобится:
1. Сообщество, от имени которого ваш бот будет общаться с пользователями ВКонтакте. 
2. Токен сообщества 
3. Токен пользователя


### Активация Бота:
1. Заполнить в файле [configdata](https://github.com/ViolinaS/VkAPI-DatingChatbot/blob/main/configdata.py): access_token(токен пользователя), postgres_password, group_id(идентификатор сообщества), group_token(токен сообщества)
2. Корректно указать путь к базе PostgreSQL, где будут созданы таблицы для работы Бота:

* *заменить название базы на свою в файле [PostgreSQL](https://github.com/ViolinaS/VkAPI-DatingChatbot/blob/main/postgreSQL_db.py)*

3. Установить недостающие библиотеки - [requirements](https://github.com/ViolinaS/VkAPI-DatingChatbot/blob/main/requirements.txt)

3. Бот активируется словом "Привет" в чате ВКонтакте.
