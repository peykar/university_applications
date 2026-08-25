from django.test import SimpleTestCase

from apps.leads.forms import _unique_ids_by_label


class PreferenceSelectorDedupeTests(SimpleTestCase):
    def test_duplicate_labels_are_collapsed_case_insensitively(self):
        rows = [
            ("1", "Accounting And Auditing"),
            ("2", "Accounting And Auditing"),
            ("3", " accounting and auditing "),
            ("4", "Accounting And Auditing With Thesis"),
        ]

        self.assertEqual(_unique_ids_by_label(rows), ["1", "4"])

    def test_blank_labels_are_not_exposed(self):
        rows = [("1", ""), ("2", "  "), ("3", "Medicine")]
        self.assertEqual(_unique_ids_by_label(rows), ["3"])
