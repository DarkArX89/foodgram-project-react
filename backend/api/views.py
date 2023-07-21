import io

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from recipes.models import (Recipe, Ingredient, Tag, Favorite, ShoppingList,
                            RecipeIngredient)
from users.models import User
from .serializers import (RecipeSerializer, RecipeAddSerializer,
                          IngredientSerializer, TagSerializer,
                          FollowSerializer, ShoppingListSerializer,
                          FollowAddSerializer, FavoriteSerializer)
from .permissions import AuthorOrAdminOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        queryset = Recipe.objects.all()
        limit = self.request.query_params.get('limit')
        author = self.request.query_params.get('author')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        tags = dict(self.request.query_params).get('tags')
        if limit:
            queryset = queryset[:int(limit)]
        if author:
            queryset = queryset.filter(author=author)
        if tags:
            tags_id = []
            for tag in tags:
                tags_id.append(get_object_or_404(Tag, slug=tag))
            queryset = queryset.filter(tags__in=tags_id)
        if is_favorited:
            favorited = Favorite.objects.filter(user=self.request.user)
            favorited_name_list = []
            for favorite in favorited:
                favorited_name_list.append(favorite.recipe)
            queryset = queryset.filter(name__in=favorited_name_list)
        if is_in_shopping_cart:
            shopping_cart = ShoppingList.objects.filter(
                user=self.request.user)
            shopping_cart_list = []
            for element in shopping_cart:
                shopping_cart_list.append(element.recipe)
            queryset = queryset.filter(name__in=shopping_cart_list)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeSerializer
        return RecipeAddSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__shop_recipe__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount')
        for ingredient in ingredients:
            if ingredient[0] not in shopping_list:
                shopping_list[ingredient[0]] = {
                    'measurement_unit': ingredient[1],
                    'amount': ingredient[2]
                }
            else:
                shopping_list[ingredient[0]]['amount'] += ingredient[2]
        text = ''
        for key, value in shopping_list.items():
            text += (f"{key} ({value['measurement_unit']}) - "
                     f"{value['amount']}\n")
        # file_path = 'shopping_list.txt'
        # file = open(file_path, 'w')
        # file.write(text)
        # file.close()
        # file = open(file_path, 'r')
        buffer = io.StringIO()
        buffer.write(text)
        response = HttpResponse(buffer.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt')
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class FollowViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        queryset = User.objects.filter(following__user=self.request.user)
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        return queryset


class APIFollowAddDelete(APIView):
    serializer_class = FollowAddSerializer
    model = User
    data_keys = ('user', 'author')

    def post(self, request, id):
        obj = get_object_or_404(self.model, id=id)
        serializer = self.serializer_class(
            data={self.data_keys[0]: request.user.id,
                  self.data_keys[1]: obj.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(self.model, id=id)
        user = request.user
        follow = user.follower.filter(author=author).first()
        if not follow:
            return Response(
                {'error': 'Подписка на этого автора не существует!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIFaforiteAddDelete(APIFollowAddDelete):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer
    model = Recipe
    data_keys = ('user', 'recipe')

    def delete(self, request, id):
        recipe = get_object_or_404(self.model, id=id)
        user = request.user
        favorite = user.favorite_user.filter(recipe=recipe).first()
        if not favorite:
            return Response(
                {'error': 'Этого рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIShoppingListAddDelete(APIFaforiteAddDelete):
    serializer_class = ShoppingListSerializer

    def delete(self, request, id):
        recipe = get_object_or_404(self.model, id=id)
        user = request.user
        shopping_object = user.shop_user.filter(recipe=recipe).first()
        if not shopping_object:
            return Response(
                {'error': 'Этого рецепта нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
