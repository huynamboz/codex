# Generated by Django 3.0.5 on 2020-04-10 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0006_auto_20200409_2325'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('name', models.CharField(max_length=32)),
                ('on', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
                'unique_together': {('name',)},
            },
        ),
    ]
