# Generated by Django 3.2.5 on 2022-02-02 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('english', '0005_auto_20220201_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='english',
            name='tag',
            field=models.ManyToManyField(null=True, related_name='notes', to='english.Tag'),
        ),
    ]
