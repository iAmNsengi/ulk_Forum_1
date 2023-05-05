from django.db import models
from django.contrib.auth.models import User
from froala_editor.fields import FroalaField


# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=128)
    admin = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    key = models.CharField(max_length=40, null=True, blank=True)
    online = models.ManyToManyField(to=User, blank=True, related_name='online_users')
    members = models.ManyToManyField(to=User, blank=True, related_name='group_members')


    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f'{self.name} ({self.get_online_count()})'


class Message(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    content = FroalaField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content} [{self.timestamp}]'
