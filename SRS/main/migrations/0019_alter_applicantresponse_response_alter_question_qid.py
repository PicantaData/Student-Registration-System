# Generated by Django 4.2.7 on 2023-11-19 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_alter_application_id_proof_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicantresponse',
            name='response',
            field=models.CharField(blank=True, choices=[('1', 'op1'), ('2', 'op2'), ('3', 'op3'), ('4', 'op4')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='qid',
            field=models.IntegerField(primary_key=True, serialize=False, unique=True),
        ),
    ]