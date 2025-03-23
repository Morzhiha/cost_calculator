from .models import Recipe


def getRecipe(id):
    return Recipe.objects.get(id=id)