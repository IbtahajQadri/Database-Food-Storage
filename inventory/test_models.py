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

    def test_missing_name_raises_error(self):
        # Ensures that creating a category with a missing name raises an IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name=None, unit='liters', ideal_quantity=5.0)

    def test_missing_unit_raises_error(self):
        # Ensures that creating a category with a missing unit raises an IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Dairy', unit=None, ideal_quantity=5.0)

    def test_missing_ideal_quantity_raises_error(self):
        # Ensures that creating a category without an ideal_quantity raises an IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Bakery', unit='packs', ideal_quantity=None)

    def test_str_representation(self):
        # Tests that the __str__ method of Category returns the name
        category = Category.objects.create(name='Meat', unit='kg', ideal_quantity=30)
        self.assertEqual(str(category), 'Meat')

    def test_update_category(self):
        # Tests that a category can be updated and changes persist
        category = Category.objects.create(name='Seafood', unit='kg', ideal_quantity=10)
        category.name = 'Fresh Seafood'
        category.unit = 'pieces'
        category.ideal_quantity = 25
        category.save()

        updated = Category.objects.get(id=category.id)
        self.assertEqual(updated.name, 'Fresh Seafood')
        self.assertEqual(updated.unit, 'pieces')
        self.assertEqual(updated.ideal_quantity, 25)

    def test_delete_category(self):
        # Tests that a category can be deleted and is no longer retrievable
        category = Category.objects.create(name='Snacks', unit='packs', ideal_quantity=12)
        category_id = category.id
        category.delete()
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=category_id)

    def test_name_uniqueness_case_sensitivity(self):
        Category.objects.create(name='Drinks', unit='liters', ideal_quantity=5.0)
        # This will pass if uniqueness is case-sensitive
        Category.objects.create(name='drinks', unit='liters', ideal_quantity=5.0)

    def test_bulk_create_categories(self):
        Category.objects.bulk_create([
            Category(name='A', unit='u', ideal_quantity=1),
            Category(name='B', unit='u', ideal_quantity=2)
        ])
        self.assertEqual(Category.objects.count(), 2)

    def test_filter_by_unit(self):
        Category.objects.create(name='Juice', unit='liters', ideal_quantity=3)
        result = Category.objects.filter(unit='liters')
        self.assertEqual(result.count(), 1)
