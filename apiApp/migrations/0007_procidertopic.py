# Generated by Django 4.0.3 on 2022-07-11 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiApp', '0006_everside_nps_polarity_score_everside_nps_topic'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProciderTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PROVIDER_NAME', models.CharField(max_length=100)),
                ('POSITIVE_TOPIC', models.CharField(max_length=100)),
                ('NEGATIVE_TOPIC', models.CharField(max_length=100)),
            ],
        ),
    ]
