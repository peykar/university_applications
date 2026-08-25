from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Min, Prefetch, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.applications.models import Application
from apps.content.models import FAQ, FAQCategory
from apps.geography.models import City
from apps.students.models import Student
from apps.universities.models import (
    AcademicYear,
    Currency,
    DegreeType,
    Department,
    Program,
    ProgramLanguage,
    ProgramOffering,
    Semester,
    University,
    UniversityMedia,
    UniversityType,
)

from .forms import ContactForm
from .services.program_filters import (
    annotate_min_active_tuition,
    apply_program_filters,
    read_program_filters,
)


def _program_filter_options(*, university=None):
    base_programs = Program.objects.filter(is_active=True)
    departments = Department.objects.filter(
        is_active=True,
        programs__is_active=True,
    )

    if university is not None:
        base_programs = base_programs.filter(university=university)
        departments = departments.filter(university=university)

    return {
        "degree_choices": DegreeType.choices,
        "language_choices": ProgramLanguage.objects.filter(
            is_active=True,
            programs__in=base_programs,
        )
        .distinct()
        .order_by("name_en"),
        "field_choices": (departments.exclude(slug_en="").order_by("name_en").distinct()),
        "academic_year_choices": AcademicYear.objects.filter(
            is_active=True,
            program_offerings__program__in=base_programs,
        )
        .distinct()
        .order_by("name_en"),
        "semester_choices": Semester.objects.filter(
            is_active=True,
            program_offerings__program__in=base_programs,
        )
        .distinct()
        .order_by("name_en"),
        "currency_choices": Currency.choices,
    }


def home(request):
    # The homepage exposes a compact filter set and sends users to the full
    # catalogue. Any supplied programme-search parameter triggers the redirect.
    forwarded_keys = ("q", "field", "degree", "language", "city")
    if any((request.GET.get(key) or "").strip() for key in forwarded_keys):
        params = {
            key: request.GET.get(key)
            for key in forwarded_keys
            if (request.GET.get(key) or "").strip()
        }
        return redirect(f"{reverse('program-list')}?{urlencode(params)}")

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
        .values("name_en", "slug_en")
        .annotate(program_count=Count("programs", distinct=True))
        .exclude(name_en="")
        .order_by("-program_count", "name_en")[:10]
    )

    faq_preview = active_faqs.select_related("category").order_by(
        "category__sort_order", "sort_order", "question_en"
    )[:6]

    hero_university = (
        active_universities.exclude(banner="").order_by("-is_featured", "-listing_priority").first()
    )

    filter_options = _program_filter_options()
    filter_options["city_choices"] = (
        City.objects.filter(
            is_active=True,
            universities__programs__is_active=True,
        )
        .distinct()
        .order_by("name_en")
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
            **filter_options,
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
        University.objects.select_related("city"),
        slug_en=slug,
        is_active=True,
    )

    state = read_program_filters(request.GET)
    programs = (
        Program.objects.filter(
            university=university,
            is_active=True,
        )
        .select_related(
            "university",
            "department",
            "program_language",
        )
        .prefetch_related("offerings")
    )

    programs = apply_program_filters(programs, state).order_by(
        "-listing_priority",
        "name_en",
    )

    paginator = Paginator(programs, 24)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "public/university_detail.html",
        {
            "university": university,
            "programs": page_obj.object_list,
            "page_obj": page_obj,
            "program_result_count": paginator.count,
            "filters": state,
            "query_without_page": query_params.urlencode(),
            **_program_filter_options(university=university),
        },
    )


def _build_active_program_filters(request, options) -> list[dict[str, str]]:
    """Create removable chips for active program filters."""
    chips: list[dict[str, str]] = []

    def add(name: str, label) -> None:
        if not request.GET.get(name) or not label:
            return
        params = request.GET.copy()
        params.pop(name, None)
        params.pop("page", None)
        query = params.urlencode()
        chips.append(
            {
                "name": name,
                "label": str(label),
                "remove_url": f"{request.path}?{query}" if query else request.path,
            }
        )

    add("q", request.GET.get("q"))

    field = next(
        (
            item
            for item in options.get("field_choices", [])
            if item.slug_en == request.GET.get("field")
        ),
        None,
    )
    add("field", getattr(field, "name_en", None))

    degree_value = request.GET.get("degree")
    add(
        "degree",
        next(
            (label for value, label in options.get("degree_choices", []) if value == degree_value),
            None,
        ),
    )

    language = next(
        (
            item
            for item in options.get("language_choices", [])
            if item.slug_en == request.GET.get("language")
        ),
        None,
    )
    add("language", getattr(language, "name_en", None))

    university = next(
        (
            item
            for item in options.get("university_choices", [])
            if item.slug_en == request.GET.get("university")
        ),
        None,
    )
    add("university", getattr(university, "name_en", None))

    city = next(
        (
            item
            for item in options.get("city_choices", [])
            if item.slug_en == request.GET.get("city")
        ),
        None,
    )
    add("city", getattr(city, "name_en", None))

    university_type_value = request.GET.get("university_type")
    add(
        "university_type",
        next(
            (
                label
                for value, label in options.get("university_type_choices", [])
                if value == university_type_value
            ),
            None,
        ),
    )

    tuition_min = request.GET.get("tuition_min")
    if tuition_min:
        add("tuition_min", _("From %(amount)s") % {"amount": tuition_min})

    tuition_max = request.GET.get("tuition_max")
    if tuition_max:
        add("tuition_max", _("Up to %(amount)s") % {"amount": tuition_max})

    add("currency", request.GET.get("currency"))

    academic_year = next(
        (
            item
            for item in options.get("academic_year_choices", [])
            if str(item.id) == request.GET.get("academic_year")
        ),
        None,
    )
    add("academic_year", getattr(academic_year, "name_en", None))

    semester = next(
        (
            item
            for item in options.get("semester_choices", [])
            if str(item.id) == request.GET.get("semester")
        ),
        None,
    )
    add("semester", getattr(semester, "name_en", None))

    boolean_labels = {
        "open": _("Open applications"),
        "moe": _("MOE approved"),
        "moh": _("MOH approved"),
        "yok": _("YÖK recognized"),
        "erasmus": _("Erasmus+"),
    }
    for name, label in boolean_labels.items():
        if request.GET.get(name):
            add(name, label)

    return chips


