from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.applications.models import Application
from apps.content.models import FAQCategory
from apps.students.models import Student
from apps.universities.models import Program, University

from .forms import ContactForm, StudentProfileForm


def home(request):
    universities = University.objects.filter(is_active=True).order_by(
        "-listing_priority",
        "name_en",
    )[:8]
    programs = Program.objects.filter(is_active=True).select_related(
        "university",
        "program_language",
    ).order_by("-listing_priority", "name_en")[:12]
    return render(
        request,
        "public/home.html",
        {
            "universities": universities,
            "programs": programs,
        },
    )


def university_list(request):
    query = request.GET.get("q", "").strip()
    qs = University.objects.filter(is_active=True).select_related(
        "city",
        "city__province",
        "city__province__country",
    )
    if query:
        qs = qs.filter(
            Q(name_en__icontains=query)
            | Q(name_fa__icontains=query)
            | Q(name_tr__icontains=query)
            | Q(name_ar__icontains=query)
        )
    return render(
        request,
        "public/university_list.html",
        {"universities": qs.order_by("-listing_priority", "name_en")},
    )


def university_detail(request, slug):
    university = get_object_or_404(
        University.objects.prefetch_related(
            "programs",
            "media",
        ),
        slug_en=slug,
        is_active=True,
    )
    return render(
        request,
        "public/university_detail.html",
        {"university": university},
    )


def program_list(request):
    query = request.GET.get("q", "").strip()
    qs = Program.objects.filter(is_active=True).select_related(
        "university",
        "department",
        "program_language",
    )
    if query:
        qs = qs.filter(
            Q(name_en__icontains=query)
            | Q(name_fa__icontains=query)
            | Q(name_tr__icontains=query)
            | Q(name_ar__icontains=query)
            | Q(university__name_en__icontains=query)
        )
    return render(
        request,
        "public/program_list.html",
        {"programs": qs.order_by("-listing_priority", "name_en")},
    )


def program_detail(request, slug):
    program = get_object_or_404(
        Program.objects.select_related(
            "university",
            "department",
            "program_language",
        ).prefetch_related("offerings"),
        slug_en=slug,
        is_active=True,
    )
    return render(
        request,
        "public/program_detail.html",
        {"program": program},
    )


def faq(request):
    categories = FAQCategory.objects.filter(is_active=True).prefetch_related(
        "faqs"
    )
    return render(
        request,
        "public/faq.html",
        {"categories": categories},
    )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent.")
            return redirect("contact")
    else:
        form = ContactForm()

    return render(
        request,
        "public/contact.html",
        {"form": form},
    )


def about(request):
    return render(request, "public/about.html")


@login_required
def dashboard(request):
    student = Student.objects.filter(user=request.user).first()
    applications = (
        Application.objects.filter(student=student)
        .select_related(
            "program_offering__program__university",
            "program_offering__academic_year",
            "program_offering__semester",
        )
        if student
        else Application.objects.none()
    )
    return render(
        request,
        "public/dashboard.html",
        {
            "student": student,
            "applications": applications,
        },
    )


@login_required
def profile(request):
    student = Student.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = StudentProfileForm(instance=student)

    return render(
        request,
        "public/profile.html",
        {"form": form},
    )
