# Generated by Django 4.2.5 on 2023-11-11 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filter_flag', models.CharField(choices=[('E', 'Every-Site-Visitor'), ('A', 'All-Applicants'), ('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected'), ('S', 'Specific-Applicant')], default='S', max_length=1)),
                ('content', models.CharField(max_length=40)),
                ('recipient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.application')),
            ],
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
