from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

PAGES = {
    'home': '/',
    'author': '/about/author/',
    'tech': '/about/tech/',
}
TEMPLATES_NAMES = {
    reverse('about:author'): 'about/author.html',
    reverse('about:tech'): 'about/tech.html',
}


class StaticTests(TestCase):
    def test_urls_static_pages(self):
        """Static pages urls"""
        for page, address in PAGES.items():
            with self.subTest(page=page):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_views_spatic_pages(self):
        """Static pages views"""
        for address, template in TEMPLATES_NAMES.items():
            with self.subTest(page=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
