from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
import random
from django.db.models import Sum

from .models import Jidlo, MealPlan, MealItem, RecipeIngredient
from .serializers import MyRenderer, JidloSerializer, MealPlanSerializer

class JidloViewSet(viewsets.ModelViewSet):
    queryset = Jidlo.objects.all()
    serializer_class = JidloSerializer


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer

class VypocetAPIView(APIView):
    renderer_classes = [MyRenderer]

    def calculate_tdee(self, vaha, vyska, vek, pohlavi, aktivita):
        if pohlavi == "muz":
            bmr = 10 * vaha + 6.25 * vyska - 5 * vek + 5
        else:
            bmr = 10 * vaha + 6.25 * vyska - 5 * vek - 161

        aktivita_koef = {
            "sedavy": 1.2,
            "lehka": 1.375,
            "stredni": 1.55,
            "vysoka": 1.725,
            "extra": 1.9
        }
        tdee = bmr * aktivita_koef.get(aktivita, 1.2)
        return round(bmr), round(tdee), round(tdee - 500)

    def create_meal_plan(self, target_calories):
        days = ["pondeli", "utery", "streda", "ctvrtek", "patek", "sobota", "nedele"]
        meal_types = ["snidane", "druhe_snidane","svacina", "obed", "vecere"]

        candidates_by_type = {}
        for typ in meal_types:
            cands = list(Jidlo.objects.filter(type=typ))
            candidates_by_type[typ] = cands

        for typ, cands in candidates_by_type.items():
            if not cands:
                return {"error": f"Нет блюд для типа '{typ}'"}

        meal_plan = MealPlan.objects.create(name=f"Týdenní plán {target_calories} kcal")

        plan_data = {}
        weekly_kcal = 0.0

        for day in days:
            selected = []
            for typ in meal_types:
                picked = random.choice(candidates_by_type[typ])
                selected.append((typ, picked))

            daily_kcal = sum(meal.calories for _, meal in selected)
            attempts = 0
            max_attempts = 100
            while daily_kcal > target_calories and attempts < max_attempts:
                heaviest_idx = max(range(len(selected)), key=lambda i: selected[i][1].calories)
                typ, current = selected[heaviest_idx]
                lower_options = [c for c in candidates_by_type[typ] if c.calories < current.calories]
                if not lower_options:
                    break
                new_choice = random.choice(lower_options)
                selected[heaviest_idx] = (typ, new_choice)
                daily_kcal = sum(meal.calories for _, meal in selected)
                attempts += 1

            for typ, meal in selected:
                MealItem.objects.create(meal_plan=meal_plan, jidlo=meal, quantity=1, day=day)

            plan_data[day] = selected
            weekly_kcal += daily_kcal

        shopping_qs = (
            RecipeIngredient.objects
            .filter(jidlo__mealitem__meal_plan=meal_plan)
            .values("ingredient__name", "ingredient__unit")
            .annotate(total_amount=Sum("amount"))
        )
        shopping_list = list(shopping_qs)

        details = {
            "weekly_calories": round(weekly_kcal, 1),
            "daily_target": target_calories
        }

        return {
            "plan_data": plan_data,
            "meal_plan": meal_plan,
            "shopping_list": shopping_list,
            "details": details,
        }

    def post(self, request):
        manual_calories = request.data.get("manual_calories")

        if manual_calories is not None:
            try:
                target_calories = int(manual_calories)
            except (ValueError, TypeError):
                return Response({"error": "Neplatná hodnota pro manual_calories."}, status=status.HTTP_400_BAD_REQUEST)

            result = self.create_meal_plan(target_calories=target_calories)
            if "error" in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            plan_summary = {}
            for day, meals in result["plan_data"].items():
                plan_summary[day] = [
                    {"typ": typ, **JidloSerializer(meal).data}
                    for typ, meal in meals
                ]

            serialized_plan = MealPlanSerializer(result["meal_plan"]).data

            response_data = {
                "message": "Plán vytvořen podle manuální kalorie",
                "details": result["details"],
                "plan": plan_summary,
                "plan_detail": serialized_plan,
                "kalorie": {"Plan_celkem": target_calories},
                "nakupni_seznam": result["shopping_list"],
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        # --- výpočet podle údajů ---
        required_fields = ["vaha", "vyska", "vek", "pohlavi"]
        for field in required_fields:
            if field not in request.data:
                return Response({"error": f"Pole '{field}' je povinné."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vaha = float(request.data.get("vaha"))
            vyska = float(request.data.get("vyska"))
            vek = int(request.data.get("vek"))
            pohlavi = request.data.get("pohlavi")
            aktivita = request.data.get("aktivita", "sedavy")
        except (ValueError, TypeError):
            return Response({"error": "Neplatné hodnoty vstupu."}, status=status.HTTP_400_BAD_REQUEST)

        bmr, tdee, deficit = self.calculate_tdee(vaha, vyska, vek, pohlavi, aktivita)
        target_calories = deficit

        result = self.create_meal_plan(target_calories=target_calories)
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        plan_summary = {}
        for day, meals in result["plan_data"].items():
            plan_summary[day] = [
                {"typ": typ, **JidloSerializer(meal).data}
                for typ, meal in meals
            ]

        serialized_plan = MealPlanSerializer(result["meal_plan"]).data

        response_data = {
            "message": "Plán vytvořen",
            "details": result["details"],
            "plan": plan_summary,
            "plan_detail": serialized_plan,
            "kalorie": {
                "BMR": bmr,
                "TDEE": tdee,
                "Deficit_500": deficit,
            },
            "nakupni_seznam": result["shopping_list"],
        }

        return Response(response_data, status=status.HTTP_201_CREATED)