# Generated by Django 3.0.8 on 2020-07-05 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saas', '0005_auto_20200523_0908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='stripe_session_id',
            field=models.CharField(help_text='Generated by Stripe API', max_length=128, verbose_name='Stripe session id'),
        ),
    ]
