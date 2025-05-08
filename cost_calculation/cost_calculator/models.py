from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название единицы измерения')
    short_name = models.CharField(max_length=10, verbose_name='Сокращение', blank=True)
    conversion_factor = models.DecimalField(
        max_digits=10, decimal_places=4, default=1, verbose_name="Коэффициент перевода в базовую единицу"
    )

    def __str__(self):
        return self.name


# class ProductCategory(models.Model):
#     name = models.CharField(max_length=255, verbose_name='Название категории продукта')
#     description = models.TextField(blank=True, verbose_name='Описание')
#
#     def __str__(self):
#         return self.name
#
#
# class RecipeCategory(models.Model):
#     name = models.CharField(max_length=255, verbose_name='Название категории рецепта')
#     description = models.TextField(blank=True, verbose_name='Описание')
#
#     def __str__(self):
#         return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название продукта')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость упаковки', default=0)
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество в упаковке',
                                         default=0)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name='Единица измерения')
    price_per_base_unit = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='Цена за базовую единицу',
                                              editable=False, default=0)
    # owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True,
    #                              verbose_name='Категория продукта')
    # class Meta:
    #     unique_together = ('name', 'owner')


    def save(self, *args, **kwargs):
        if self.total_quantity > 0:
            self.price_per_base_unit = self.total_price / (self.total_quantity * self.unit.conversion_factor)
        else:
            self.price_per_base_unit = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название рецепта')
    description = models.TextField(blank=True, verbose_name="Описание")
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Вес готового изделия')
    # owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def get_total_cost(self):
        return sum(ingredient.get_cost for ingredient in self.recipeingredient_set.all())


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Продукт')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')

    def __str__(self):
        return f'{self.quantity} {self.product.unit} {self.product.name} {self.recipe.name}'

    @property
    def get_cost(self):
        return self.quantity * self.product.price_per_base_unit
