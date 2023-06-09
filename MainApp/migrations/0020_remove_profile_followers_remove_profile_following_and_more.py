# Generated by Django 4.1.7 on 2023-05-02 21:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MainApp', '0019_post_dislikes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='followers',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='following',
        ),
        migrations.CreateModel(
            name='FollowersCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.ManyToManyField(related_name='followed', to=settings.AUTH_USER_MODEL)),
                ('user', models.ManyToManyField(related_name='who_is_following', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
