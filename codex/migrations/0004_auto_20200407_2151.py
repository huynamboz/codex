# Generated by Django 3.0.5 on 2020-04-07 21:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0003_auto_20200407_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comic',
            name='parent_folder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='codex.Folder'),
        ),
    ]
