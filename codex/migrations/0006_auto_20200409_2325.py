# Generated by Django 3.0.5 on 2020-04-09 23:25

import codex.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0005_auto_20200408_0115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='path',
            field=models.CharField(max_length=128, validators=[codex.validators.validate_dir_exists]),
        ),
    ]
