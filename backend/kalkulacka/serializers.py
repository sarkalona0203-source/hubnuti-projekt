from rest_framework import serializers
from .models import Ingredient, Jidlo, RecipeIngredient, MealPlan, MealItem, ProgressRecord
from rest_framework.renderers import JSONRenderer
import json
import os
class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressRecord
        fields = ["id", "date", "weight", "note"]  # 🩵 убрал лишний пробел после "note"
        read_only_fields = ["id", "date"]  # дата создаётся автоматически на сервере
# Кастомный рендерер для красивого JSON
class MyRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        return response_data.encode("utf-8")

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            "id", "name", "calories_per_100g",
            "protein_per_100g", "fat_per_100g", "carbs_per_100g"
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)
    unit = serializers.CharField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient_name', 'amount', 'unit']


class JidloSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    # 🔹 значения, вычисленные в queryset через annotate()
    price_value = serializers.FloatField(read_only=True)
    ready_price_value = serializers.FloatField(read_only=True)

    # SerializerMethodField для корректного URL картинки
    obrazek_url = serializers.SerializerMethodField(method_name="get_obrazek_url")

    class Meta:
        model = Jidlo
        fields = [
            "id", "name", "type", "calories", "protein", "fat", "carbs",
            "preparation", "ingredients", "price_value", "ready_price_value",
            "obrazek_url"
        ]

    def get_obrazek_url(self, obj):
        request = self.context.get("request")
        if obj.obrazek_url:
            url = obj.obrazek_url
            if request:
                url = request.build_absolute_uri(url)
            return url
        return None
    def get_price(self, obj):
        total_price = sum(
            (ri.ingredient.price or 0) * (ri.amount / 100)
            for ri in obj.ingredients.all()
        )
        return round(total_price, 2)

    def get_total_price(self, obj):
        if hasattr(obj, "total_price") and obj.total_price is not None:
            return round(float(obj.total_price), 2)
        return self.get_price(obj)


class MealItemSerializer(serializers.ModelSerializer):
    jidlo = serializers.SerializerMethodField()

    class Meta:
        model = MealItem
        fields = ["id", "jidlo", "quantity", "day", "type"]

    def get_jidlo(self, obj):
        # Передаем context, чтобы JidloSerializer имел доступ к request
        return JidloSerializer(obj.jidlo, context=self.context).data

class MealPlanSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)

    class Meta:
        model = MealPlan
        fields = ["id", "name", "created_at", "items"]