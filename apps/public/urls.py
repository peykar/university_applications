from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("universities/", views.university_list, name="university-list"),
    path(
        "universities/<str:slug>/",
        views.university_detail,
        name="university-detail",
    ),
    path("programs/", views.program_list, name="program-list"),
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
