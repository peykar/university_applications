from django.db import migrations, models

import apps.leads.models


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leadmessageattachment",
            name="file",
            field=models.FileField(
                max_length=500,
                upload_to=apps.leads.models.lead_message_attachment_upload_path,
            ),
        ),
    ]
