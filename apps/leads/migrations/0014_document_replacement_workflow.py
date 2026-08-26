import uuid

from django.conf import settings
from django.db import migrations, models
from apps.leads.models import lead_document_version_upload_path
import django.db.models.deletion


def rename_rejected_status(apps, schema_editor):
    LeadDocument = apps.get_model("leads", "LeadDocument")
    LeadDocument.objects.filter(review_status="rejected").update(
        review_status="replacement_requested"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0013_leaddocument_review_workflow"),
    ]

    operations = [
        migrations.RunPython(
            rename_rejected_status,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="leaddocument",
            name="review_status",
            field=models.CharField(
                choices=[
                    ("pending", "Needs review"),
                    ("approved", "Approved"),
                    ("replacement_requested", "Replacement requested"),
                ],
                db_index=True,
                default="pending",
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="LeadDocumentReviewHistory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("review_status", models.CharField(
                    choices=[
                        ("pending", "Needs review"),
                        ("approved", "Approved"),
                        ("replacement_requested", "Replacement requested"),
                    ],
                    max_length=32,
                )),
                ("review_note", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField()),
                ("document", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="review_history",
                    to="leads.leaddocument",
                )),
                ("reviewed_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("created_by", models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("updated_by", models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ("-reviewed_at", "-created_at")},
        ),
        migrations.CreateModel(
            name="LeadDocumentVersion",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file", models.FileField(
                    max_length=500,
                    upload_to=lead_document_version_upload_path,
                )),
                ("original_name", models.CharField(blank=True, max_length=255)),
                ("review_status", models.CharField(
                    choices=[
                        ("pending", "Needs review"),
                        ("approved", "Approved"),
                        ("replacement_requested", "Replacement requested"),
                    ],
                    max_length=32,
                )),
                ("review_note", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("document", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="versions",
                    to="leads.leaddocument",
                )),
                ("reviewed_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("created_by", models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("updated_by", models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
