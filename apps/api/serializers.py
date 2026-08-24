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
    language = serializers.CharField(
        source="program_language.name_en",
        read_only=True,
    )

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
            "language",
            "duration",
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
            "quota",
            "deadline",
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
