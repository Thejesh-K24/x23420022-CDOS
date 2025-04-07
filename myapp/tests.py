from django.test import TestCase
from django.urls import reverse

class MyViewTestCase(TestCase):
    def test_home_view(self):
        """Test if website is available or not-  returns 200 status"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)