from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, F, FloatField
from collections import defaultdict
import random
from django.conf import settings
from .models import Jidlo, MealPlan, ProgressRecord, Profile
from .serializers import JidloSerializer, ProgressSerializer
import json
from django.utils import timezone
from rest_framework import status
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

COOKING_COEFFICIENT = 1.6


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Регистрация нового пользователя и выдача токена.
    Ожидает JSON с полями 'username' и 'password'.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

    # Создаём пользователя
    user = User.objects.create_user(username=username, password=password)

    # Создаём токен для нового пользователя
    token, created = Token.objects.get_or_create(user=user)

    return Response({
        "message": "User created successfully",
        "token": token.key
    }, status=status.HTTP_201_CREATED)
class QueryParamTokenAuthentication(TokenAuthentication):
    """
    Позволяет передавать токен через ?token=<ваш_токен>
    """
    def authenticate(self, request):
        token = request.GET.get('token')
        if token:
            token = token.replace('"', '')  # убираем лишние кавычки
            request.META['HTTP_AUTHORIZATION'] = f'Token {token}'
        return super().authenticate(request)

# --- Получение прогресса ---
@api_view(["GET"])
@authentication_classes([QueryParamTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_progress(request):
    user = request.user

    # Проверка наличия профиля
    if not hasattr(user, 'profile'):
        return Response([], status=status.HTTP_200_OK)

    records = ProgressRecord.objects.filter(profile=user.profile).order_by('date')
    serializer = ProgressSerializer(records, many=True)

    data = []
    prev_weight = None

    for r in serializer.data:
        weight = r["weight"]
        if prev_weight is None:
            change = 0
            message = "Začínáme! 💫"
        else:
            diff = round(weight - prev_weight, 1)
            if diff < -0.3:
                message = "Skvělý pokrok! Pokračuj v pravidelném pohybu 💪"
            elif diff > 0.3:
                message = "Váha mírně vzrostla, zkus omezit večerní svačiny 🍽️"
            else:
                message = "Stabilní výsledek, udrž si rytmus 🔄"
            change = diff

        data.append({**r, "change": change, "message": message})
        prev_weight = weight

    return Response(data)

# --- Добавление записи ---
@api_view(["POST"])
@authentication_classes([QueryParamTokenAuthentication])
@permission_classes([IsAuthenticated])
def add_progress(request):
    user = request.user
    if not hasattr(user, 'profile'):
        return Response({"error": "Uživatel nemá profil."}, status=status.HTTP_400_BAD_REQUEST)

    weight = request.data.get("weight")
    note = request.data.get("note", "")

    if weight is None:
        return Response({"error": "Zadejte prosím hmotnost."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        weight = float(weight)
    except ValueError:
        return Response({"error": "Neplatná hodnota hmotnosti."}, status=status.HTTP_400_BAD_REQUEST)

    record = ProgressRecord.objects.create(
        profile=user.profile,
        weight=weight,
        note=note,
        date=timezone.now().date()
    )

    serializer = ProgressSerializer(record)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# --- Удаление записи ---
@api_view(["DELETE"])
@authentication_classes([QueryParamTokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_progress(request, pk):
    user = request.user
    if not hasattr(user, 'profile'):
        return Response({"error": "Uživatel nemá profil."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        record = ProgressRecord.objects.get(pk=pk, profile=user.profile)
        record.delete()
        return Response({"message": "Záznam byl úspěšně smazán."}, status=status.HTTP_200_OK)
    except ProgressRecord.DoesNotExist:
        return Response({"error": "Záznam nenalezen."}, status=status.HTTP_404_NOT_FOUND)
@api_view(["GET"])
@permission_classes([AllowAny])
def vsechna_jidla(request):
    print("📩 Query params:", request.GET)
    jidla = (
        Jidlo.objects.annotate(
            price_value=Sum(
                F("ingredients__ingredient__price") * F("ingredients__amount") / 100.0,
                output_field=FloatField()
            ),
            ready_price_value=Sum(
                F("ingredients__ingredient__price") * F("ingredients__amount") / 100.0,
                output_field=FloatField()
            ) * COOKING_COEFFICIENT
        )
    )

    filters = {}

    def safe_float(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    if safe_float(request.GET.get("product_price__gte")) is not None:
        filters["price_value__gte"] = safe_float(request.GET["product_price__gte"])
    if safe_float(request.GET.get("product_price__lte")) is not None:
        filters["price_value__lte"] = safe_float(request.GET["product_price__lte"])

    if safe_float(request.GET.get("ready_price__gte")) is not None:
        filters["ready_price_value__gte"] = safe_float(request.GET["ready_price__gte"])
    if safe_float(request.GET.get("ready_price__lte")) is not None:
        filters["ready_price_value__lte"] = safe_float(request.GET["ready_price__lte"])

    if safe_float(request.GET.get("protein__gte")) is not None:
        filters["protein__gte"] = safe_float(request.GET["protein__gte"])
    if safe_float(request.GET.get("protein__lte")) is not None:
        filters["protein__lte"] = safe_float(request.GET["protein__lte"])

    if safe_float(request.GET.get("calories__gte")) is not None:
        filters["calories__gte"] = safe_float(request.GET["calories__gte"])
    if safe_float(request.GET.get("calories__lte")) is not None:
        filters["calories__lte"] = safe_float(request.GET["calories__lte"])

    if request.GET.get("category"):
        filters["type"] = request.GET["category"]

    print("🔎 filters:", filters)
    jidla = jidla.filter(**filters)

    serializer = JidloSerializer(jidla, many=True, context={"request": request})
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

@api_view(["POST"])
@permission_classes([AllowAny])
def vypocet(request):
    """
    Генерация недельного плана питания с расчетом калорий и списка покупок.
    """
    data = request.data

    # --- Расчет дневной калорийности ---
    manual = data.get("manual_calories")
    if manual:
        try:
            daily_calories = int(manual)
        except ValueError:
            return Response({"error": "Neplatná hodnota kalorií."}, status=400)
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
            return Response({"error": "Neplatné vstupní údaje."}, status=400)

    save = data.get("save", False)

    # --- Загрузка всех типов еды ---
    snidane = list(Jidlo.objects.filter(type="snidane"))
    druhe_snidane = list(Jidlo.objects.filter(type="druhe_snidane"))
    obedy = list(Jidlo.objects.filter(type="obed"))
    svaciny = list(Jidlo.objects.filter(type="svacina"))
    vecere = list(Jidlo.objects.filter(type="vecere"))

    if not (snidane and druhe_snidane and obedy and svaciny and vecere):
        return Response({"error": "Chybí jídla v databázi."}, status=400)

    # --- Комбинации по дням недели ---
    KOMBINACE_DNU = {
        "kombinace_A": ["pondeli", "utery", "ctvrtek"],
        "kombinace_B": ["streda", "patek"],
        "kombinace_C": ["sobota", "nedele"],
    }
    day_to_combo = {d: k for k, v in KOMBINACE_DNU.items() for d in v}

    kombinace_jidel = {
        "kombinace_A": (random.choice(obedy), random.choice(vecere)),
        "kombinace_B": (random.choice(obedy), random.choice(vecere)),
        "kombinace_C": (random.choice(obedy), random.choice(vecere)),
    }

    kombinace_snidane = {
        "kombinace_A": random.sample(snidane, min(3, len(snidane))),
        "kombinace_B": random.sample(snidane, min(3, len(snidane))),
        "kombinace_C": random.sample(snidane, min(3, len(snidane))),
    }

    days = ["pondeli", "utery", "streda", "ctvrtek", "patek", "sobota", "nedele"]
    plan_data = {}
    weekly_kcal = 0
    all_jidla = []

    for day in days:
        kombinace = day_to_combo.get(day, "kombinace_A")
        obed, vecere_item = kombinace_jidel[kombinace]
        fixed_kcal = float(obed.calories or 0) + float(vecere_item.calories or 0)

        sn_combo = find_best_snidane_combo(
            kombinace_snidane[kombinace],
            druhe_snidane,
            svaciny,
            daily_calories,
            fixed_kcal
        )

        if not sn_combo:
            return Response({"error": f"Nepodařilo se najít snídaňovou kombinaci pro {day}."}, status=400)

        jidla_v_deni = [sn_combo[0], sn_combo[1], obed, sn_combo[2], vecere_item]
        denni_meals = []
        denni_kcal = 0

        for jidlo in jidla_v_deni:
            jidlo_serialized = JidloSerializer(jidlo, context={'request': request}).data
            denni_meals.append(jidlo_serialized)
            denni_kcal += float(jidlo.calories or 0)
            all_jidla.append(jidlo)

        # Добавляем дополнительный перекус, если необходимо
        min_acceptable_kcal = daily_calories * getattr(settings, "MEAL_TOLERANCE", 0.9)
        if denni_kcal < min_acceptable_kcal:
            deficit = min_acceptable_kcal - denni_kcal
            snack_candidates = Jidlo.objects.filter(type="snack_extra").order_by('calories')
            snack_candidates = sorted(snack_candidates, key=lambda x: abs((x.calories or 0) - deficit))
            for snack in snack_candidates:
                if not snack or not snack.calories:
                    continue
                snack_serialized = JidloSerializer(snack, context={'request': request}).data
                snack_serialized['type'] = "extra_snack"
                denni_meals.append(snack_serialized)
                denni_kcal += float(snack.calories)
                all_jidla.append(snack)
                if denni_kcal >= min_acceptable_kcal:
                    break

        plan_data[day] = denni_meals
        weekly_kcal += denni_kcal

    # Сохраняем план
    meal_plan = None
    if save:
        plan_to_save = {"Plan_celkem": daily_calories, "plan": plan_data}
        meal_plan = MealPlan.objects.create(
            profile=None,
            data=json.dumps(plan_to_save, ensure_ascii=False),
            name=f"Plán {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )

    # Формируем список покупок
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
            "ingredient__unit": data["unit"]
        }
        for name, data in sorted(ingredients_sum.items())
    ]

    response_data = {
        "plan_data": plan_data,
        "shopping_list": shopping_list,
        "details": {
            "weekly_calories": round(weekly_kcal, 1),
            "daily_target": daily_calories
        }
    }

    if meal_plan:
        response_data.update({"meal_plan_id": meal_plan.id, "saved": True})

    return Response(response_data)
@api_view(["GET"])
@permission_classes([AllowAny])
def ulozeny_plan(request):
    """
    Получение последнего сохраненного плана с подсчетом списка покупок.
    """
    posledni = MealPlan.objects.last()
    if not posledni:
        return Response({"error": "Žádný uložený plán nebyl nalezen."}, status=404)

    data = json.loads(posledni.data)
    plan = data.get("plan", {})
    target = data.get("Plan_celkem", 0)

    # Соберём список покупок по сохранённому плану
    all_jidla = []
    for den, meals in plan.items():
        for m in meals:
            all_jidla.append(m)

    ingredients_sum = defaultdict(lambda: {"total_amount": 0, "unit": ""})
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
        "details": {"daily_target": target},
        "plan_data": plan,
        "shopping_list": shopping_list,
    }

    return Response(response_data)


@api_view(['POST'])
@permission_classes([AllowAny])
def ulozit_z_existujiciho(request):
    """
    Сохраняет план ДЛЯ ГОСТЯ — без пользователя и без профиля.
    """
    data = request.data

    plan_to_save = {
        "Plan_celkem": data.get("details", {}).get("daily_target", 0),
        "plan": data.get("plan_data", {})
    }

    # Сохраняем в MealPlan без привязки к юзеру
    new_plan = MealPlan.objects.create(
        profile=None,  # хранится без пользователя
        data=json.dumps(plan_to_save, ensure_ascii=False),
        name="Guest Plan"
    )

    return Response({
        "message": "Plán byl uložen jako host.",
        "plan_id": new_plan.id,
        "saved": True
    })
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})