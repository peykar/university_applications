from django.contrib import admin
from .models import Student, StudentDocument
admin.site.register([Student, StudentDocument])
