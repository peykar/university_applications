from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0003_lead_assignment_settings"),
    ]

    operations = [
        migrations.DeleteModel(
            name="LeadAssignmentSettings",
        ),
    ]
