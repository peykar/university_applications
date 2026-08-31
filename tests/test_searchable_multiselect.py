from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class SearchableMultiselectTests(SimpleTestCase):
    def setUp(self):
        self.source = (
            Path(settings.BASE_DIR) / "static" / "js" / "searchable_multiselect.js"
        ).read_text(encoding="utf-8")

    def test_selection_closes_picker(self):
        self.assertIn(
            'optionsPanel.classList.remove("is-open");',
            self.source,
        )

    def test_click_reopens_picker_even_when_input_is_already_focused(self):
        self.assertIn(
            'search.addEventListener("click", openOptions);',
            self.source,
        )
        self.assertIn(
            'search.addEventListener("focus", openOptions);',
            self.source,
        )

    def test_escape_and_outside_click_still_close_picker(self):
        self.assertIn('event.key === "Escape"', self.source)
        self.assertIn("!wrapper.contains(event.target)", self.source)

    def test_interface_copy_comes_from_localized_data_attributes(self):
        self.assertIn('select.dataset.placeholder || ""', self.source)
        self.assertIn('select.dataset.emptyLabel || ""', self.source)
        self.assertIn('select.dataset.removeLabel || ""', self.source)
        self.assertNotIn('"No matching options"', self.source)
        self.assertNotIn("`Remove ${option.text}`", self.source)
