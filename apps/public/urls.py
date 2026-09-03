from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("universities/", views.university_list, name="university-list"),
    path(
        "universities/cities/<str:slug>/",
        views.university_city_detail,
        name="university-city-detail",
    ),
    path(
        "universities/<str:slug>/",
        views.university_detail,
        name="university-detail",
    ),
    path("programs/", views.program_list, name="program-list"),
    path(
        "programs/fields/<str:slug>/",
        views.program_field_detail,
        name="program-field-detail",
    ),
    path(
        "programs/<str:slug>/",
        views.program_detail,
        name="program-detail",
    ),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
]
