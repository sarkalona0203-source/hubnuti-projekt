from django.db import models
from PIL import Image
import os

class Ingredient(models.Model):
    CATEGORY_CHOICES = [
        ("maso", "Maso"),
        ("ryba", "Ryby"),
        ("mlecne", "Mléčné výrobky"),
        ("obiloviny", "Obiloviny a kaše"),
        ("ovoce", "Ovoce"),
        ("zelenina", "Zelenina"),
        ("syry", "Sýry"),
        ("tuky", "Oleje a tuky"),
        ("ostatni", "Ostatní"),
    ]

    name = models.CharField(max_length=255)
    calories_per_100g = models.FloatField()
    protein_per_100g = models.FloatField()
    fat_per_100g = models.FloatField()
    carbs_per_100g = models.FloatField()
    unit = models.CharField(max_length=20, default="g")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="ostatni")

    def __str__(self):
        return f"{self.name} ({self.category})"


class Jidlo(models.Model):
    TYPY = [
        ("snidane", "Snídaně"),
        ("druhe_snidane", "Druhá snídaně"),
        ("obed", "Oběd"),
        ("svacina", "Svačina"),
        ("vecere", "Večeře"),
    ]

    name = models.CharField(max_length=100)
    calories = models.FloatField(default=0.0, editable=False)
    protein = models.FloatField(default=0.0, editable=False)
    fat = models.FloatField(default=0.0, editable=False)
    carbs = models.FloatField(default=0.0, editable=False)
    type = models.CharField(max_length=20, choices=TYPY)
    preparation = models.TextField()
    obrazek = models.ImageField(upload_to='jidla/', blank=True, null=True)  # <---

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.obrazek:
            img_path = self.obrazek.path
            with Image.open(img_path) as img:
                max_size = (800, 800)  # 🔹 максимум 800x800 пикселей
                img.thumbnail(max_size)
                img.save(img_path, quality=80, optimize=True)


    def recalc_macros_and_calories(self):
        kcal = protein = fat = carbs = 0.0
        for ri in self.ingredients.all():
            factor = ri.amount / 100
            ingr = ri.ingredient
            kcal += ingr.calories_per_100g * factor
            protein += ingr.protein_per_100g * factor
            fat += ingr.fat_per_100g * factor
            carbs += ingr.carbs_per_100g * factor
        return round(kcal, 1), round(protein, 1), round(fat, 1), round(carbs, 1)

    def get_macros_display(self):
        return f"{self.calories} kcal | B: {self.protein} g, T: {self.fat} g, S: {self.carbs} g"

    def __str__(self):
        return f"{self.name} ({self.get_macros_display()})"


class RecipeIngredient(models.Model):
    jidlo = models.ForeignKey(Jidlo, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField()
    unit = models.CharField(max_length=20, default="g")  # ← добавляем поле

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.jidlo.calories, self.jidlo.protein, self.jidlo.fat, self.jidlo.carbs = self.jidlo.recalc_macros_and_calories()
        self.jidlo.save(update_fields=['calories', 'protein', 'fat', 'carbs'])

    def delete(self, *args, **kwargs):
        jidlo = self.jidlo
        super().delete(*args, **kwargs)
        jidlo.calories, jidlo.protein, jidlo.fat, jidlo.carbs = jidlo.recalc_macros_and_calories()
        jidlo.save(update_fields=['calories', 'protein', 'fat', 'carbs'])


class MealPlan(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(null=True, blank=True)

    def total_macros(self):
        kcal = protein = fat = carbs = 0.0
        for item in self.items.all():
            kcal += item.jidlo.calories * item.quantity
            protein += item.jidlo.protein * item.quantity
            fat += item.jidlo.fat * item.quantity
            carbs += item.jidlo.carbs * item.quantity
        return {
            "calories": round(kcal, 1),
            "protein": round(protein, 1),
            "fat": round(fat, 1),
            "carbs": round(carbs, 1),
        }

    def __str__(self):
        return self.name

class MealItem(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="items")
    jidlo = models.ForeignKey(Jidlo, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)
    day = models.CharField(max_length=20, default="pondeli")
    type = models.CharField(max_length=20, default="obed")  # 👈 ДОБАВЬ ЭТО ПОЛЕ

    def __str__(self):
        return f"{self.day.title()} - {self.type} - {self.jidlo.name} x {self.quantity}"

