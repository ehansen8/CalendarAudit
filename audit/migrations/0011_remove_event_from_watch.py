# Generated by Django 4.1.2 on 2022-10-11 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0010_alter_event_summary"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="from_watch",
        ),
    ]
