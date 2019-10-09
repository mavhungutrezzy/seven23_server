# Generated by Django 2.1.11 on 2019-09-26 22:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0007_auto_20190706_0359'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='social_networks',
            field=models.TextField(blank=True, verbose_name='social_networks blob'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.CharField(choices=[('NONE', 'None'), ('GRAVATAR', 'Gravatar'), ('NOMADLIST', 'Nomadlist')], default='NONE', help_text='Select between different origins.', max_length=20, verbose_name='Avatar'),
        ),
    ]