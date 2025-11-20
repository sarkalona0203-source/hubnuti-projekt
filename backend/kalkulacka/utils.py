from collections import defaultdict
from .models import MealPlan, RecipeIngredient

def shopping_list_for_mealplan(meal_plan_id):
    meal_plan = MealPlan.objects.get(id=meal_plan_id)
    totals = defaultdict(float)

    for item in meal_plan.items.all():
        for recipe_ing in item.jidlo.ingredients.all():
            totals[recipe_ing.ingredient, recipe_ing.ingredient.unit] += recipe_ing.amount * item.quantity

    shopping_list = sorted(
        [
            {"name": ingredient.name, "amount": amount, "unit": unit}
            for (ingredient, unit), amount in totals.items()
        ],
        key=lambda x: x["name"]
    )
    return shopping_list


# 👇 вызов функции и вывод — уже **вне функции**
shopping_list = shopping_list_for_mealplan(1)

for item in shopping_list:
    print(f"{item['name']}: {item['amount']} {item['unit']}")