# Generated by Django 4.1.2 on 2022-10-11 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0008_remove_calendar_channel_watchchannel_calendar"),
    ]

    operations = [
        migrations.AddField(
            model_name="calendar",
            name="sync_token",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
