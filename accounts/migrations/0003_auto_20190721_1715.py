# Generated by Django 2.2.3 on 2019-07-21 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20190719_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subuser',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
