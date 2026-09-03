from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Prefetch, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.content.models import FAQ, FAQCategory
from apps.geography.models import City
from apps.universities.models import (
    AcademicUnit,
    AcademicYear,
    Currency,
    DegreeType,
    GeneralField,
    Intake,
    OfferingFee,
    Program,
    ProgramLanguage,
    ProgramOffering,
    StudyMode,
    University,
    UniversityMedia,
    UniversityType,
)

from .forms import ContactForm
from .seo import (
    absolute_media_url,
    breadcrumb_schema,
    graph_schema,
    localized_absolute_url,
)
from .services.program_filters import (
    annotate_min_active_tuition,
    apply_program_filters,
    read_program_filters,
)


def _canonical_field_choices(*, university=None):
    general_fields = GeneralField.objects.filter(
        is_active=True,
        programs__is_active=True,
        programs__university__is_active=True,
    ).exclude(slug_en="")

    if university is not None:
        general_fields = general_fields.filter(programs__university=university)

    return general_fields.distinct().order_by("sort_order", "name_en", "pk")


def _program_filter_options(*, university=None):
    base_programs = Program.objects.filter(
        is_active=True,
        university__is_active=True,
    )

    if university is not None:
        base_programs = base_programs.filter(university=university)

    return {
        "degree_choices": DegreeType.choices,
        "study_mode_choices": StudyMode.choices,
        "language_choices": ProgramLanguage.objects.filter(
            is_active=True,
            programs__in=base_programs,
        )
        .distinct()
        .order_by("name_en"),
        "academic_unit_choices": AcademicUnit.objects.filter(
            is_active=True,
            programs__in=base_programs,
        )
        .distinct()
        .order_by("name_en"),
        "field_choices": _canonical_field_choices(university=university),
        "academic_year_choices": AcademicYear.objects.filter(
            is_active=True,
            program_offerings__program__in=base_programs,
        )
        .distinct()
        .order_by("name_en"),
        "intake_choices": Intake.objects.filter(
            is_active=True,
            program_offerings__program__in=base_programs,
        )
        .distinct()
        .order_by("academic_year__name_en", "name_en"),
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
    active_programs = Program.objects.filter(is_active=True, university__is_active=True)
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

    popular_programs = annotate_min_active_tuition(
        active_programs.select_related(
            "university",
            "academic_unit",
            "department",
        ).prefetch_related("instruction_language_rows__language")
    ).order_by("-listing_priority", "name_en")[:8]

    study_fields = (
        GeneralField.objects.filter(
            is_active=True,
            programs__is_active=True,
            programs__university__is_active=True,
        )
        .exclude(slug_en="")
        .annotate(
            program_count=Count(
                "programs",
                filter=Q(
                    programs__is_active=True,
                    programs__university__is_active=True,
                ),
                distinct=True,
            )
        )
        .order_by("-program_count", "sort_order", "name_en")[:10]
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
            "seo_schema": graph_schema(
                {
                    "@type": "Organization",
                    "name": "TurkDemy",
                    "url": localized_absolute_url("home"),
                },
                {
                    "@type": "WebSite",
                    "name": "TurkDemy",
                    "url": localized_absolute_url("home"),
                },
            ),
            **filter_options,
        },
    )


def university_list(request):
    query = request.GET.get("q", "").strip()
    qs = (
        University.objects.filter(is_active=True)
        .select_related(
            "city",
            "city__province",
            "city__province__country",
        )
        .annotate(
            active_program_count=Count(
                "programs",
                filter=Q(programs__is_active=True),
            )
        )
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
        {
            "universities": qs.order_by("-listing_priority", "name_en"),
            "seo_schema": {
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": _("Universities in Türkiye"),
                "url": localized_absolute_url("university-list"),
            },
        },
    )


