from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from .bd_service import *
from .forms import *
from .models import *


def homepage(request):

    return render(request, 'start_page.html',
                  {'title': 'Домашняя страница'})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('homepage')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'registration/profile.html')


def check_product_exists(request):
    if request.method == 'GET':
        name = request.GET.get('name', '')
        exists = Product.objects.filter(name=name, owner=request.user).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})


@login_required
def product_catalog(request):
    """
    Отображает список добавленных продуктов
    :param request:
    :return:
    """
    products = Product.objects.filter(owner=request.user)
    form = ProductForm()
    return render(request, 'product_catalog.html', {
        'title': 'Каталог продуктов',
        'products': products,
        'form': form
    })


@login_required
@require_http_methods(["POST"])
def create_product(request):
    """Создание нового продукта"""
    form = ProductForm(request.POST, user=request.user)

    if form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'total_price': product.total_price,
            'total_quantity': product.total_quantity,
            'unit': product.unit.short_name,
        })

    return JsonResponse({'error': form.errors}, status=400)


@login_required
@require_http_methods(["POST"])
def update_product(request, pk):
    """Обновление существующего продукта"""
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    form = ProductForm(request.POST, instance=product, user=request.user)

    if form.is_valid():
        product = form.save()
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'total_price': product.total_price,
            'total_quantity': product.total_quantity,
            'unit': product.unit.short_name,
        })
    return JsonResponse({'error': form.errors}, status=400)


@login_required
@require_http_methods(["DELETE"])
def delete_product(request, pk):
    """Удаление продукта с проверкой на использование в рецептах"""
    product = get_object_or_404(Product, pk=pk, owner=request.user)

    try:
        product.delete()
        return JsonResponse({'success': True})
    except ProtectedError:
        return JsonResponse({
            'error': 'Нельзя удалить продукт, так как он используется в рецептах'
        }, status=400)


@login_required
def recipe_catalog(request):
    return render(request, 'recipe_catalog.html', {
        'title': 'Каталог рецептов',
        'recipes': getAllRecipes(request.user),
    })


@login_required
def recipe_edit(request, recipe_id=None):
    RecipeIngredientFormSet = formset_factory(RecipeIngredientForm, extra=1)

    is_edit = recipe_id is not None
    recipe = get_object_or_404(Recipe, pk=recipe_id, owner=request.user) if is_edit else None

    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, instance=recipe)
        ingredients_formset = RecipeIngredientFormSet(
            request.POST,
            prefix='ingredients',
            initial=[{'product': i.product, 'quantity': i.quantity} for i in
                     recipe.recipeingredient_set.all()] if is_edit else None
        )

        if recipe_form.is_valid() and ingredients_formset.is_valid():
            recipe = recipe_form.save(commit=False)
            if not is_edit:
                recipe.owner = request.user
            recipe.save()

            if is_edit:
                recipe.recipeingredient_set.all().delete()

            for form in ingredients_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    ingredient = form.save(commit=False)
                    ingredient.recipe = recipe
                    ingredient.save()

            return JsonResponse({'redirect': f'/recipes/'})

        return JsonResponse({'errors': {
            'recipe': recipe_form.errors,
            'ingredients': ingredients_formset.errors
        }}, status=400)

    initial_ingredients = [
        {'product': i.product.id, 'quantity': i.quantity}
        for i in recipe.recipeingredient_set.all()
    ] if is_edit else None

    formset = RecipeIngredientFormSet(
        prefix='ingredients',
        initial=initial_ingredients
    )

    return render(request, 'recipe_create.html', {
        'recipe_id': recipe_id,
        'edit_mode': is_edit,
        'products': list(getAllProducts(request.user)),
        'recipe_form': RecipeForm(instance=recipe),
        'ingredient_formset': formset
    })


@login_required
def recipe_delete(request, recipe_id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, pk=recipe_id, owner=request.user)
        recipe.recipeingredient_set.all().delete()
        recipe.delete()
        return redirect('recipes')
    return JsonResponse({'error': 'Invalid request'}, status=400)

