# Generated by Django 3.1 on 2020-04-22 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0031_auto_20200422_0358'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comic',
            old_name='folders',
            new_name='folder',
        ),
    ]