def university_city_detail(request, slug):
    city = get_object_or_404(
        City.objects.filter(
            is_active=True,
            universities__is_active=True,
        )
        .select_related("province", "province__country")
        .distinct(),
        slug_en=slug,
    )

    universities = (
        University.objects.filter(
            is_active=True,
            city=city,
        )
        .select_related("city", "city__province", "city__province__country")
        .annotate(
            active_program_count=Count(
                "programs",
                filter=Q(programs__is_active=True),
                distinct=True,
            )
        )
        .order_by("-listing_priority", "name_en")
    )

    paginator = Paginator(universities, 24)
    page_obj = paginator.get_page(request.GET.get("page"))

    programs = annotate_min_active_tuition(
        Program.objects.filter(
            is_active=True,
            university__is_active=True,
            university__city=city,
        )
        .select_related(
            "university",
            "university__city",
            "academic_unit",
            "department",
        )
        .prefetch_related("instruction_language_rows__language")
    ).order_by(
        "-listing_priority",
        "-university__listing_priority",
        "name_en",
    )[:12]

    city_url = localized_absolute_url(
        "university-city-detail",
        slug=city.slug_en,
    )
    city_description = city.localized_seo_description or city.localized_description
    schema_node = {
        "@type": "CollectionPage",
        "name": city.localized_seo_title or city.localized_name,
        "url": city_url,
    }
    if city_description:
        schema_node["description"] = city_description

    return render(
        request,
        "public/university_city_detail.html",
        {
            "city": city,
            "universities": page_obj.object_list,
            "page_obj": page_obj,
            "university_count": paginator.count,
            "programs": programs,
            "program_count": Program.objects.filter(
                is_active=True,
                university__is_active=True,
                university__city=city,
            ).count(),
            "program_filter_url": (
                f"{reverse('program-list')}?{urlencode({'city': city.slug_en})}"
            ),
            "seo_schema": graph_schema(
                schema_node,
                breadcrumb_schema(
                    [
                        (_("Universities"), localized_absolute_url("university-list")),
                        (city.localized_name, city_url),
                    ]
                ),
            ),
        },
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
            "academic_unit",
            "department",
        )
        .prefetch_related("instruction_language_rows__language", "offerings")
    )

    programs = annotate_min_active_tuition(apply_program_filters(programs, state)).order_by(
        "-listing_priority",
        "name_en",
    )

    paginator = Paginator(programs, 24)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)

    university_url = localized_absolute_url(
        "university-detail",
        slug=university.slug_en,
    )
    university_node = {
        "@type": "CollegeOrUniversity",
        "name": university.localized_name,
        "url": university_url,
    }
    if university.website:
        university_node["sameAs"] = university.website
    if university.logo:
        university_node["logo"] = absolute_media_url(university.logo.url)
    if university.city:
        university_node["address"] = {
            "@type": "PostalAddress",
            "addressLocality": university.city.localized_name,
        }

    context = {
        "university": university,
        "seo_image_url": (
            absolute_media_url(university.banner.url)
            if university.banner
            else absolute_media_url(university.logo.url)
            if university.logo
            else ""
        ),
        "seo_schema": graph_schema(
            university_node,
            breadcrumb_schema(
                [
                    (_("Universities"), localized_absolute_url("university-list")),
                    (university.localized_name, university_url),
                ]
            ),
        ),
        "programs": page_obj.object_list,
        "page_obj": page_obj,
        "program_result_count": paginator.count,
        "filters": state,
        "query_without_page": query_params.urlencode(),
        **_program_filter_options(university=university),
    }
    context["active_filters"] = _build_active_program_filters(request, context)

    return render(
        request,
        "public/university_detail.html",
        context,
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
    add("field", getattr(field, "localized_name", None))

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
    add("language", getattr(language, "localized_name", None))

    study_mode_label = dict(StudyMode.choices).get(request.GET.get("study_mode"))
    add("study_mode", study_mode_label)

    academic_unit = next(
        (
            item
            for item in options.get("academic_unit_choices", [])
            if item.slug_en == request.GET.get("academic_unit")
        ),
        None,
    )
    add("academic_unit", getattr(academic_unit, "localized_name", None))

    university = next(
        (
            item
            for item in options.get("university_choices", [])
            if item.slug_en == request.GET.get("university")
        ),
        None,
    )
    add("university", getattr(university, "localized_name", None))

    city = next(
        (
            item
            for item in options.get("city_choices", [])
            if item.slug_en == request.GET.get("city")
        ),
        None,
    )
    add("city", getattr(city, "localized_name", None))

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
    add("academic_year", getattr(academic_year, "localized_name", None))

    intake = next(
        (
            item
            for item in options.get("intake_choices", [])
            if str(item.id) == request.GET.get("intake")
        ),
        None,
    )
    add("intake", getattr(intake, "localized_name", None))

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
            "academic_unit",
            "department",
        )
        .prefetch_related("instruction_language_rows__language", "offerings")
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
        "seo_schema": {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": _("University programs in Türkiye"),
            "url": localized_absolute_url("program-list"),
        },
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


def program_field_detail(request, slug):
    general_field = get_object_or_404(
        GeneralField.objects.filter(
            is_active=True,
            programs__is_active=True,
            programs__university__is_active=True,
        ).distinct(),
        slug_en=slug,
    )

    programs = annotate_min_active_tuition(
        Program.objects.filter(
            is_active=True,
            university__is_active=True,
            general_fields=general_field,
        )
        .select_related(
            "university",
            "university__city",
            "academic_unit",
            "department",
        )
        .prefetch_related("instruction_language_rows__language")
        .distinct()
    ).order_by(
        "-listing_priority",
        "university__name_en",
        "name_en",
    )

    paginator = Paginator(programs, 24)
    page_obj = paginator.get_page(request.GET.get("page"))

    universities = (
        University.objects.filter(
            is_active=True,
            programs__is_active=True,
            programs__general_fields=general_field,
        )
        .select_related("city", "city__province")
        .annotate(
            active_program_count=Count(
                "programs",
                filter=Q(
                    programs__is_active=True,
                    programs__general_fields=general_field,
                ),
                distinct=True,
            )
        )
        .distinct()
        .order_by("-active_program_count", "-listing_priority", "name_en")
    )

    field_url = localized_absolute_url(
        "program-field-detail",
        slug=general_field.slug_en,
    )
    field_description = (
        general_field.localized_seo_description or general_field.localized_description
    )
    schema_node = {
        "@type": "CollectionPage",
        "name": general_field.localized_seo_title or general_field.localized_name,
        "url": field_url,
    }
    if field_description:
        schema_node["description"] = field_description

    return render(
        request,
        "public/program_field_detail.html",
        {
            "field": general_field,
            "programs": page_obj.object_list,
            "page_obj": page_obj,
            "program_result_count": paginator.count,
            "universities": universities[:12],
            "university_count": universities.count(),
            "advanced_filter_url": (
                f"{reverse('program-list')}?{urlencode({'field': general_field.slug_en})}"
            ),
            "seo_schema": graph_schema(
                schema_node,
                breadcrumb_schema(
                    [
                        (_("Programs"), localized_absolute_url("program-list")),
                        (general_field.localized_name, field_url),
                    ]
                ),
            ),
        },
    )


