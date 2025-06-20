from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Category, Food
from datetime import date
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def dashboard(request):
    return render(request, "inventory/dashboard.html")


def category_view(request):
    action = request.GET.get("action")
    success_message = ""
    error_message = ""
    units = ["kg", "liters", "pieces", "packs"]
    context = {"action": action}
    context["units"] = units
    context["selected_category"] = None  # default value

    if request.method == "POST":
        name = request.POST.get("name")
        unit = request.POST.get("unit")
        ideal_quantity = request.POST.get("ideal_quantity")
        category_id = request.POST.get("category_id")

        # Preserve form data for re-rendering in case of error
        context["form_data"] = {
            "name": name,
            "unit": unit,
            "ideal_quantity": ideal_quantity,
            "category_id": category_id,
        }

        if action == "create":
            if not name or not unit or not ideal_quantity:
                error_message = "Please fill in all fields."
            else:
                try:
                    ideal_quantity = float(ideal_quantity)
                    if ideal_quantity <= 0:
                        error_message = "Ideal quantity must be greater than zero."
                    else:
                        category = Category(
                            name=name, unit=unit, ideal_quantity=ideal_quantity
                        )
                        category.save()
                        success_message = "Category created successfully!"
                        logger.info(f"Category created: {name}")
                        context["form_data"] = {}  # Clear form on success
                except ValueError:
                    error_message = "Ideal quantity must be a number."
                except IntegrityError:
                    error_message = "Category name must be unique."

        elif action == "modify":
            context["categories"] = Category.objects.all()

            if not category_id or not name or not unit or not ideal_quantity:
                error_message = "Please fill in all fields."
            else:
                try:
                    ideal_quantity = float(ideal_quantity)
                    if ideal_quantity <= 0:
                        error_message = "Ideal quantity must be greater than zero."
                    else:
                        category = get_object_or_404(Category, pk=category_id)
                        category.name = name
                        category.unit = unit
                        category.ideal_quantity = ideal_quantity
                        category.save()
                        success_message = "Category modified successfully!"
                        logger.info(f"Category modified: ID {category_id}")
                        context["form_data"] = {}  # Clear form on success
                except ValueError:
                    error_message = "Ideal quantity must be a number."
                except IntegrityError:
                    error_message = "Category name must be unique."

        elif action == "delete":
            context["categories"] = Category.objects.all()
            confirm_delete = request.POST.get("confirm_delete")

            if not category_id:
                error_message = "Please select a category to delete."
            elif not confirm_delete:
                error_message = "Please confirm category deletion."
            else:
                category = get_object_or_404(Category, pk=category_id)
                if category.foods.exists():
                    error_message = 'Cannot delete category with associated food items.'
                    logger.warning(f'Attempted deletion of category with foods: ID {category_id}')
                else:
                    category.delete()
                    success_message = 'Category deleted successfully!'
                    logger.info(f'Category deleted: ID {category_id}')

    if request.method == "GET":
        context["categories"] = Category.objects.all()

        if action == "modify":
            category_id = request.GET.get("category_id")
            if category_id:
                category = get_object_or_404(Category, pk=category_id)
                context["selected_category"] = category

        if request.GET.get("success") == "1":
            success_message = "Category created successfully!"

    context["success_message"] = success_message
    context["error_message"] = error_message

    return render(request, "inventory/category.html", context)


