from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Jidlo, MealPlan
import random
from collections import defaultdict
from .models import Jidlo
from .serializers import JidloSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def vsechna_jidla(request):
    jidla = Jidlo.objects.all()
    serializer = JidloSerializer(jidla, many=True, context={'request': request})
    return Response(serializer.data)
def find_best_snidane_combo(snidane_list, druhe_snidane_list, svacina_list, target_kcal, fixed_kcal, max_attempts=500):
    best_combo = None
    smallest_diff = float("inf")

    for _ in range(max_attempts):
        sn = random.choice(snidane_list)
        ds = random.choice(druhe_snidane_list)
        sv = random.choice(svacina_list)

        total = float(sn.calories or 0) + float(ds.calories or 0) + float(sv.calories or 0)
        total += fixed_kcal
        diff = abs(target_kcal - total)

        if diff < smallest_diff:
            best_combo = [sn, ds, sv]
            smallest_diff = diff

            if diff <= 50:
                break

    return best_combo


@csrf_exempt
def vypocet(request):
    if request.method != "POST":
        return JsonResponse({"error": "Pouze metoda POST je povolena."})

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Neplatný JSON vstup."})

    manual = data.get("manual_calories")
    save = data.get("save")

    if manual:
        try:
            daily_calories = int(manual)
        except ValueError:
            return JsonResponse({"error": "Neplatná hodnota kalorií."})
    else:
        try:
            vaha = float(data.get("vaha"))
            vyska = float(data.get("vyska"))
            vek = float(data.get("vek"))
            pohlavi = data.get("pohlavi", "muz")
            aktivita = data.get("aktivita", "sedavy")

            if pohlavi == "muz":
                bmr = 10 * vaha + 6.25 * vyska - 5 * vek + 5
            else:
                bmr = 10 * vaha + 6.25 * vyska - 5 * vek - 161

            aktivita_map = {
                "sedavy": 1.2,
                "lehka": 1.375,
                "stredni": 1.55,
                "vysoka": 1.725,
                "extra": 1.9,
            }
            tdee = bmr * aktivita_map.get(aktivita, 1.2)
            daily_calories = round(tdee - 500)
        except Exception:
            return JsonResponse({"error": "Neplatné vstupní údaje."})

    # Загрузка всех типов еды
    snidane = list(Jidlo.objects.filter(type="snidane"))
    druhe_snidane = list(Jidlo.objects.filter(type="druhe_snidane"))
    obedy = list(Jidlo.objects.filter(type="obed"))
    svaciny = list(Jidlo.objects.filter(type="svacina"))
    vecere = list(Jidlo.objects.filter(type="vecere"))

    if not (snidane and druhe_snidane and obedy and svaciny and vecere):
        return JsonResponse({"error": "Chybí jídla v databázi."})

        # --- Комбинации по дням недели ---
    KOMBINACE_DNU = {
        "kombinace_A": ["pondeli", "utery", "ctvrtek"],
        "kombinace_B": ["streda", "patek"],
        "kombinace_C": ["sobota", "nedele"],
    }

    # Сопоставление дня и его комбинации (например, "pondeli" → "kombinace_A")
    day_to_combo = {d: k for k, v in KOMBINACE_DNU.items() for d in v}

    # Комбинации обедов и ужинов
    kombinace_jidel = {
        "kombinace_A": (obedy[0], vecere[0]),
        "kombinace_B": (
            obedy[1] if len(obedy) > 1 else obedy[0],
            vecere[1] if len(vecere) > 1 else vecere[0],
        ),
        "kombinace_C": (obedy[-1], vecere[-1]),
    }

    # Комбинации завтраков (например, первые 3 завтрака — для комбинации A)
    kombinace_snidane = {
        "kombinace_A": snidane[:3],
        "kombinace_B": snidane[3:6] if len(snidane) > 5 else snidane[:3],
        "kombinace_C": snidane[-3:] if len(snidane) > 2 else snidane[:3],
    }

    days = ["pondeli", "utery", "streda", "ctvrtek", "patek", "sobota", "nedele"]
    plan_data = {}
    weekly_kcal = 0
    all_jidla = []

    for day in days:
        kombinace = day_to_combo.get(day, "kombinace_A")
        obed, vecere_item = kombinace_jidel[kombinace]
        fixed_kcal = float(obed.calories or 0) + float(vecere_item.calories or 0)

        # ❗ Здесь исправлено — используется правильная группа завтраков
        sn_combo = find_best_snidane_combo(
            kombinace_snidane[kombinace],
            druhe_snidane,
            svaciny,
            daily_calories,
            fixed_kcal
        )

        if not sn_combo:
            return JsonResponse({"error": f"Nepodařilo se najít snídaňovou kombinaci pro {day}."})

        jidla_v_deni = [
            sn_combo[0],
            sn_combo[1],
            obed,
            sn_combo[2],
            vecere_item
        ]
        denni_meals = []
        denni_kcal = 0

        for jidlo in jidla_v_deni:
            calories = float(jidlo.calories or 0)
            ingredients = [
                {
                    "name": ing.ingredient.name,
                    "amount": ing.amount,
                    "unit": ing.unit,
                }
                for ing in jidlo.ingredients.all()
            ]
            meal_entry = {
                "type": jidlo.type,
                "name": jidlo.name,
                "calories": calories,
                "protein": float(jidlo.protein or 0),
                "fat": float(jidlo.fat or 0),
                "carbs": float(jidlo.carbs or 0),
                "preparation": jidlo.preparation,
                "ingredients": ingredients,
                "obrazek": request.build_absolute_uri(jidlo.obrazek.url) if jidlo.obrazek else None,
            }
            denni_meals.append(meal_entry)
            denni_kcal += calories
            all_jidla.append(jidlo)

        # ✅ Теперь — проверяем и при необходимости добавляем extra snack
        min_acceptable_kcal = daily_calories * 0.9
        if denni_kcal < min_acceptable_kcal:
            deficit = min_acceptable_kcal - denni_kcal

            snack_candidates = Jidlo.objects.filter(type="snack_extra")
            snack_candidates = sorted(snack_candidates, key=lambda x: abs((x.calories or 0) - deficit))

            for snack in snack_candidates:
                if not snack or not snack.calories:
                    continue

                calories = float(snack.calories)
                ingredients = [
                    {
                        "name": ing.ingredient.name,
                        "amount": ing.amount,
                        "unit": ing.unit,
                    }
                    for ing in snack.ingredients.all()
                ]
                meal_entry = {
                    "type": "extra_snack",
                    "name": snack.name,
                    "calories": calories,
                    "protein": float(snack.protein or 0),
                    "fat": float(snack.fat or 0),
                    "carbs": float(snack.carbs or 0),
                    "preparation": snack.preparation,
                    "ingredients": ingredients,
                    "obrazek": request.build_absolute_uri(snack.obrazek.url) if snack.obrazek else None,
                }
                denni_meals.append(meal_entry)
                denni_kcal += calories
                all_jidla.append(snack)

                if denni_kcal >= min_acceptable_kcal:
                    break

        plan_data[day] = denni_meals
        weekly_kcal += denni_kcal

    # Сохраняем план, если нужно
    meal_plan = None
    try:
        if save:
            result_to_save = {
                "Plan_celkem": daily_calories,
                "plan": plan_data,
            }
            meal_plan = MealPlan.objects.create(data=json.dumps(result_to_save, ensure_ascii=False))
    except Exception as e:
        return JsonResponse({"error": f"Chyba při ukládání plánu: {str(e)}"})

    # Nákupní seznam
    ingredients_sum = defaultdict(lambda: {"total_amount": 0, "unit": ""})
    for jidlo in all_jidla:
        for ing in jidlo.ingredients.all():
            key = ing.ingredient.name
            ingredients_sum[key]["total_amount"] += float(ing.amount)
            ingredients_sum[key]["unit"] = ing.unit

    shopping_list = [
        {
            "ingredient__name": name,
            "total_amount": round(data["total_amount"], 1),
            "ingredient__unit": data["unit"],
        }
        for name, data in ingredients_sum.items()
    ]

    response_data = {
        "plan_data": plan_data,
        "shopping_list": shopping_list,
        "details": {
            "weekly_calories": round(weekly_kcal, 1),
            "daily_target": daily_calories,
        },
    }

    if meal_plan:
        response_data["meal_plan_id"] = meal_plan.id
        response_data["saved"] = True

    return JsonResponse(response_data)


