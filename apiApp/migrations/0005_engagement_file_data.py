# Generated by Django 4.0.3 on 2022-06-20 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiApp', '0004_user_data_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='engagement_file_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('USERNAME', models.CharField(max_length=100)),
                ('FILE_NAME', models.CharField(max_length=100)),
                ('FILE_SIZE', models.BigIntegerField()),
            ],
        ),
    ]
