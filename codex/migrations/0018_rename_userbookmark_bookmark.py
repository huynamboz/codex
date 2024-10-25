"""Generated by Django 4.1 on 2022-08-24 01:49."""

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Rename Bookmark table & use '' for CharField nulls."""

    dependencies = [
        ("sessions", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("codex", "0017_alter_timestamp_options_alter_adminflag_name_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="UserBookmark", old_name="bookmark", new_name="page"
        ),
        migrations.RenameModel(
            old_name="UserBookmark",
            new_name="Bookmark",
        ),
        migrations.AlterField(
            model_name="bookmark",
            name="fit_to",
            field=models.CharField(
                blank=True,
                default="",
                max_length=6,
                # Code dependent validators removed in the future
            ),
        ),
        migrations.AlterField(
            model_name="comic",
            name="age_rating",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="comic",
            name="country",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="comic",
            name="format",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="comic",
            name="language",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="comic",
            name="scan_info",
            field=models.CharField(default="", max_length=128),
        ),
        migrations.AlterField(
            model_name="comic",
            name="web",
            field=models.URLField(default=""),
        ),
        migrations.AlterField(
            model_name="timestamp",
            name="version",
            field=models.CharField(default="", max_length=32),
        ),
    ]
