from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.db.models import Sum, F, FloatField
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
class Profile(models.Model):
    saved_plan = models.JSONField(default=dict, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("muz", "Muž"), ("zena", "Žena")], default="muz")
# === Прогресс пользователя (вес + заметки) ===
class ProgressRecord(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="progress_records")
    date = models.DateField(default=timezone.now)
    weight = models.FloatField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.weight} kg"

# === Ингредиенты ===
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
    price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


# === Блюдо ===
class Jidlo(models.Model):
    TYPY = [
        ("snidane", "Snídaně"),
        ("druhe_snidane", "Druhá snídaně"),
        ("obed", "Oběd"),
        ("svacina", "Svačina"),
        ("vecere", "Večeře"),
        ("snack_extra", "Extra snack"),
    ]

    name = models.CharField(max_length=100)
    calories = models.FloatField(default=0.0, editable=False)
    protein = models.FloatField(default=0.0, editable=False)
    fat = models.FloatField(default=0.0, editable=False)
    carbs = models.FloatField(default=0.0, editable=False)
    type = models.CharField(max_length=20, choices=TYPY)
    preparation = models.TextField()
    obrazek_url = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def total_weight(self):
        return sum(ri.amount for ri in self.ingredients.all())

    @property
    def ready_price(self):
        if hasattr(self, "ready_price_value"):
            return round(self.ready_price_value, 2)
        total_price = self.ingredients.aggregate(
            total=Sum(
                F("ingredient__price") * F("amount") / 100.0,
                output_field=FloatField(),
            )
        )["total"] or 0.0
        return round(total_price * 1.6, 2)

    def optimize_image(self):
        if self.obrazek and self.obrazek.path:
            try:
                with Image.open(self.obrazek.path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((800, 800))
                    img.save(self.obrazek.path, format="JPEG", quality=80, optimize=True)
            except Exception as e:
                print(f"Ошибка при оптимизации изображения: {e}")

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


# === Связка рецепта и ингредиента ===
class RecipeIngredient(models.Model):
    jidlo = models.ForeignKey(Jidlo, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField()
    unit = models.CharField(max_length=20, default="g")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.jidlo.calories, self.jidlo.protein, self.jidlo.fat, self.jidlo.carbs = self.jidlo.recalc_macros_and_calories()
        self.jidlo.save(update_fields=['calories', 'protein', 'fat', 'carbs'])

    def delete(self, *args, **kwargs):
        jidlo = self.jidlo
        super().delete(*args, **kwargs)
        jidlo.calories, jidlo.protein, jidlo.fat, jidlo.carbs = jidlo.recalc_macros_and_calories()
        jidlo.save(update_fields=['calories', 'protein', 'fat', 'carbs'])


# === План питания (Premium) ===
class MealPlan(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="Plán")
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
        if self.profile:
            return f"{self.name} ({self.profile.first_name} {self.profile.last_name})"
        return self.name

# === Элемент плана (день / тип еды) ===
class MealItem(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="items")
    jidlo = models.ForeignKey(Jidlo, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)
    day = models.CharField(max_length=20, default="pondeli")
    type = models.CharField(max_length=20, default="obed")

    def __str__(self):
        return f"{self.day.title()} - {self.type} - {self.jidlo.name} x {self.quantity}"