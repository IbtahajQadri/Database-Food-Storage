from django.test import TestCase
from django.urls import reverse
from .models import Category, Food
from datetime import date, timedelta


class InventoryViewsTest(TestCase):
    def setUp(self):
        # Create some categories and foods for testing
        self.category = Category.objects.create(name='Vegetables', unit='kg', ideal_quantity=10)
        self.food = Food.objects.create(
            name='Tomato',
            category=self.category,
            quantity=5,
            best_before=date.today() + timedelta(days=5)
        )

    def test_dashboard_view(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/dashboard.html')

    def test_category_view(self):
        url = reverse('category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/category.html')

    def test_category_view_get(self):
        url = reverse('category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', response.context)
        self.assertTemplateUsed(response, 'inventory/category.html')

    def test_food_view(self):
        url = reverse('food')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/food.html')

    def test_food_view_get(self):
        url = reverse('food')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', response.context)
        self.assertIn('foods', response.context)
        self.assertTemplateUsed(response, 'inventory/food.html')

    def test_shopping_view(self):
        response = self.client.get('/shopping/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/shopping.html')

    def test_search_view_get(self):
        response = self.client.get('/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/search.html')

