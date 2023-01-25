# Generated by Django 4.1.4 on 2023-01-16 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_user_is_admin_alter_user_is_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='uploader',
        ),
        migrations.AlterField(
            model_name='review',
            name='ticket',
            field=models.ForeignKey(blank=True,
                                    null=True,
                                    on_delete=django.
                                    db.models.
                                    deletion.SET_NULL,
                                    related_name='reviews',
                                    to='blog.ticket'),
        ),
        migrations.DeleteModel(
            name='Blog',
        ),
        migrations.DeleteModel(
            name='Photo',
        ),
    ]
