# Generated by Django 2.2.16 on 2022-02-14 05:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0023_auto_20220211_0654'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='user_not_author',
        ),
    ]