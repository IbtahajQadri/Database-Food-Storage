from django.shortcuts import render, get_object_or_404
from .models import Category
from django.db import IntegrityError
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
                category.delete()
                success_message = "Category deleted successfully!"
                logger.info(f"Category deleted: ID {category_id}")

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
    return render(request, 'inventory/food.html')

def search_view(request):
    return render(request, 'inventory/search.html')

def shopping_view(request):
    return render(request, 'inventory/shopping.html')


