from django.contrib import admin
from .models import University, UniversityMedia, Department, ProgramLanguage, AcademicYear, Semester, Program, ProgramOffering
admin.site.register([University, UniversityMedia, Department, ProgramLanguage, AcademicYear, Semester, Program, ProgramOffering])
