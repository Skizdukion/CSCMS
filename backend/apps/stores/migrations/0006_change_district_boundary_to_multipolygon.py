# Generated by Django 4.2.7 on 2025-06-29 15:18

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0005_remove_inventory_stores_inve_quantit_d2778a_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='boundary',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, help_text='Geographic boundary of the district (can contain multiple polygons)', null=True, srid=4326),
        ),
    ]
