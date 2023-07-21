from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, IngredientViewSet, TagViewSet,
                    FollowViewSet, APIFollowAddDelete, APIFaforiteAddDelete,
                    APIShoppingListAddDelete)


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('tags', TagViewSet)

urlpatterns = [
    path('users/subscriptions/', FollowViewSet.as_view({'get': 'list'})),
    path('users/<int:id>/subscribe/', APIFollowAddDelete.as_view()),
    path('recipes/<int:id>/favorite/', APIFaforiteAddDelete.as_view()),
    path('recipes/<int:id>/shopping_cart/',
         APIShoppingListAddDelete.as_view()),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
