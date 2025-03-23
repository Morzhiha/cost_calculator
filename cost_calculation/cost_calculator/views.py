from django.shortcuts import render


def homepage(request):

    return render(request, 'start_page.html',
                  {'title': 'Домашняя страница'})

def catalog_products(request):
    return render(request, 'catalog_products.html',
                  )


def catalog_recipes(request):
    return render(request, 'catalog_recipes.html',)


def create_recipe(request):

    return render(request, 'create_recipe.html',
                  {'title': 'Создание рецепта'})


def edit_recipe(request):
    pass


def delete_recipe(request):
    pass


def calculate_recipe(request):
    # recipe = getRecipe()
    recipe = {'ingredients': [{'name': 'Мука', 'weight': '100',  'unit': 'гр', 'price': '80'},
                              {'name': 'Сахар', 'weight': '50',  'unit': 'гр', 'price': '60'}]}
    return render(request, 'calculate_recipe.html',
                  {'title': 'Подсчет себестоимости',
                   'recipe': recipe,
                   })
