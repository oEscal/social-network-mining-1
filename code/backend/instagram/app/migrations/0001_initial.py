# Generated by Django 2.1.7 on 2019-03-12 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('total_score', models.IntegerField()),
                ('total_voted', models.IntegerField()),
            ],
        ),
    ]