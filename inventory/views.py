from django.shortcuts import render

def dashboard(request):
    return render(request, 'inventory/dashboard.html')

def category_view(request):
    return render(request, 'inventory/category.html')

def food_view(request):
    return render(request, 'inventory/food.html')

def search_view(request):
    return render(request, 'inventory/search.html')

def shopping_view(request):
    return render(request, 'inventory/shopping.html')


