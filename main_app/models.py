from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

# Create your models here.


class Art(models.Model):
    name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('art_detail', kwargs={'art_id': self.id})


class Photo(models.Model):
    url = models.CharField(max_length=200)
    art = models.ForeignKey(Art, on_delete=models.CASCADE)