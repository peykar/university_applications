from django.contrib import admin
from .models import FAQCategory, FAQ, ContactSubmission
admin.site.register([FAQCategory, FAQ, ContactSubmission])
