from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_review_status(apps, schema_editor):
    LeadDocument = apps.get_model("leads", "LeadDocument")
    LeadDocument.objects.filter(is_verified=True).update(review_status="approved")
    LeadDocument.objects.filter(is_verified=False).update(review_status="pending")


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0012_simplify_lead_program_associations"),
    ]

    operations = [
        migrations.AddField(
            model_name="leaddocument",
            name="review_status",
            field=models.CharField(
                choices=[
                    ("pending", "Needs review"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                db_index=True,
                default="pending",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="leaddocument",
            name="review_note",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="leaddocument",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="leaddocument",
            name="reviewed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="leaddocument",
            name="source_message_attachment",
            field=models.OneToOneField(
                blank=True,
                help_text="Chat attachment this document was promoted from, when applicable.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="promoted_document",
                to="leads.leadmessageattachment",
            ),
        ),
        migrations.RunPython(
            backfill_review_status,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="leadactivity",
            name="activity_type",
            field=models.CharField(
                choices=[
                    ("created", "Created"),
                    ("note", "Note"),
                    ("status_changed", "Status changed"),
                    ("document_uploaded", "Document uploaded"),
                    ("document_reviewed", "Document reviewed"),
                    ("program_added", "Program added"),
                    ("program_suggested", "Program suggested"),
                    ("program_response", "Program response"),
                    ("recommendations_generated", "Recommendations generated"),
                    ("finalized", "Finalized"),
                    ("converted", "Converted"),
                ],
                max_length=40,
            ),
        ),
    ]
