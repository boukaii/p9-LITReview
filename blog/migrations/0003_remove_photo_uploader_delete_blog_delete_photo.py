# Generated by Django 4.1.4 on 2022-12-19 21:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_photo_blog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='uploader',
        ),
        migrations.DeleteModel(
            name='Blog',
        ),
        migrations.DeleteModel(
            name='Photo',
        ),
    ]