# Generated by Django 4.1.7 on 2023-04-26 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bannedusers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=100)),
                ('target', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Testo',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='static/uploads/')),
                ('trust', models.BooleanField(blank=True, null=True)),
            ],
        ),
    ]