from django import forms

from apps.applications.models import Application
from apps.content.models import ContactSubmission
from apps.students.models import Student


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ("name", "email", "phone", "subject", "message")


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = (
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "birthdate",
            "nationality",
            "country_of_birth",
            "email",
            "cell",
            "country_of_residence",
            "city_of_residence",
            "address",
        )


class ApplicationNoteForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("notes",)
