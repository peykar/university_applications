from unittest.mock import Mock

from django.contrib import admin
from django.test import RequestFactory, SimpleTestCase

from apps.core.admin import ActiveActionsMixin


class ExampleAdmin(ActiveActionsMixin, admin.ModelAdmin):
    pass


class ActiveActionsMixinTests(SimpleTestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_registered_inactive_action_accepts_model_admin_request_and_queryset(self):
        model_admin = ExampleAdmin(Mock(), admin.site)
        request = self.request_factory.get("/admin/")
        request.user = Mock()
        request.user.has_perm.return_value = True
        queryset = Mock()

        action = model_admin.get_actions(request)["mark_inactive"][0]
        action(model_admin, request, queryset)

        queryset.update.assert_called_once_with(is_active=False)

    def test_registered_active_action_accepts_model_admin_request_and_queryset(self):
        model_admin = ExampleAdmin(Mock(), admin.site)
        request = self.request_factory.get("/admin/")
        request.user = Mock()
        request.user.has_perm.return_value = True
        queryset = Mock()

        action = model_admin.get_actions(request)["mark_active"][0]
        action(model_admin, request, queryset)

        queryset.update.assert_called_once_with(is_active=True)
