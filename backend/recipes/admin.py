from django.contrib import admin

from .models import (Recipe, Ingredient, Tag, RecipeIngredient, RecipeTag,
                     Follow, Favorite, ShoppingList)


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'text', 'cooking_time',
                    'is_favorited')
    list_filter = ('name', 'author', 'tags')
    ordering = ['id']
    inlines = (RecipeIngredientInline,)

    def is_favorited(self, obj):
        return len(Favorite.objects.filter(recipe=obj))


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    ordering = ['id']


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    ordering = ['id']


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
