from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Box(models.Model):
    password = models.CharField(max_length=255)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)


class Room(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=255)


class Users(models.Model):
    def __str__(self):
        return self.user.username

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)
    group_id = models.IntegerField(default=0)
    is_commander = models.BooleanField(default=False)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    public_key = models.TextField(default='')
    private_key = models.TextField(default='')
    rsa_n = models.TextField(default='')
    mill_rand = models.TextField(default='')
    mill_prime = models.TextField(default='')
    vote_to = models.IntegerField(default=0)

    room = models.ForeignKey(Room, on_delete=models.CASCADE)


class SystemParam(models.Model):
    def __str__(self):
        return self.key

    key = models.CharField(max_length=255)
    intValue = models.IntegerField(default=0)
    strValue = models.CharField(max_length=255)

class Rank(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=255)
