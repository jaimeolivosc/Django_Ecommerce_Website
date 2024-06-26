# Generated by Django 5.0.3 on 2024-04-11 20:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_modified', models.DateTimeField(auto_now=True)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('address', models.CharField(blank=True, max_length=150)),
                ('additional_address', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('region', models.CharField(blank=True, max_length=100)),
                ('zip_code', models.CharField(blank=True, max_length=15)),
                ('country', models.CharField(blank=True, max_length=15)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
