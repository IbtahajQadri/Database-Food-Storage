from django.test import TestCase
from datetime import date
from inventory.models import Category
from django.db import IntegrityError


class CategoryModelTest(TestCase):
    def test_create_and_read_category(self):
        # Tests if a category can be created and correctly retrieved from the database
        Category.objects.create(name='Vegetables', unit='kg', ideal_quantity=20.0)
        category = Category.objects.get(name='Vegetables')
        self.assertEqual(category.name, 'Vegetables')
        self.assertEqual(category.unit, 'kg')
        self.assertEqual(category.ideal_quantity, 20.0)

    def test_duplicate_category_name_raises_error(self):
        # Ensures that creating two categories with the same name raises an IntegrityError (due to unique constraint)
        Category.objects.create(name='Fruits', unit='kg', ideal_quantity=15.0)
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Fruits', unit='pieces', ideal_quantity=10.0)

