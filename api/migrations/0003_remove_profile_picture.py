# Generated by Django 5.1.7 on 2025-03-25 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_profile_picture_alter_profile_phone_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='picture',
        ),
    ]
