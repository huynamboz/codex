# Generated by Django 3.1 on 2020-04-19 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0020_auto_20200419_0705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comic',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='comic',
            name='title',
        ),
        migrations.RemoveField(
            model_name='folder',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='imprint',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='series',
            name='display_name',
        ),
        migrations.AlterField(
            model_name='imprint',
            name='name',
            field=models.CharField(default='Main Imprint', max_length=32),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='name',
            field=models.CharField(default='No Publisher', max_length=32),
        ),
        migrations.AlterField(
            model_name='series',
            name='name',
            field=models.CharField(default='Default Series', max_length=32),
        ),
        migrations.AlterField(
            model_name='volume',
            name='name',
            field=models.CharField(default='', max_length=32),
        ),
    ]
