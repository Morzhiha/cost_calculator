from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import *


class AuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label
            })


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label
            })


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['owner', 'price_per_base_unit']
        error_messages = {
            'name': {
                'required': 'Поле обязательно для заполнения.',
                'max_length': 'Название слишком длинное (максимум %(limit_value)d символов).',
            },
            'total_quantity': {
                'required': 'Поле обязательно для заполнения.',
                'invalid': 'Введите корректное число (например, 1.5 или 10).',
            },
            'total_price': {
                'required': 'Поле обязательно для заполнения.',
                'invalid': 'Введите корректную цену (например, 100.50).',
            },
            'unit': {
                'required': 'Выберите единицу измерения.',
            },
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.user:
            qs = Product.objects.filter(name=name, owner=self.user)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Продукт с таким названием уже существует.")
        return name

    def clean_total_quantity(self):
        total_quantity = self.cleaned_data['total_quantity']
        if total_quantity <= 0:
            raise ValidationError("Количество должно быть положительным числом")
        return total_quantity

    def clean_total_price(self):
        total_price = self.cleaned_data['total_price']
        if total_price < 0:
            raise ValidationError("Цена не может быть отрицательной")
        return total_price


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'weight']


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01', 'min': '0'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()
