from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0004_remove_lead_assignment_settings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lead",
            name="first_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name="lead",
            name="last_name",
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
