# Generated by Django 4.1.7 on 2023-03-27 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0010_profile_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='default.png', null=True, upload_to='media/user_profiles/'),
        ),
    ]
