from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User

MIN_VALUE = 1
MAX_VALUE = 32000


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=250)
    measurement_unit = models.CharField('Единицы измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'], name='unique ingredient')]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField('Название', unique=True, max_length=250)
    color = models.CharField('Цвет', unique=True, max_length=7)
    slug = models.SlugField('Slug', unique=True, max_length=50)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
        constraints = [models.UniqueConstraint(
            fields=['name', 'color', 'slug'], name='unique tag')]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингридиенты',
        related_name='recipes'
    )
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(
                MIN_VALUE, message='Время не может быть меньше 1-й минуты!'),
            MaxValueValidator(
                MAX_VALUE, message='Время не может быть больше 32000 минут!')
        ),
    )
    pub_date = models.DateTimeField(
        'Дата публикации', default=timezone.now)

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [models.UniqueConstraint(
            fields=['author', 'name'], name='unique recipe')]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='amounts'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='amounts'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                MIN_VALUE, message='Количество не может быть меньше 1-го!'),
            MaxValueValidator(
                MAX_VALUE, message='Количество не может быть больше 32000!')
        ),
    )

    class Meta:
        verbose_name = 'Рецепт-Ингредиент'
        verbose_name_plural = 'Рецепт-Ингредиент'
        ordering = ['-id']

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_tag'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        related_name='recipe_tag'
    )

    class Meta:
        verbose_name = 'Рецепт-Тег'
        verbose_name_plural = 'Рецепт-Тег'
        ordering = ['-id']

    def __str__(self):
        return f'{self.recipe} - {self.tag}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-author_id']
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique follow')]

    def __str__(self):
        return f'{self.user} - {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['-recipe_id']
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique favorite')]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shop_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shop_recipe'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ['-recipe_id']
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique shopping list')]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
