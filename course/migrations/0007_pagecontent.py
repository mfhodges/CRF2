# Generated by Django 2.1.5 on 2019-06-21 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_auto_20190619_2148'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=100)),
                ('markdown_text', models.TextField(max_length=4000)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]