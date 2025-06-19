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

    def test_category_create_post_success(self):
        url = reverse('category') + '?action=create'
        response = self.client.post(url, {
            'name': 'Fruits',
            'unit': 'kg',
            'ideal_quantity': '15',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Category created successfully!')
        self.assertTrue(Category.objects.filter(name='Fruits').exists())

    def test_category_create_post_invalid_quantity(self):
        url = reverse('category') + '?action=create'
        response = self.client.post(url, {
            'name': 'Fruits',
            'unit': 'kg',
            'ideal_quantity': '-5',
        })
        self.assertContains(response, 'Ideal quantity must be greater than zero.')

    def test_category_update(self):
        response = self.client.post('/category/?action=modify', {
            'category_id': self.category.id,
            'name': 'Fresh Vegetables',
            'unit': 'kg',
            'ideal_quantity': 10,
        })

        self.assertEqual(response.status_code, 200)
        updated_category = Category.objects.get(id=self.category.id)
        self.assertEqual(updated_category.name, 'Fresh Vegetables')
        self.assertEqual(updated_category.ideal_quantity, 10)
        self.assertContains(response, 'Category modified successfully!')
 
    def test_category_delete(self):
        # First confirm the category exists
        category_id = self.category.id
        self.assertTrue(Category.objects.filter(id=category_id).exists())
        # Make sure the category has NO food associated
        Food.objects.filter(category=self.category).delete()

        response = self.client.post('/category/?action=delete', {
            'category_id': category_id,
            'confirm_delete': 'on',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Category.objects.filter(id=category_id).exists())
        self.assertContains(response, 'Category deleted successfully!')

    def test_food_create_post_success(self):
        url = reverse('food') + '?action=create'
        response = self.client.post(url, {
            'name': 'Carrot',
            'category_id': str(self.category.id),
            'quantity': '3',
            'best_before': (date.today() + timedelta(days=7)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Food item created successfully!')
        self.assertTrue(Food.objects.filter(name='Carrot').exists())

    def test_category_delete_with_food(self):
        Food.objects.create(
            name='Carrot',
            quantity=2,
            category=self.category,
            best_before='2025-12-31'
        )

        response = self.client.post('/category/?action=delete', {
            'category_id': self.category.id,
            'confirm_delete': 'on',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Category.objects.filter(id=self.category.id).exists())
        self.assertContains(response, 'Cannot delete category with associated food items.')

