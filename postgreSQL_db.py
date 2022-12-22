import configdata
import psycopg2
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship



"""
База данных postgres для хранения ID users - Vkinder
Table User - хранит ID пользователя Бота.
Table Wanted_users - содержит избранный список ID пользователей, которых выбрал пользователь Бота.
Table Blacklisted - черный список ID пользователей, которых не выбрал пользователь Бота.
Посмотреть данные в базе можно в процессе активной работы Бота, то-есть:
После нажатия кнопки 'START', добавления первых кандидатов в базу и до нажатия кнопок 
'STOP' 'ОТМЕНА', так как после Бот стирает данные, чтобы подготовить
базу для нового пользователя(активация 'Привет' после стоп, отмена)
"""

engine = create_engine("postgresql://postgres:" + configdata.postgres_password + "@localhost:5432/vkinder", echo=True)
Base = declarative_base()    
    
class User(Base):
    __tablename__ = 'Users'

    id_user = Column(Integer, primary_key=True)
    

class Wanted_user(Base):
    __tablename__ = 'Wanted_users'

    id_wanted_user = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id_user'))
    user = relationship("User")
    

class Black_list(Base):
    __tablename__ = 'Blacklisted'
  
    id_notwanted_user = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id_user'))
    user = relationship("User")


Base.metadata.drop_all(bind=engine, tables=[User.__table__, Wanted_user.__table__, Black_list.__table__])
Base.metadata.create_all(engine)  