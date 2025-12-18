from django.contrib import admin
from .models import InventoryLog

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'action', 'quantity', 'previous_stock', 'new_stock', 'created_by', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['product__name', 'notes']
    readonly_fields = ['created_at']