def program_list(request):
    state = read_program_filters(request.GET)

    programs = (
        Program.objects.filter(
            is_active=True,
            university__is_active=True,
        )
        .select_related(
            "university",
            "university__city",
            "department",
            "program_language",
        )
        .prefetch_related("offerings")
    )

    programs = apply_program_filters(programs, state).order_by(
        "-listing_priority",
        "university__name_en",
        "name_en",
    )

    paginator = Paginator(programs, 24)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)

    options = _program_filter_options()
    options.update(
        {
            "university_choices": University.objects.filter(
                is_active=True,
                programs__is_active=True,
            )
            .distinct()
            .order_by("name_en"),
            "city_choices": City.objects.filter(
                is_active=True,
                universities__programs__is_active=True,
            )
            .distinct()
            .order_by("name_en"),
            "university_type_choices": UniversityType.choices,
        }
    )

    context = {
        "programs": page_obj.object_list,
        "page_obj": page_obj,
        "program_result_count": paginator.count,
        "filters": state,
        "query_without_page": query_params.urlencode(),
        **options,
    }
    context["active_filters"] = _build_active_program_filters(request, context)

    return render(
        request,
        "public/program_list.html",
        context,
    )


def program_detail(request, slug):
    active_offerings = (
        ProgramOffering.objects.filter(
            is_active=True,
        )
        .select_related(
            "academic_year",
            "semester",
        )
        .order_by(
            "academic_year__name_en",
            "semester__name_en",
            "tuition",
        )
    )

    active_media = UniversityMedia.objects.filter(
        is_active=True,
    ).order_by("sort_order", "created_at")

    program = get_object_or_404(
        Program.objects.select_related(
            "university",
            "university__city",
            "university__city__province",
            "university__city__province__country",
            "department",
            "program_language",
        ).prefetch_related(
            Prefetch("offerings", queryset=active_offerings, to_attr="active_offerings"),
            Prefetch("university__media", queryset=active_media, to_attr="active_media"),
        ),
        slug_en=slug,
        is_active=True,
        university__is_active=True,
    )

    similarity_filter = Q(degree=program.degree)
    department = program.department if program.department_id else None
    if department is not None:
        similarity_filter |= Q(department__slug_en=department.slug_en)
    if program.program_language_id:
        similarity_filter |= Q(program_language=program.program_language)

    similarity_cases = []
    if department is not None:
        similarity_cases.extend(
            [
                When(
                    department__slug_en=department.slug_en,
                    degree=program.degree,
                    program_language=program.program_language,
                    then=Value(6),
                ),
                When(
                    department__slug_en=department.slug_en,
                    degree=program.degree,
                    then=Value(5),
                ),
                When(
                    department__slug_en=department.slug_en,
                    program_language=program.program_language,
                    then=Value(4),
                ),
                When(
                    department__slug_en=department.slug_en,
                    then=Value(3),
                ),
            ]
        )

    similarity_cases.extend(
        [
            When(
                degree=program.degree,
                program_language=program.program_language,
                then=Value(2),
            ),
            When(degree=program.degree, then=Value(1)),
        ]
    )

    similar_programs = annotate_min_active_tuition(
        Program.objects.filter(
            is_active=True,
            university__is_active=True,
        )
        .filter(similarity_filter)
        .exclude(pk=program.pk)
        .select_related(
            "university",
            "university__city",
            "department",
            "program_language",
        )
        .annotate(
            similarity_score=Case(
                *similarity_cases,
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        .order_by(
            "-similarity_score",
            "-listing_priority",
            "university__name_en",
            "name_en",
        )[:6]
    )

    more_from_university = annotate_min_active_tuition(
        Program.objects.filter(
            university=program.university,
            is_active=True,
        )
        .exclude(pk=program.pk)
        .select_related(
            "department",
            "program_language",
        )
        .order_by("-listing_priority", "name_en")[:4]
    )

    university_program_count = Program.objects.filter(
        university=program.university,
        is_active=True,
    ).count()

    return render(
        request,
        "public/program_detail.html",
        {
            "program": program,
            "offerings": getattr(program, "active_offerings", []),
            "university_media": getattr(program.university, "active_media", [])[:6],
            "similar_programs": similar_programs,
            "more_from_university": more_from_university,
            "university_program_count": university_program_count,
            "today": timezone.localdate(),
        },
    )


def faq(request):
    categories = FAQCategory.objects.filter(is_active=True).prefetch_related("faqs")
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
    students = Student.objects.filter(user=request.user).prefetch_related(
        "applications__program_offering__program__university"
    )
    applications = Application.objects.filter(student__user=request.user).select_related(
        "student",
        "program_offering__program__university",
        "program_offering__academic_year",
        "program_offering__semester",
    )
    leads = request.user.leads.select_related("converted_student").order_by("-updated_at")[:8]

    return render(
        request,
        "public/dashboard.html",
        {
            "students": students,
            "applications": applications,
            "leads": leads,
        },
    )


@login_required
def profile(request):
    messages.info(
        request,
        "Applicant profiles are managed separately because one account can manage multiple people.",
    )
    return redirect("lead-list")
