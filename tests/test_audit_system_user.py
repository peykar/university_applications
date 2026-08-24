from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.core.audit import audited_update_or_create, get_system_user
from apps.geography.models import Country


@override_settings(
    SYSTEM_USER_USERNAME="automation-test",
    SYSTEM_USER_EMAIL="automation-test@turkdemy.local",
    SYSTEM_USER_IS_ACTIVE=False,
    SYSTEM_USER_IS_STAFF=False,
    SYSTEM_USER_IS_SUPERUSER=False,
)
class SystemUserAuditTests(TestCase):
    def test_system_user_is_non_login_account(self):
        user = get_system_user()

        self.assertEqual(user.username, "automation-test")
        self.assertEqual(user.email, "automation-test@turkdemy.local")
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_audited_update_preserves_creator_and_changes_updater(self):
        system_user = get_system_user()
        country, created = audited_update_or_create(
            Country.objects,
            lookup={"iso2": "TR"},
            defaults={
                "iso3": "TUR",
                "name_en": "Türkiye",
                "name_fa": "ترکیه",
                "name_tr": "Türkiye",
                "name_ar": "تركيا",
                "slug_en": "turkiye",
                "slug_fa": "ترکیه",
                "slug_tr": "turkiye",
                "slug_ar": "تركيا",
                "is_active": True,
            },
            actor=system_user,
        )
        self.assertTrue(created)
        self.assertEqual(country.created_by, system_user)
        self.assertEqual(country.updated_by, system_user)

        User = get_user_model()
        staff = User.objects.create_user(username="staff-user", password="password")
        country.updated_by = staff
        country.save(update_fields=["updated_by"])

        country, created = audited_update_or_create(
            Country.objects,
            lookup={"iso2": "TR"},
            defaults={
                "iso3": "TUR",
                "name_en": "Türkiye",
                "name_fa": "ترکیه",
                "name_tr": "Türkiye",
                "name_ar": "تركيا",
                "slug_en": "turkiye",
                "slug_fa": "ترکیه",
                "slug_tr": "turkiye",
                "slug_ar": "تركيا",
                "is_active": True,
            },
            actor=system_user,
        )
        self.assertFalse(created)
        self.assertEqual(country.created_by, system_user)
        self.assertEqual(country.updated_by, system_user)
