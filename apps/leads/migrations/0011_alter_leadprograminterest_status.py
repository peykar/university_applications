from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0010_lead_names_optional"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leadprograminterest",
            name="status",
            field=models.CharField(
                choices=[
                    ("suggested", "Recommended"),
                    ("interested", "Interested"),
                    ("applied", "Applied"),
                    ("shortlisted", "Shortlisted"),
                    ("declined", "Declined"),
                    ("qualified", "Qualified"),
                    ("converted", "Converted"),
                ],
                db_index=True,
                default="interested",
                max_length=24,
            ),
        ),
    ]