def food_view(request):
    action = request.GET.get('action')
    success_message = ''
    error_message = ''
    context = {'action': action, 'today': date.today().isoformat()}

    context['categories'] = Category.objects.all()
    context['foods'] = Food.objects.all()

    # Make sure food_items is included for modify/delete pages
    if request.method == 'GET' and action in ['modify', 'delete']:
        context['food_items'] = Food.objects.all()

    if request.method == 'POST':
        submit_type = request.POST.get('submit_type')

        if action == 'create':
            name = request.POST.get('name')
            category_id = request.POST.get('category_id')
            quantity = request.POST.get('quantity')
            best_before = request.POST.get('best_before')

            selected_category = Category.objects.filter(id=category_id).first()
            context.update({
                'selected_category': selected_category,
                'name': name,
                'quantity': quantity,
                'best_before': best_before,
            })

            if submit_type == 'update_unit':
                return render(request, 'inventory/food.html', context)

            if not name or not category_id or not quantity or not best_before:
                error_message = 'Please fill in all fields.'
            else:
                try:
                    quantity = float(quantity)
                    if quantity < 0:
                        raise ValueError('Quantity must be non-negative.')

                    best_before_date = date.fromisoformat(best_before)
                    if best_before_date < date.today():
                        error_message = 'Best before date cannot be in the past.'
                    else:
                        category = get_object_or_404(Category, pk=category_id)
                        food = Food(name=name, category=category, quantity=quantity, best_before=best_before_date)
                        food.save()
                        success_message = 'Food item created successfully!'
                        context.update({
                            'name': '',
                            'quantity': '',
                            'best_before': '',
                            'selected_category': None
                        })
                except ValueError:
                    error_message = 'Quantity must be a number and non-negative.'

        elif action == 'modify':
            food_items = Food.objects.all()
            context['food_items'] = food_items
            context['categories'] = Category.objects.all()
            success_message = ''
            error_message = ''
            
            if request.method == 'POST':
                food_id = request.POST.get('food_id')
                if not food_id:
                    error_message = 'Please select a food item.'
                else:
                    selected_food = Food.objects.filter(id=food_id).first()
                    context['selected_food'] = selected_food

                    # If only food_id sent (dropdown changed), just reload form with data
                    if not request.POST.get('name'):
                        # just reload the form with selected food's data
                        pass
                    else:
                        # Full form submission for modification
                        name = request.POST.get('name')
                        category_id = request.POST.get('category_id')
                        quantity = request.POST.get('quantity')
                        best_before = request.POST.get('best_before')

                        if not (name and category_id and quantity and best_before):
                            error_message = 'Please fill in all fields.'
                        else:
                            try:
                                quantity = float(quantity)
                                if quantity < 0:
                                    raise ValueError('Quantity must be non-negative.')

                                best_before_date = date.fromisoformat(best_before)
                                if best_before_date < date.today():
                                    error_message = 'Best before date cannot be in the past.'
                                else:
                                    food = get_object_or_404(Food, pk=food_id)
                                    food.name = name
                                    food.category_id = category_id
                                    food.quantity = quantity
                                    food.best_before = best_before_date
                                    food.save()
                                    success_message = 'Food item modified successfully!'
                                    context['selected_food'] = food  # update selected food
                            except ValueError:
                                error_message = 'Quantity must be a number and non-negative.'


        elif action == 'delete':
            food_id = request.POST.get('food_id')
            if not food_id:
                error_message = 'Please select a food item to delete.'
            else:
                food = get_object_or_404(Food, pk=food_id)
                food.delete()
                success_message = 'Food item deleted successfully!'
            context['food_items'] = Food.objects.all()

    context['success_message'] = success_message
    context['error_message'] = error_message

    return render(request, 'inventory/food.html', context)

def search_view(request):
    filter_type = request.GET.get('filter')
    query = request.GET.get('query', '').strip()
    results = []
    message = ''

    if not filter_type:
        # Case 1: No filter selected - Search both food name and category
        if not query:
            if 'query' in request.GET:
                message = "Please enter a search term."
        else:
            food_matches = Food.objects.filter(name__icontains=query)
            if food_matches.exists():
                results = food_matches
            else:
                category_matches = Category.objects.filter(name__icontains=query)
                if category_matches.exists():
                    results = Food.objects.filter(category__in=category_matches)
                    if not results:
                        message = "No food items found in the matching categories."
                else:
                    message = "No matching food or category found."

    elif filter_type == 'best_before':
        # Case 2: Best Before Date filter
        if not query:
            message = "Please enter a date in YYYY-MM-DD format."
        else:
            try:
                selected_date = datetime.strptime(query, '%Y-%m-%d').date()
                results = Food.objects.filter(best_before__lte=selected_date).order_by('best_before')
                if not results:
                    message = f"No food items expiring on or before {selected_date}."
            except ValueError:
                message = "Please enter a valid date in YYYY-MM-DD format."

    elif filter_type == 'category':
        # Case 3: Category filter
        if not query:
            message = "Please enter a category name."
        else:
            category_matches = Category.objects.filter(name__icontains=query)
            if category_matches.exists():
                results = Food.objects.filter(category__in=category_matches)
                if not results:
                    message = "No food items found in the matching categories."
            else:
                message = "No matching categories found."

    context = {
        'results': results,
        'message': message,
        'filter_type': filter_type,
        'query': query,
    }
    return render(request, 'inventory/search.html', context)


def shopping_view(request):
    return render(request, 'inventory/shopping.html')
