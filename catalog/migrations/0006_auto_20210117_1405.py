# Generated by Django 3.1.5 on 2021-01-18 00:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_auto_20210117_1344'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back'], 'permissions': (('can_view_all_loaned', 'View books on loan'),)},
        ),
    ]
