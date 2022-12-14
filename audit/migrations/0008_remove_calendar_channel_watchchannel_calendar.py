# Generated by Django 4.1.2 on 2022-10-10 23:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0007_watchchannel_calendar_channel"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="calendar",
            name="channel",
        ),
        migrations.AddField(
            model_name="watchchannel",
            name="calendar",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="channel",
                to="audit.calendar",
            ),
        ),
    ]
