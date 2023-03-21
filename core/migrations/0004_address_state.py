# Generated by Django 2.2.14 on 2023-03-20 02:55

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_address_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='state',
            field=localflavor.us.models.USStateField(default='None', max_length=2),
            preserve_default=False,
        ),
    ]
