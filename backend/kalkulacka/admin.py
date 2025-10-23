from django.contrib import admin
from django.utils.html import format_html
from .models import Jidlo, Ingredient, RecipeIngredient, MealPlan, MealItem


@admin.register(Jidlo)
class JidloAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "calories", "obrazek_preview")  # 👈 добавили превью
    search_fields = ("name",)
    list_filter = ("type",)

    def obrazek_preview(self, obj):
        if obj.obrazek:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;" />',
                obj.obrazek.url)
        return "—"

    obrazek_preview.short_description = "Obrázek"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "calories_per_100g")


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("jidlo", "ingredient", "amount", "unit")


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")


@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ("meal_plan", "jidlo", "day", "type", "quantity")
# Register your models here.
