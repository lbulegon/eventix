from django.test import TestCase


class AuthCompatUrlsTestCase(TestCase):
    def test_auth_login_compat_v1_nao_retorna_404(self):
        response = self.client.post("/api/v1/auth/login/", {"username": "x", "password": "y"})
        self.assertNotEqual(response.status_code, 404)

    def test_auth_refresh_compat_v1_nao_retorna_404(self):
        response = self.client.post("/api/v1/auth/refresh/", {"refresh": "token-invalido"})
        self.assertNotEqual(response.status_code, 404)
