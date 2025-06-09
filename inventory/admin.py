from django.contrib import admin
from inventory.models import Food, Category
# Register your models here.

@admin.register(Food)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'best_before', 'expiry_status']
    list_filter = ['category', 'best_before']
    search_fields = ['name', 'brand', 'notes']
    readonly_fields = ['days_until_expiry', 'is_expired', 'expiry_status']
    date_hierarchy = 'best_before'
    
    def expiry_status(self, obj):
        status = obj.expiry_status
        if "Expired" in status:
            return f"🚨 {status}"
        elif "Today" in status or "day" in status:
            return f"⚠️ {status}"
        else:
            return f"✅ {status}"
    expiry_status.short_description = 'Expiry Status'
    
    def get_queryset(self, request):
        """Order by expiry date by default"""
        qs = super().get_queryset(request)
        return qs.order_by('best_before')

@admin.register(Category)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'ideal_quantity', 'current_quantity', 'quantity_difference', 'is_low_stock']
    # list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['current_quantity', 'quantity_difference', 'is_low_stock']
    
    def current_quantity(self, obj):
        return obj.current_quantity
    current_quantity.short_description = 'Current Stock'
    
    def quantity_difference(self, obj):
        diff = obj.quantity_difference
        if diff < 0:
            return f"{diff} (Low Stock)"
        elif diff == 0:
            return "0 (Ideal)"
        else:
            return f"+{diff} (Overstocked)"
    quantity_difference.short_description = 'Stock Status'