# Generated by Django 3.2 on 2021-06-22 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='thresh',
            field=models.IntegerField(default=100),
        ),
    ]