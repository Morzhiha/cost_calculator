from .models import Recipe, Product


def getRecipe(id):
    return Recipe.objects.get(id=id)


def getAllProducts(user_id):
    return Product.objects.filter(owner=user_id).values('id', 'name', 'unit__short_name', 'price_per_base_unit')


def getAllRecipes(user_id):
    return Recipe.objects.filter(owner=user_id)