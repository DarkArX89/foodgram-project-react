# Generated by Django 3.2 on 2023-07-20 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_edit_recipes_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipetag',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_tag', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_tag', to='recipes.tag', verbose_name='Тег'),
        ),
    ]
