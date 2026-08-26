from django.test import SimpleTestCase, override_settings


@override_settings(DEBUG=True)
class GlobalBranded404Tests(SimpleTestCase):
    def test_unknown_browser_url_uses_branded_page_even_in_debug(self):
        response = self.client.get(
            "/en/this-route-does-not-exist/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "errors/404.html")
        self.assertContains(
            response,
            "We couldn't find that page.",
            status_code=404,
        )
        self.assertEqual(
            response.headers.get("X-TurkDemy-Error-Page"),
            "1",
        )

    def test_non_html_404_is_not_replaced(self):
        response = self.client.get(
            "/en/this-route-does-not-exist/",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(
            response.headers.get("X-TurkDemy-Error-Page"),
            "1",
        )

    def test_api_404_is_not_replaced(self):
        response = self.client.get(
            "/api/v1/this-route-does-not-exist/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(
            response.headers.get("X-TurkDemy-Error-Page"),
            "1",
        )

    def test_health_404_is_not_replaced(self):
        response = self.client.get(
            "/health/this-route-does-not-exist/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(
            response.headers.get("X-TurkDemy-Error-Page"),
            "1",
        )
