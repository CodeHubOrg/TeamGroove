from django.test import TestCase
from django.test.client import Client
from django.shortcuts import reverse

class CoreViewsTest(TestCase):

    def test_frontpage_loads(self):        
        response = self.client.get(reverse('frontpage'))
        self.assertEqual(response.status_code, 200)
