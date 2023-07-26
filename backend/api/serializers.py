import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer
from users.models import User
from recipes.models import (Recipe, Ingredient, Tag, RecipeIngredient,
                            Follow, Favorite, ShoppingList)

MIN_VALUE = 1
MAX_VALUE = 32000


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'password')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        queryset = obj.amounts
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorite_user.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shop_user.filter(recipe=obj).exists()


class IngredientAddSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate(self, data):
        amount = data.get('amount')
        if not MIN_VALUE <= int(amount) <= MAX_VALUE:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть от 1 до 32000!')
        return data


class RecipeAddSerializer(serializers.ModelSerializer):
    ingredients = IngredientAddSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate(self, data):
        cooking_time = data['cooking_time']
        if not (MIN_VALUE <= cooking_time <= MAX_VALUE):
            raise serializers.ValidationError(
                'Количество должно быть в диапазоне от 1 до 32000!')
        ingredients = data.get('ingredients')
        if len(ingredients) < 1:
            raise serializers.ValidationError(
                'В рецепте должен быть хотя бы 1 ингредиент!')
        unique_ingredients = set()
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            unique_ingredients.add(ingredient_id)
        if len(ingredients) != len(unique_ingredients):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными!')

        tags = data.get('tags')
        if len(tags) < 1:
            raise serializers.ValidationError(
                'У рецепта должен быть хотя бы 1 тег!')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными!')
        return data

    @staticmethod
    def create_recipe_ingredient(ingredients, recipe):
        ingredients_list = []
        for ingredient in ingredients:
            RIobj = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            ingredients_list.append(RIobj)
        RecipeIngredient.objects.bulk_create(ingredients_list)

    @staticmethod
    def create_recipe_tag(tags_list, recipe):
        for tag in tags_list:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author_id = self.context.get('request').user.id
        author = User.objects.get(id=author_id)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)

        self.create_recipe_ingredient(ingredients, recipe)
        self.create_recipe_tag(tags, recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        instance.amounts.all().delete()
        instance.recipe_tag.all().delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        self.create_recipe_ingredient(ingredients, instance)
        self.create_recipe_tag(tags, instance)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'recipes', 'recipes_count', 'is_subscribed')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = self.context.get(
            'request').query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class FollowAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, data):
        author = data.get('author')
        user = data.get('user')
        if author == user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        if user.follower.filter(author=author).exists():
            raise serializers.ValidationError(
                'Подписка на этого автора уже существует!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowSerializer(instance.author, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if user.favorite_user.filter(recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже есть в избранном!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(instance.recipe, context=context).data


class ShoppingListSerializer(FavoriteSerializer):

    class Meta:
        model = ShoppingList
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if user.shop_user.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже есть в списке покупок!')
        return data
