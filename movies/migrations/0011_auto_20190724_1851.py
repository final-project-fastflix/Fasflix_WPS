# Generated by Django 2.2.3 on 2019-07-24 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0010_degree_degree_image_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='degree_path',
        ),
        migrations.AlterField(
            model_name='degree',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]