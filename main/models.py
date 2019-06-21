from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Box(models.Model):
    password = models.IntegerField(default=None, null=True)
    position_x = models.IntegerField(default=None)
    position_y = models.IntegerField(default=None)


class Room(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=255)


class Users(models.Model):
    def __str__(self):
        return self.user.username

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.IntegerField(default=-1, null=True)
    group_id = models.IntegerField(default=None)
    is_commander = models.BooleanField(default=None, null=True)
    position_x = models.IntegerField(default=None, null=True)
    position_y = models.IntegerField(default=None, null=True)
    public_key = models.TextField(default=None, null=True)
    private_key = models.TextField(default=None, null=True)
    rsa_n = models.TextField(default=None, null=True)
    mill_rand = models.TextField(default=None, null=True)
    mill_prime = models.TextField(default=None, null=True)
    vote_to = models.IntegerField(default=None, null=True)
    box_key_x = models.IntegerField(default=None, null=True)
    box_key_y = models.IntegerField(default=None, null=True)

    room = models.ForeignKey(Room, on_delete=models.CASCADE)


class SystemParam(models.Model):
    def __str__(self):
        return self.key

    key = models.CharField(max_length=255)
    intValue = models.IntegerField(default=None, null=True)
    strValue = models.CharField(max_length=255, default=None, null=True)


class Rank(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=255)
