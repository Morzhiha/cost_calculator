from django.contrib import admin

from .models import Product, Unit, Recipe, RecipeIngredient

admin.site.register(Product)
admin.site.register(Unit)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