def program_detail(request, slug):
    active_fees = OfferingFee.objects.filter(is_active=True).select_related("language")
    active_offerings = (
        ProgramOffering.objects.filter(
            is_active=True,
        )
        .select_related(
            "academic_year",
            "intake",
        )
        .prefetch_related(
            Prefetch("fees", queryset=active_fees, to_attr="active_structured_fees"),
        )
        .order_by(
            "academic_year__name_en",
            "intake__name_en",
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
            "academic_unit",
            "department",
        ).prefetch_related(
            "instruction_language_rows__language",
            Prefetch("offerings", queryset=active_offerings, to_attr="active_offerings"),
            Prefetch("university__media", queryset=active_media, to_attr="active_media"),
        ),
        slug_en=slug,
        is_active=True,
        university__is_active=True,
    )

    similarity_filter = Q(degree=program.degree)
    department = program.department if program.department_id else None
    language_ids = list(program.instruction_languages.values_list("pk", flat=True))
    if department is not None:
        similarity_filter |= Q(department__slug_en=department.slug_en)
    if language_ids:
        similarity_filter |= Q(instruction_languages__in=language_ids)

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
            "academic_unit",
            "department",
        )
        .prefetch_related("instruction_language_rows__language")
        .annotate(
            similarity_score=Case(
                When(department=department, degree=program.degree, then=Value(4)),
                When(department=department, then=Value(3)),
                When(degree=program.degree, then=Value(2)),
                default=Value(1),
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
            "academic_unit",
            "department",
        )
        .prefetch_related("instruction_language_rows__language")
        .order_by("-listing_priority", "name_en")[:4]
    )

    university_program_count = Program.objects.filter(
        university=program.university,
        is_active=True,
    ).count()

    program_url = localized_absolute_url("program-detail", slug=program.slug_en)
    university_url = localized_absolute_url(
        "university-detail",
        slug=program.university.slug_en,
    )
    program_node = {
        "@type": "EducationalOccupationalProgram",
        "name": program.localized_name,
        "url": program_url,
        "provider": {
            "@type": "CollegeOrUniversity",
            "name": program.university.localized_name,
            "url": university_url,
        },
    }
    if program.localized_description:
        program_node["description"] = program.localized_description
    if program.duration_months:
        program_node["timeToComplete"] = f"P{program.duration_months}M"

    return render(
        request,
        "public/program_detail.html",
        {
            "program": program,
            "seo_image_url": (
                absolute_media_url(program.university.banner.url)
                if program.university.banner
                else absolute_media_url(program.university.logo.url)
                if program.university.logo
                else ""
            ),
            "seo_schema": graph_schema(
                program_node,
                breadcrumb_schema(
                    [
                        (_("Programs"), localized_absolute_url("program-list")),
                        (program.university.localized_name, university_url),
                        (program.localized_name, program_url),
                    ]
                ),
            ),
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
    faq_entities = [
        {
            "@type": "Question",
            "name": item.localized_question,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item.localized_answer,
            },
        }
        for category in categories
        for item in category.faqs.all()
        if item.is_active
    ]
    return render(
        request,
        "public/faq.html",
        {
            "categories": categories,
            "seo_schema": {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": faq_entities,
            },
        },
    )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your message has been sent."))
            return redirect("contact")
    else:
        form = ContactForm()

    return render(
        request,
        "public/contact.html",
        {
            "form": form,
            "seo_schema": {
                "@context": "https://schema.org",
                "@type": "ContactPage",
                "name": _("Contact TurkDemy"),
                "url": localized_absolute_url("contact"),
            },
        },
    )


def about(request):
    return render(
        request,
        "public/about.html",
        {
            "seo_schema": graph_schema(
                {
                    "@type": "AboutPage",
                    "name": _("About TurkDemy"),
                    "url": localized_absolute_url("about"),
                },
                {
                    "@type": "Organization",
                    "name": "TurkDemy",
                    "url": localized_absolute_url("home"),
                },
            ),
        },
    )


@login_required
def dashboard(request):
    """Legacy customer dashboard entry; Requests are the customer workspace home."""
    return redirect("lead-list")


@login_required
def profile(request):
    messages.info(
        request,
        _(
            "Applicant profiles are managed separately because one account can "
            "manage multiple people."
        ),
    )
    return redirect("lead-list")
