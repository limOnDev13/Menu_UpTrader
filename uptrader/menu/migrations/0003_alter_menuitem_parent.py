# Generated by Django 5.2.1 on 2025-05-13 16:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0002_alter_menuitem_parent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menuitem",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="menu.menuitem",
            ),
        ),
    ]
