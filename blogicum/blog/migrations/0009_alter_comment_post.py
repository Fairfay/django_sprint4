# Generated by Django 3.2.16 on 2023-11-11 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='Post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='blog.post'),
        ),
    ]
