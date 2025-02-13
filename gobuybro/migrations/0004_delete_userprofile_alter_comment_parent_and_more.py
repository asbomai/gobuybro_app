# Generated by Django 5.1.4 on 2025-02-12 10:13

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gobuybro', '0003_alter_post_video_alter_postimage_image_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
        migrations.AlterField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='gobuybro.comment'),
        ),
        migrations.AlterField(
            model_name='post',
            name='video',
            field=models.FileField(upload_to='videos/'),
        ),
        migrations.AlterField(
            model_name='postimage',
            name='image',
            field=models.ImageField(upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='business_address',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='business_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=17, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_photo',
            field=models.ImageField(default='profile_photos/p-image.png', upload_to='profile_photos/'),
        ),
    ]
