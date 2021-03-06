# Generated by Django 3.2.5 on 2022-02-01 13:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('english', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='english',
            name='author',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='english',
            name='category',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='english.category'),
        ),
        migrations.AlterField(
            model_name='english',
            name='created_time',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='english',
            name='key_expressions',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='english',
            name='key_words',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='english',
            name='modified_time',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='english',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='english',
            name='source',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='english.source'),
        ),
        migrations.AlterField(
            model_name='english',
            name='words_to_learn',
            field=models.TextField(blank=True),
        ),
    ]
