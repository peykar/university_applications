from django.urls import path

from .views import (
    FAQCategoryListAPIView,
    FAQListAPIView,
    ProgramDetailAPIView,
    ProgramListAPIView,
    ProgramOfferingListAPIView,
    UniversityDetailAPIView,
    UniversityListAPIView,
)

urlpatterns = [
    path("universities/", UniversityListAPIView.as_view()),
    path("universities/<str:slug>/", UniversityDetailAPIView.as_view()),
    path("programs/", ProgramListAPIView.as_view()),
    path("programs/<str:slug>/", ProgramDetailAPIView.as_view()),
    path("offerings/", ProgramOfferingListAPIView.as_view()),
    path("faq-categories/", FAQCategoryListAPIView.as_view()),
    path("faqs/", FAQListAPIView.as_view()),
]
