from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField


class Athlete(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    city = models.CharField(max_length=100)
    sex = models.CharField(max_length=5)
    type = models.CharField(max_length=50)
    email = models.EmailField()

    @classmethod
    def create(cls, ath):
      return cls(id=ath.id, city=ath.city, sex=ath.sex, type=ath.athlete_type, email=ath.email)


class Activity(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    athlete = models.ForeignKey('Athlete', on_delete=models.CASCADE)
    commute = models.BooleanField()
    stream = ArrayField(ArrayField(models.FloatField(), size=2))

    @classmethod
    def create(cls, act, ath, strm):
      return cls(id=act.id, athlete=ath, commute=act.commute, stream=strm)
