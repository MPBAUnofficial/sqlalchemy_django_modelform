from django.db import models
from django.db.models import CharField, IntegerField, BooleanField


class Person(models.Model):
    name = CharField(max_length=100)
    age = IntegerField()
    nerd = BooleanField()

    def __str__(self):
        return '{} - {} YO - nerd: {}'.format(self.name, self.age, self.nerd)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()