# Generated by Django 5.0.7 on 2024-07-22 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_products_bidding_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='description',
            field=models.CharField(blank=True, default='', max_length=2500, null=True),
        ),
    ]
