# Generated by Django 4.2.3 on 2023-08-11 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_business_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drug',
            name='drug_image',
        ),
        migrations.AddField(
            model_name='drug',
            name='images',
            field=models.JSONField(default=dict),
        ),
        migrations.DeleteModel(
            name='Images',
        ),
    ]