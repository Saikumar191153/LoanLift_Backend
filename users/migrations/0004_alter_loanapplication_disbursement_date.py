# Generated by Django 5.1.5 on 2025-01-18 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_loanapplication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanapplication',
            name='disbursement_date',
            field=models.DateField(null=True),
        ),
    ]
