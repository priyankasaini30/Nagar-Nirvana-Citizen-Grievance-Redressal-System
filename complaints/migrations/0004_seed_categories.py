from django.db import migrations


def seed_categories(apps, schema_editor):
    Category = apps.get_model("complaints", "Category")
    names = [
        "Electricity",
        "Water Supply",
        "Sewage",
        "Road Damage",
        "Street Light",
        "Garbage",
    ]
    for name in names:
        Category.objects.get_or_create(name=name)


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("complaints", "Category")
    names = [
        "Electricity",
        "Water Supply",
        "Sewage",
        "Road Damage",
        "Street Light",
        "Garbage",
    ]
    Category.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("complaints", "0003_alter_complaint_image_alter_complaint_status_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
