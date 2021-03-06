# Generated by Django 3.2.5 on 2022-02-10 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('english', '0014_english_audio_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, null=True)),
                ('abstract', models.TextField(null=True)),
                ('summary', models.TextField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='english',
            name='summary',
            field=models.ManyToManyField(null=True, related_name='summary_notes', to='english.Tag'),
        ),
    ]
