# Generated by Django 5.2 on 2025-05-08 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pet_care_app', '0005_sitepartner_partner_type_sitepartner_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sitepartner',
            name='location',
        ),
    ]
