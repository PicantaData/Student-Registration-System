# Generated by Django 4.2.7 on 2023-11-19 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_test'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='test_end',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='test_start',
            field=models.DateTimeField(null=True),
        ),
    ]
