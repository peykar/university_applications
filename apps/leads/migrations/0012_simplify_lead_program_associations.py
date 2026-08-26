from django.db import migrations, models


def map_system_source_to_agent(apps, schema_editor):
    LeadProgramInterest = apps.get_model("leads", "LeadProgramInterest")
    LeadProgramInterest.objects.filter(source="system").update(source="agent")


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0011_alter_leadprograminterest_status"),
    ]

    operations = [
        migrations.RunPython(
            map_system_source_to_agent,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="leadprograminterest",
            name="status",
        ),
        migrations.RemoveField(
            model_name="leadprograminterest",
            name="user_responded_at",
        ),
        migrations.AlterField(
            model_name="leadprograminterest",
            name="source",
            field=models.CharField(
                choices=[
                    ("user", "User-added"),
                    ("agent", "Agent-suggested"),
                ],
                default="user",
                max_length=16,
            ),
        ),
    ]
