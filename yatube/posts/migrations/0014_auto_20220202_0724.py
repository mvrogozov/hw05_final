# Generated by Django 2.2.16 on 2022-02-02 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20220202_0719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
    ]
