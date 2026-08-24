from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.applications.models import Application
from apps.content.models import FAQ, FAQCategory
from apps.students.models import Student
from apps.universities.models import Department, Program, University

from .forms import ContactForm, StudentProfileForm


def home(request):
    search_query = request.GET.get("q", "").strip()
    if search_query:
        return redirect(f"{reverse('program-list')}?q={search_query}")

    active_universities = University.objects.filter(is_active=True)
    active_programs = Program.objects.filter(is_active=True)
    active_faqs = FAQ.objects.filter(is_active=True)

    featured_universities = (
        active_universities.select_related("city")
        .annotate(
            active_program_count=Count(
                "programs",
                filter=Q(programs__is_active=True),
            )
        )
        .order_by("-is_featured", "-listing_priority", "name_en")[:8]
    )

    popular_programs = (
        active_programs.select_related(
            "university",
            "program_language",
            "department",
        )
        .prefetch_related("offerings")
        .annotate(
            min_tuition=Min(
                "offerings__tuition",
                filter=Q(offerings__is_active=True),
            )
        )
        .order_by("-listing_priority", "name_en")[:8]
    )

    study_fields = (
        Department.objects.filter(
            is_active=True,
            programs__is_active=True,
        )
        .annotate(
            program_count=Count(
                "programs",
                filter=Q(programs__is_active=True),
            )
        )
        .order_by("-program_count", "name_en")[:10]
    )

    faq_preview = (
        active_faqs.select_related("category")
        .order_by("category__sort_order", "sort_order", "question_en")[:6]
    )

    hero_university = (
        active_universities.exclude(banner="")
        .order_by("-is_featured", "-listing_priority")
        .first()
    )

    return render(
        request,
        "public/home.html",
        {
            "featured_universities": featured_universities,
            "popular_programs": popular_programs,
            "study_fields": study_fields,
            "faq_preview": faq_preview,
            "hero_university": hero_university,
            "university_count": active_universities.count(),
            "program_count": active_programs.count(),
            "faq_count": active_faqs.count(),
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
            | Q(department__name_en__icontains=query)
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
