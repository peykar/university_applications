from django.test import SimpleTestCase
from django.utils import translation

from apps.accounts.forms import AddLoginEmailForm


class AuthenticationTranslationTests(SimpleTestCase):
    def test_persian_sign_in_method_strings(self):
        with translation.override("fa"):
            self.assertEqual(
                translation.gettext("Sign-in methods"),
                "روش‌های ورود",
            )
            self.assertEqual(
                translation.gettext("Connected"),
                "متصل",
            )
            form = AddLoginEmailForm(user=None)
            self.assertEqual(form.fields["email"].label, "آدرس ایمیل")

    def test_turkish_sign_in_method_strings(self):
        with translation.override("tr"):
            self.assertEqual(
                translation.gettext("Sign-in methods"),
                "Giriş yöntemleri",
            )
            self.assertEqual(
                translation.gettext("Disconnect Telegram"),
                "Telegram bağlantısını kaldır",
            )

    def test_arabic_sign_in_method_strings(self):
        with translation.override("ar"):
            self.assertEqual(
                translation.gettext("Sign-in methods"),
                "طرق تسجيل الدخول",
            )
            self.assertEqual(
                translation.gettext("Verified email login"),
                "تسجيل الدخول ببريد إلكتروني موثّق",
            )
