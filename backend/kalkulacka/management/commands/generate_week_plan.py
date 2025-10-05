from django.core.management.base import BaseCommand
from kalkulacka.models import Jidlo, RecipeIngredient
from django.db.models import Sum

class Command(BaseCommand):
    help = "Vygeneruje pevný týdenní jídelní plán s nákupním seznamem"

    def handle(self, *args, **kwargs):
        # Жёсткие комбинации
        DNY = ["pondeli", "utery", "streda", "ctvrtek", "patek", "sobota", "nedele"]
        KOMBINACE_DNU = {
            "kombinace_A": ["pondeli", "utery", "ctvrtek"],
            "kombinace_B": ["streda", "patek"],
            "kombinace_C": ["sobota", "nedele"]
        }

        # Обратная мапа день -> комбинация
        day_to_combo = {}
        for combo_name, days_list in KOMBINACE_DNU.items():
            for d in days_list:
                day_to_combo[d.strip().lower()] = combo_name

        # Получаем блюда
        snidane = list(Jidlo.objects.filter(type="snidane"))
        druhe_snidane = list(Jidlo.objects.filter(type="druhe_snidane"))
        obedy = list(Jidlo.objects.filter(type="obed"))
        svaciny = list(Jidlo.objects.filter(type="svacina"))
        vecere = list(Jidlo.objects.filter(type="vecere"))

        if not (snidane and druhe_snidane and obedy and svaciny and vecere):
            self.stdout.write(self.style.ERROR("❌ Chybí jídla v databázi!"))
            return

        # Жёсткие комбинации обед+ужин
        kombinace_jidel = {
            "kombinace_A": (obedy[0], vecere[0]),
            "kombinace_B": (obedy[1] if len(obedy) > 1 else obedy[0],
                            vecere[1] if len(vecere) > 1 else vecere[0]),
            "kombinace_C": (obedy[-1], vecere[-1])
        }

        tydenni_kalorie = 0
        nakupni_seznam = {}

        self.stdout.write(self.style.SUCCESS("🧠 Jídelní plán (pevně):\n"))

        for den in DNY:
            norm_den = den.strip().lower()
            kombinace = day_to_combo.get(norm_den, "kombinace_A")
            obed, vecere_item = kombinace_jidel[kombinace]

            sn = snidane[0]
            ds = druhe_snidane[0]
            sv = svaciny[0]

            denni_kalorie = sn.calories + ds.calories + obed.calories + sv.calories + vecere_item.calories
            tydenni_kalorie += denni_kalorie

            # Собираем ингредиенты
            for jidlo in [sn, ds, obed, sv, vecere_item]:
                ing_qs = RecipeIngredient.objects.filter(jidlo=jidlo).values(
                    "ingredient__name", "ingredient__unit"
                ).annotate(total_amount=Sum("amount"))
                for ing in ing_qs:
                    key = (ing["ingredient__name"], ing["ingredient__unit"])
                    nakupni_seznam[key] = nakupni_seznam.get(key, 0) + ing["total_amount"]

            # Вывод плана
            self.stdout.write(
                f"{den.title()}: {round(denni_kalorie)} kcal\n"
                f"  🍳 Snídaně: {sn.name}\n"
                f"  🥐 Druhá snídaně: {ds.name}\n"
                f"  🧃 Svačina: {sv.name}\n"
                f"  🍲 Oběd: {obed.name}\n"
                f"  🍝 Večeře: {vecere_item.name}\n"
            )

        # Вывод списка покупок
        self.stdout.write(self.style.SUCCESS("\n🛒 Nákupní seznam na týden:"))
        for (name, unit), amount in nakupni_seznam.items():
            self.stdout.write(f" - {name}: {round(amount, 2)} {unit}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ Týdenní součet: {round(tydenni_kalorie)} kcal"))