@csrf_exempt
def ulozeny_plan(request):
    posledni = MealPlan.objects.last()
    if not posledni:
        return JsonResponse({"error": "Žádný uložený plán nebyl nalezen."})

    data = json.loads(posledni.data)
    plan = data.get("plan", {})
    target = data.get("Plan_celkem", 0)

    # Соберём список покупок по сохранённому плану
    # Нам нужны все блюда плана
    all_jidla = []
    for den, meals in plan.items():
        for m in meals:
            # m — словарь с {"type", "name", "calories", "ingredients", ...}
            all_jidla.append(m)

    ingredients_sum = defaultdict(lambda: {"total_amount": 0, "unit": ""})
    from .models import Ingredient  # не обязательно, просто для вида
    # m["ingredients"] — список словарей с полями name, amount, unit
    for m in all_jidla:
        for ing in m.get("ingredients", []):
            name = ing.get("name")
            amt = ing.get("amount", 0)
            unit = ing.get("unit", "")
            ingredients_sum[name]["total_amount"] += float(amt)
            ingredients_sum[name]["unit"] = unit

    shopping_list = [
        {
            "ingredient__name": name,
            "total_amount": round(info["total_amount"], 1),
            "ingredient__unit": info["unit"],
        }
        for name, info in ingredients_sum.items()
    ]

    response_data = {
        "details": {
            "daily_target": target
        },
        "plan_data": plan,
        "shopping_list": shopping_list,
    }

    return JsonResponse(response_data)

@csrf_exempt
def ulozit_z_existujiciho(request):
    if request.method != "POST":
        return JsonResponse({"error": "Pouze metoda POST je povolena."})

    try:
        data = json.loads(request.body.decode("utf-8"))
        plan_to_save = {
            "Plan_celkem": data.get("details", {}).get("daily_target", 0),
            "plan": data.get("plan_data", {})
        }
        meal_plan = MealPlan.objects.create(data=json.dumps(plan_to_save, ensure_ascii=False))
        return JsonResponse({"message": "Plán byl uložen.", "meal_plan_id": meal_plan.id})
    except Exception as e:
        return JsonResponse({"error": f"Chyba při ukládání: {str(e)}"})