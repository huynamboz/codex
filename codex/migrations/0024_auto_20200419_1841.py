# Generated by Django 3.1 on 2020-04-19 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0023_auto_20200419_1839'),
    ]

    operations = [
        migrations.RenameField(
            model_name='volume',
            old_name='volume_count',
            new_name='issue_count',
        ),
    ]
