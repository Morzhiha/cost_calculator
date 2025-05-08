from django.contrib import admin

from .models import Product, Unit, Recipe, RecipeIngredient


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('price_per_base_unit',)
    fields = ['name', 'total_price', 'total_quantity', 'unit', 'price_per_base_unit', 'owner']
    list_display = ['name', 'total_price', 'total_quantity', 'unit', 'price_per_base_unit']


admin.site.register(Product, ProductAdmin)
admin.site.register(Unit)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
