from rest_framework import serializers
from .models import Ingredient, Jidlo, RecipeIngredient, MealPlan, MealItem
from rest_framework.renderers import JSONRenderer
import json

# Кастомный рендерер для красивого JSON
class MyRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        return response_data.encode("utf-8")

# Сериализатор для ингредиентов
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            "id", "name", "calories_per_100g",
            "protein_per_100g", "fat_per_100g", "carbs_per_100g"
        ]

# Сериализатор для связи Jidlo <-> Ingredient
class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)
    unit = serializers.CharField(source="ingredient.unit", read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient_name', 'amount', 'unit']


class JidloSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)


    class Meta:
        model = Jidlo
        fields = ["id", "name", "calories", "protein", "fat", "carbs", "preparation", "ingredients"]


class MealItemSerializer(serializers.ModelSerializer):
    jidlo = JidloSerializer(read_only=True)

    class Meta:
        model = MealItem
        fields = ["id", "jidlo", "quantity", "day"]


class MealPlanSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)

    class Meta:
        model = MealPlan
        fields = ["id", "name", "created_at", "items"]