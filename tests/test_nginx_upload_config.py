from pathlib import Path
from unittest import TestCase


class NginxUploadConfigTests(TestCase):
    def test_example_allows_application_uploads(self):
        config = Path("deploy/nginx/turkdemy.conf.example").read_text()
        self.assertIn("client_max_body_size 25M;", config)

    def test_deployment_docs_explain_413_fix(self):
        docs = Path("docs/deployment.md").read_text()
        self.assertIn("413 Request Entity Too Large", docs)
        self.assertIn("sudo nginx -t", docs)
        self.assertIn("sudo systemctl reload nginx", docs)
