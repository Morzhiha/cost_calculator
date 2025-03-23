from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название единицы измерения')

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название продукта')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость за единицу')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name='Единица измерения')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название рецепта')
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость за единицу')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Продукт')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')

    def __str__(self):
        return f'{self.quantity} {self.product.unit} {self.product.name} {self.recipe.name}'
