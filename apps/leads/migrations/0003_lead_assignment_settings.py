from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("agents", "0001_initial"),
        ("leads", "0002_expand_message_attachment_file_path"),
    ]

    operations = [
        migrations.CreateModel(
            name="LeadAssignmentSettings",
            fields=[
                (
                    "id",
                    models.PositiveSmallIntegerField(
                        default=1,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "default_agent",
                    models.ForeignKey(
                        blank=True,
                        help_text=(
                            "Automatically assign newly created leads to this "
                            "agent when no agent was explicitly selected."
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="agents.agent",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lead assignment settings",
                "verbose_name_plural": "Lead assignment settings",
            },
        ),
    ]
