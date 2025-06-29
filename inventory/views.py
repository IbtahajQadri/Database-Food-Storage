from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from inventory.models import Category, Food
from datetime import date, timedelta
from django.utils.dateparse import parse_date
from django.db import IntegrityError
from django.db.models import Q, Sum
import logging

logger = logging.getLogger(__name__)


def dashboard(request):
    today = date.today()
    next_7_days = today + timedelta(days=7)

    # Summary stats
    total_categories = Category.objects.count()
    total_food_items = Food.objects.count()

    # Categories below ideal quantity
    categories_below_ideal = []
    for category in Category.objects.all():
        current_quantity = category.foods.aggregate(total=Sum('quantity'))['total'] or 0
        if current_quantity < category.ideal_quantity:
            categories_below_ideal.append({
                'category': category,
                'current_quantity': current_quantity,
                'ideal_quantity': category.ideal_quantity,
                'unit': category.unit,
                'quantity_needed': category.ideal_quantity - current_quantity
            })

    num_categories_below_ideal = len(categories_below_ideal)

    # Expiring soon food count per category (within next 7 days only)
    expiring_soon_summary = []
    for category in Category.objects.all():
        count = category.foods.filter(best_before__gt=today, best_before__lte=next_7_days).count()
        if count > 0:
            expiring_soon_summary.append({
                'category__name': category.name,
                'count': count
            })

    # Bar chart data
    chart_labels = []
    chart_current = []
    chart_ideal = []
    for category in Category.objects.all():
        current_quantity = category.foods.aggregate(total=Sum('quantity'))['total'] or 0
        chart_labels.append(category.name)
        chart_current.append(round(current_quantity, 2))
        chart_ideal.append(round(category.ideal_quantity, 2))

    context = {
        'total_categories': total_categories,
        'total_food_items': total_food_items,
        'num_categories_below_ideal': num_categories_below_ideal,
        'expiring_soon_summary': expiring_soon_summary,
        'low_stock_categories': sorted(categories_below_ideal, key=lambda x: x['quantity_needed'], reverse=True)[:5],
        'chart_labels': chart_labels,
        'chart_current': chart_current,
        'chart_ideal': chart_ideal,
    }

    return render(request, 'inventory/dashboard.html', context)


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
                    elif Category.objects.filter(name__iexact=name).exists():
                        error_message = "Category name must be unique (case-insensitive)."
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
                        # Check for duplicates ignoring the current category itself
                        if Category.objects.filter(name__iexact=name).exclude(pk=category.pk).exists():
                            error_message = "Category name must be unique (case-insensitive)."
                        else:
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

def search_view(request, slug=None):
    food_items = []
    item_count = 0
    message = "food item fetched succesfully"
    search = request.GET.get('search', '').strip()
    if slug=="category":
        food_items = Food.objects.filter(category__name__icontains=search)
    elif slug == "best_before_date":
        expires_before_date = parse_date(search)
        if expires_before_date:
            food_items = Food.objects.filter(best_before__lte=expires_before_date)
        else: 
            message = "Invalid date format"
    else:
        food_items = Food.objects.filter(
                Q(name__icontains=search) | 
                Q(category__name__icontains=search)
            )
    if not slug and not search or not food_items:
        food_items = Food.objects.all()
    item_count = food_items.count()

    return render(request, 'inventory/search.html', {'items': food_items, 'item_count': item_count, 'message': message})

def shopping_view(request):
    categories = Category.objects.all()
    shopping_items = []
    
    for category in categories:
        if category.is_low_stock:
            needed_quantity = category.ideal_quantity - category.current_quantity
            shopping_items.append({
                'category_name': category.name,
                'current_quantity': category.current_quantity,
                'ideal_quantity': category.ideal_quantity,
                'needed_quantity': needed_quantity
            })
    return render(request, 'inventory/shopping.html', {'shopping_items': shopping_items, 'item_count': len(shopping_items)})
