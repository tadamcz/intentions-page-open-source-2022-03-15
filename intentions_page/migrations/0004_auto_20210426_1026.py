# Generated by Django 3.1.8 on 2021-04-26 09:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('intentions_page', '0003_auto_20210426_1006'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='intention',
            options={'ordering': ['-created_datetime']},
        ),
        migrations.AddField(
            model_name='intention',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
