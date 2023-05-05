from django.db import models
from django.contrib.auth.models import User
from froala_editor.fields import FroalaField


# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    dob = models.CharField(max_length=200, blank=True, null=True)
    sex = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(
        upload_to="media/user_profiles/", default="default.png", null=True
    )

    class Meta:
        ordering = ["-id"]


class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="comment_likes")
    comment = FroalaField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]


class Post(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = FroalaField(theme="dark")
    likes = models.ManyToManyField(User, related_name="likes")
    dislikes = models.ManyToManyField(User, related_name="dislikes")
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField(Comment, related_name="post_comments")

    class Meta:
        ordering = ["-id"]
