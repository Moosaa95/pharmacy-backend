# Generated by Django 4.2.3 on 2023-08-14 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_drug_is_prescription_needed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='prescription',
        ),
        migrations.AlterField(
            model_name='order',
            name='cart',
            field=models.JSONField(blank=True, null=True),
        ),
    ]