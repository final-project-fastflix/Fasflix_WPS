# Generated by Django 2.2.3 on 2019-07-15 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_auto_20190715_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='synopsis',
            field=models.TextField(blank=True),
        ),
    ]
