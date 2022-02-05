# Generated by Django 2.2.16 on 2022-02-04 08:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20220204_0819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='author',
            field=models.ManyToManyField(help_text='Подписан на', related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Подписан на'),
        ),
    ]