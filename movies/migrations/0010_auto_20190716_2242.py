# Generated by Django 2.2.3 on 2019-07-16 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0009_auto_20190716_2241'),
    ]

    operations = [
        migrations.RenameField(
            model_name='moviecontinue',
            old_name='movie',
            new_name='movie_id',
        ),
    ]