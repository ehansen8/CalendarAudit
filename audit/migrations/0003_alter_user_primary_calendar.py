# Generated by Django 4.1.2 on 2022-10-06 23:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0002_alter_event_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="primary_calendar",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="audit.calendar",
            ),
        ),
    ]
