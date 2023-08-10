from django.db import models
from django.contrib.auth import get_user_model
import uuid


User = get_user_model()

class Stock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    ticker = models.CharField(max_length=5)
    follows = models.IntegerField(default=0)

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile-images', default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)
    followed_stocks = models.ManyToManyField(Stock, blank=True)

    def __str__(self):
        return self.user.username

class FollowChart(models.Model):
    chart_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.username






