# Generated by Django 4.2.3 on 2023-08-17 03:19

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='drug',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True),
        ),
    ]
