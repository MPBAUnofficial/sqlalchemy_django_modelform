from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Person(Base):
    __tablename__ = 'persone'

    pk = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    nerd = Column(Boolean)

    def __init__(self, name, age, nerd):
        self.name = name
        self.age = age
        self.nerd = nerd

    def __str__(self):
        return '{}'.format(self.name)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()