# Generated by Django 3.1 on 2020-04-19 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0016_auto_20200416_0023'),
    ]

    operations = [
        migrations.AddField(
            model_name='comic',
            name='cover_path',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
