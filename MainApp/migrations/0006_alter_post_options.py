# Generated by Django 4.1.7 on 2023-03-26 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0005_post_timestamp'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-id']},
        ),
    ]
