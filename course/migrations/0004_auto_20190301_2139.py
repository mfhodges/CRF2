# Generated by Django 2.1.5 on 2019-03-01 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20190301_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='masquerade',
            field=models.CharField(default=None, max_length=20),
        ),
    ]