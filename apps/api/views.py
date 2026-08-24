from rest_framework import generics

from apps.content.models import FAQ, FAQCategory
from apps.universities.models import Program, ProgramOffering, University

from .serializers import (
    FAQCategorySerializer,
    FAQSerializer,
    ProgramOfferingSerializer,
    ProgramSerializer,
    UniversitySerializer,
)


class UniversityListAPIView(generics.ListAPIView):
    queryset = University.objects.filter(is_active=True).select_related("city")
    serializer_class = UniversitySerializer


class UniversityDetailAPIView(generics.RetrieveAPIView):
    queryset = University.objects.filter(is_active=True)
    serializer_class = UniversitySerializer
    lookup_field = "slug_en"
    lookup_url_kwarg = "slug"


class ProgramListAPIView(generics.ListAPIView):
    queryset = Program.objects.filter(is_active=True).select_related(
        "university",
        "program_language",
    )
    serializer_class = ProgramSerializer


class ProgramDetailAPIView(generics.RetrieveAPIView):
    queryset = Program.objects.filter(is_active=True)
    serializer_class = ProgramSerializer
    lookup_field = "slug_en"
    lookup_url_kwarg = "slug"


class ProgramOfferingListAPIView(generics.ListAPIView):
    queryset = ProgramOffering.objects.filter(is_active=True).select_related(
        "program",
        "academic_year",
        "semester",
    )
    serializer_class = ProgramOfferingSerializer


class FAQCategoryListAPIView(generics.ListAPIView):
    queryset = FAQCategory.objects.filter(is_active=True)
    serializer_class = FAQCategorySerializer


class FAQListAPIView(generics.ListAPIView):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
