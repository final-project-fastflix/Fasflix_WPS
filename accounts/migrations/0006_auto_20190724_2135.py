# Generated by Django 2.2.3 on 2019-07-24 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profileimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profileimage',
            name='category',
        ),
        migrations.RemoveField(
            model_name='profileimage',
            name='image_path',
        ),
    ]
