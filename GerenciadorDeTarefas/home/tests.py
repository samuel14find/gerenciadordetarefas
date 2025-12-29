from django.test import TestCase

# Create your tests here.
class TestHome(TestCase):
    def test_creditos(self):
        response = self.client.get('/creditos/')
        self.assertEqual(response.status_code, 200)

