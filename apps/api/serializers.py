from rest_framework import serializers

from apps.content.models import FAQ, FAQCategory
from apps.universities.models import Program, ProgramOffering, University


class UniversitySerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name_en", read_only=True)

    class Meta:
        model = University
        fields = (
            "id",
            "slug_en",
            "name_en",
            "name_fa",
            "name_tr",
            "name_ar",
            "city",
            "university_type",
            "logo",
            "banner",
            "website",
            "is_yok_recognized",
            "is_moe_approved",
            "is_moh_approved",
            "has_erasmus",
            "has_dormitory",
            "listing_priority",
        )


class ProgramSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(
        source="university.name_en",
        read_only=True,
    )
    languages = serializers.SerializerMethodField()
    academic_unit_name = serializers.CharField(
        source="academic_unit.name_en", read_only=True, default=None
    )
    duration_display = serializers.CharField(read_only=True)

    def get_languages(self, obj):
        return [
            {
                "id": str(row.language_id),
                "name": row.language.name_en,
                "percentage": row.percentage,
                "is_primary": row.is_primary,
            }
            for row in obj.instruction_language_rows.select_related("language").order_by(
                "-is_primary", "language__name_en"
            )
        ]

    class Meta:
        model = Program
        fields = (
            "id",
            "slug_en",
            "name_en",
            "name_fa",
            "name_tr",
            "name_ar",
            "university",
            "university_name",
            "degree",
            "study_mode",
            "academic_unit",
            "academic_unit_name",
            "languages",
            "duration_months",
            "duration_display",
            "listing_priority",
        )


class ProgramOfferingSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(
        source="program.name_en",
        read_only=True,
    )

    class Meta:
        model = ProgramOffering
        fields = (
            "id",
            "program",
            "program_name",
            "academic_year",
            "semester",
            "currency",
            "fee_basis",
            "tuition",
            "tuition_discounted",
            "tuition_cash",
            "tuition_annual_installment",
            "deposit",
            "preparatory_tuition",
            "preparation_included",
            "quota",
            "deadline",
            "valid_from",
            "valid_until",
            "notes",
            "source",
        )


class FAQCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQCategory
        fields = (
            "id",
            "key",
            "name_en",
            "name_fa",
            "name_tr",
            "name_ar",
            "sort_order",
        )


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = (
            "id",
            "category",
            "question_en",
            "question_fa",
            "question_tr",
            "question_ar",
            "answer_en",
            "answer_fa",
            "answer_tr",
            "answer_ar",
            "sort_order",
        )
