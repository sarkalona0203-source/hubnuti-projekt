from django.core.management.base import BaseCommand
from kalkulacka.models import Ingredient, Jidlo, RecipeIngredient


class Command(BaseCommand):
    help = "Seed database with full meal plan (with categories)"

    def handle(self, *args, **kwargs):
        # 🔹 Очистка старых данных
        RecipeIngredient.objects.all().delete()
        Jidlo.objects.all().delete()
        Ingredient.objects.all().delete()

        # 🔹 Продукты с калориями, БЖУ и категориями
        produkty = {
            # 🥩 Maso
            "Kuřecí prsa": ((212, 23, 3, 0), "maso"),
            "Hovězí maso": ((304, 26, 21, 0), "maso"),
            "Kuřecí játra": ((268, 20, 12, 1), "maso"),
            "Mleté maso (vepřové)": ((270, 17, 23, 0), "maso"),


            # 🐟 Ryby
            "Makrela": ((234, 20, 15, 0), "ryba"),
            "Játra tresky": ((613, 4.2, 65.7, 1.2), "ryba"),
            "Treska": ((82, 18, 0.7, 0), "ryba"),

            # 🥛 Mléčné výrobky
            "Tvaroh tvrdý": ((260, 28, 14, 2), "mlecne"),
            "Tvaroh": ((98, 11, 4, 3), "mlecne"),
            "Řecký jogurt bíly 0 % tuku": ((114, 10, 0, 4), "mlecne"),
            "Jogurt": ((80, 5, 2.5, 6), "mlecne"),
            "Kefír": ((59, 3.3, 3.2, 4.6), "mlecne"),
            "Mléko polotučné 1,5 % tuku": ((46, 3.3, 1.5, 4.8), "mlecne"),
            "Smetana": ((228, 2, 20, 3), "mlecne"),
            "Sýr feta": ((264, 14, 21, 4),"mlecne"),
            "Máslo": ((717, 0.8, 81, 0),"mlecne"),

            # 🧀 Sýry
            "Eidam sýr 30 % tuku": ((263, 27, 17, 1.6), "syry"),
            "Tvrdý sýr (průměr)": ((356, 26, 27, 2), "syry"),
            "Mozzarella": ((280, 18, 17, 3), "syry"),
            "Sýr suluguni": ((320, 25, 25, 0), "syry"),

            # 🥦 Zelenina
            "Okurka": ((31, 1, 0, 4), "zelenina"),
            "Rajčata": ((42, 1, 0, 6), "zelenina"),
            "Rajčata cherry": ((18, 1, 0, 4), "zelenina"),
            "Mrkev": ((42, 1, 0, 10), "zelenina"),
            "Paprika": ((70, 1, 0, 14), "zelenina"),
            "Brokolice": ((48, 4, 0, 7), "zelenina"),
            "Ledový salát": ((14, 1, 0, 3), "zelenina"),
            "Žampiony": ((22, 3, 0, 3), "zelenina"),
            "Mražená zelenina havajská směs": ((90, 2.0, 1.0, 16), "zelenina"),
            "Cuketa": ((17, 1.2, 0.3, 3.1), "zelenina"),
            "Petržel": ((36, 3, 0, 6), "zelenina"),
            "Česnek": ((149, 6, 0, 33), "zelenina"),
            "Cibule zelená": ((32, 1, 0, 6), "zelenina"),
            "Červená cibule": ((40, 1, 0, 9), "zelenina"),
            "Červená řepa": ((43, 1.6, 0.2, 10), "zelenina"),
            "Kapusta": ((27, 1.3, 0.2, 6), "zelenina"),
            "Kukuřice konzervovaná": ((98, 3.2, 1.5, 19), "zelenina"),
            "Okurky nakládané": ((18, 0.6, 0.1, 2.4),"zelenina"),
            "Hrášek zelený": ((81, 5.4, 0.4, 14),"zelenina"),



            # 🍎 Ovoce
            "Banán": ((88, 1, 0, 23), "ovoce"),
            "Jablko": ((52, 0, 0, 14), "ovoce"),
            "Avokádo": ((160, 2, 15, 9), "ovoce"),
            "Švestky": ((46, 0.7, 0.3, 11), "ovoce"),
            "Broskev": ((39, 0.9, 0.3, 10), "ovoce"),
            "Dýně": ((26, 1, 0.1, 6),"ovoce"),
            "Sušené meruňky": ((284, 5, 0.5, 62),"ovoce"),
            "Sušené švestky": ((240, 2.3, 0.7, 64),"ovoce"),
            "Rozinky": ((299, 3.1, 0.5, 79),"ovoce"),
            "Sušené fíky": ((249, 3.3, 0.9, 58),"ovoce"),

            # 🌾 Obiloviny a přílohy
            "Ovesná kaše": ((71, 2.5, 1.5, 12), "obiloviny"),
            "Pohanka vařená": ((110, 4, 1, 20), "obiloviny"),
            "Pšenice kaše": ((127, 4.5, 0.4, 27), "obiloviny"),
            "Rýže bílá dlouhozrnná vařená": ((130, 2.7, 0.3, 28), "obiloviny"),
            "Bulgur": ((83, 3.1, 0.2, 18), "obiloviny"),
            "Brambory vařené": ((86, 2, 0, 20), "obiloviny"),
            "Rýže suchá": ((365, 7, 1, 79),"obiloviny"),
            "Krupice": ((360, 10, 1, 76),"obiloviny"),

            # 🧈 Tuky
            "Rostlinný olej": ((884, 0, 100, 0), "tuky"),
            "Olej slunečnicový": ((884, 0, 100, 0), "tuky"),
            "Olivový olej": ((884, 0, 100, 0), "tuky"),

            # 🍬 Ostatní
            "Vejce": ((155, 13, 11, 1), "ostatni"),
            "Mouka": ((364, 10, 1, 76), "ostatni"),
            "Cukr": ((387, 0, 0, 100), "ostatni"),
            "Vanilkový cukr": ((400, 0, 0, 100), "ostatni"),
            "Vlašské ořechy": ((654, 15, 65, 14),"ostatni"),
            "Tresčí játra": ((613, 13, 65, 0),"ostatni"),
            "Pepř černý mletý": ((251, 10.4, 3.3, 64), "ostatni"),
            "Sůl": ((0, 0, 0, 0),"ostatni"),
            "Čerstvé bylinky": ((43, 3, 1, 7),"ostatni"),
            "Rajčatový protlak": ((82, 1.5, 0.3, 18),"ostatni"),
            "Zelí bílé": ((25, 1.3, 0.1, 6),"ostatni"),
            "Lesní plody": ((50, 1, 0.3, 12),"ostatni"),
            "Majonéza": ((680, 1, 75, 2),"ostatni"),
            "Tuňák konzerva ve vlastní šťávě": ((116, 25, 1, 0),"ostatni"),
            "Okurky sterilované": ((19, 0.5, 0.2, 4),"ostatni"),
            "Chléb žitný": ((227, 5.6, 1.1, 43),"ostatni"),
        }

        # 🔹 Заполняем таблицу Ingredient
        ingredient_objects = {}
        for name, (nutrients, category) in produkty.items():
            kcal, protein, fat, carbs = nutrients
            ingr = Ingredient.objects.create(
                name=name,
                calories_per_100g=kcal,
                protein_per_100g=protein,
                fat_per_100g=fat,
                carbs_per_100g=carbs,
                unit="g",
                category=category
            )
            ingredient_objects[name] = ingr

        # Завтраки
        snidane1 = Jidlo.objects.create(
            name="Tvaroh se smetanou",
            type="snidane",
            preparation="Smíchej tvaroh se smetanou."
        )
        RecipeIngredient.objects.create(jidlo=snidane1, ingredient=ingredient_objects["Tvaroh tvrdý"], amount=180)
        RecipeIngredient.objects.create(jidlo=snidane1, ingredient=ingredient_objects["Smetana"], amount=70)

        snidane2 = Jidlo.objects.create(
            name="Vejce se zeleninou",
            type="snidane",
            preparation="Uvař vejce a podávej se zeleninovým salátem."
         )
        RecipeIngredient.objects.create(jidlo=snidane2, ingredient=ingredient_objects["Vejce"], amount=100)
        RecipeIngredient.objects.create(jidlo=snidane2, ingredient=ingredient_objects["Mrkev"], amount=80)
        RecipeIngredient.objects.create(jidlo=snidane2, ingredient=ingredient_objects["Paprika"], amount=80)
        snidane3 = Jidlo.objects.create(
            name="Syrniki",
            type="snidane",
            preparation=(
                "Smíchej tvaroh, vejce, mouku, cukr a vanilkový cukr. "
                "Vytvoř placky, obalte v mouce a smažte na pánvi s olejem."
            )
        )
        RecipeIngredient.objects.create(jidlo=snidane3, ingredient=ingredient_objects["Tvaroh tvrdý"], amount=100)
        RecipeIngredient.objects.create(jidlo=snidane3, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane3, ingredient=ingredient_objects["Mouka"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane3, ingredient=ingredient_objects["Cukr"], amount=16)
        RecipeIngredient.objects.create(jidlo=snidane3, ingredient=ingredient_objects["Rostlinný olej"], amount=10)
        RecipeIngredient.objects.create(jidlo=snidane3, ingredient=ingredient_objects["Vanilkový cukr"], amount=5)
        snidane4 = Jidlo.objects.create(
            name="Ovesná kaše s banánem",
            type="snidane",
            preparation="Uvař ovesnou kaši a přidej nakrájený banán."
        )
        RecipeIngredient.objects.create(jidlo=snidane4, ingredient=ingredient_objects["Ovesná kaše"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane4, ingredient=ingredient_objects["Banán"], amount=100)
        RecipeIngredient.objects.create(jidlo=snidane4, ingredient=ingredient_objects["Mléko polotučné 1,5 % tuku"],
                                        amount=200)

        snidane5 = Jidlo.objects.create(
            name="Tvaroh s ovocem a ořechy",
            type="snidane",
            preparation="Smíchej tvaroh s nakrájeným ovocem a posyp ořechy."
        )
        RecipeIngredient.objects.create(jidlo=snidane5, ingredient=ingredient_objects["Tvaroh"], amount=150)
        RecipeIngredient.objects.create(jidlo=snidane5, ingredient=ingredient_objects["Jablko"], amount=100)
        RecipeIngredient.objects.create(jidlo=snidane5, ingredient=ingredient_objects["Banán"], amount=50)
        # Предположим, что у тебя есть "Vlašské ořechy" (грецкие орехи)
        RecipeIngredient.objects.create(jidlo=snidane5, ingredient=ingredient_objects["Vlašské ořechy"], amount=20)

        snidane6 = Jidlo.objects.create(
            name="Vejce na tvrdo s okurkou",
            type="snidane",
            preparation="Uvař vejce na tvrdo a podávej s čerstvou okurkou."
        )
        RecipeIngredient.objects.create(jidlo=snidane6, ingredient=ingredient_objects["Vejce"], amount=120)
        RecipeIngredient.objects.create(jidlo=snidane6, ingredient=ingredient_objects["Okurka"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane4, ingredient=ingredient_objects["Rajčata"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane4, ingredient=ingredient_objects["Paprika"], amount=60)
        snidane7 = Jidlo.objects.create(
            name="Omeleta se zeleninou",
            type="snidane",
            preparation="Rozšlehej vejce, osol, opepři. Přidej nakrájenou zeleninu a smaž na pánvi s trochou oleje."
        )
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Vejce"], amount=120)  # 2 vejce
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Paprika"], amount=40)
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Rajčata"], amount=40)
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Rostlinný olej"], amount=5)
        snidane8 = Jidlo.objects.create(
            name="Pohanková kaše a salát s játry tresky",
            type="snidane",
            preparation=(
                "Uvař pohanku. Připrav salát: smíchej játra tresky, kukuřici, nakrájenou okurku, osol a opepři. "
                "Přidej čerstvé bylinky podle chuti."
            )
        )
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Pohanka vařená"], amount=170)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Játra tresky"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Kukuřice konzervovaná"],
                                        amount=50)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Okurka"], amount=70)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Sůl"], amount=2)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Pepř černý mletý"], amount=1)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Čerstvé bylinky"], amount=5)
        snidane9 = Jidlo.objects.create(
            name="Omeleta se sýrem",
            type="snidane",
            preparation="Rozšlehej vejce s mlékem, osol. Nalij na pánev, přidej nastrouhaný sýr a osmaž omeletu."
        )

        RecipeIngredient.objects.create(jidlo=snidane9, ingredient=ingredient_objects["Vejce"], amount=120)
        RecipeIngredient.objects.create(jidlo= snidane9, ingredient=ingredient_objects["Eidam sýr 30 % tuku"],
                                        amount=40)
        RecipeIngredient.objects.create(jidlo= snidane9,
                                        ingredient=ingredient_objects["Smetana"], amount=20)

        snidane10 = Jidlo.objects.create(
            name="Ovesná kaše s lesními plody",
            type="snidane",
            preparation="Uvař ovesnou kaši a podávej s čerstvými nebo mraženými lesními plody."
        )

        RecipeIngredient.objects.create(jidlo=snidane10, ingredient=ingredient_objects["Ovesná kaše"],
                                        amount=180)
        RecipeIngredient.objects.create(jidlo=snidane10, ingredient=ingredient_objects["Lesní plody"],
                                        amount=160)
        snidane11 = Jidlo.objects.create(
            name="Tvarohová zapékaná",
            type="snidane",
            preparation=(
                "Smíchej tvaroh, vejce, trochu cukru a krupici. "
                "Peč v předehřáté troubě na 180 °C asi 35–40 minut."
            )
        )

        RecipeIngredient.objects.create(jidlo=snidane11, ingredient=ingredient_objects["Tvaroh"], amount=150)
        RecipeIngredient.objects.create(jidlo=snidane11, ingredient=ingredient_objects["Vejce"], amount=40)
        RecipeIngredient.objects.create(jidlo=snidane11, ingredient=ingredient_objects["Cukr"], amount=10)
        RecipeIngredient.objects.create(jidlo=snidane11, ingredient=ingredient_objects["Krupice"], amount=20)
        snidane12 = Jidlo.objects.create(
            name="Bliny s houbami",
            type="snidane",
            preparation=(
                "Připrav těsto na palačinky (vejce, mléko, mouka, špetka soli). "
                "Na pánvi osmaž palačinky. "
                "Houby (žampiony) osmaž s cibulkou a trochou smetany. "
                "Naplň palačinky směsí a zabal je."
            )
        )

        RecipeIngredient.objects.create(jidlo=snidane12,
                                        ingredient=ingredient_objects["Mléko polotučné 1,5 % tuku"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane12, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane12, ingredient=ingredient_objects["Mouka"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane12, ingredient=ingredient_objects["Žampiony"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane12, ingredient=ingredient_objects["Smetana"], amount=20)
        snidane13 = Jidlo.objects.create(
            name="Dýňová rýžová kaše",
            type="snidane",
            preparation="Uvař dýni s rýží, mlékem, vodou, cukrem a máslem do měkka. Podávej teplé."
        )

        RecipeIngredient.objects.create(jidlo=snidane13, ingredient=ingredient_objects["Dýně"], amount=90)
        RecipeIngredient.objects.create(jidlo=snidane13, ingredient=ingredient_objects["Rýže suchá"],
                                        amount=50)
        RecipeIngredient.objects.create(jidlo=snidane13,
                                        ingredient=ingredient_objects["Mléko polotučné 1,5 % tuku"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane13, ingredient=ingredient_objects["Cukr"], amount=6)
        RecipeIngredient.objects.create(jidlo=snidane13, ingredient=ingredient_objects["Máslo"], amount=9)

        # Вторые завтраки / полдники
        svacina1 = Jidlo.objects.create(
            name="Ovoce",
            type="druhe_snidane",
            preparation="Nakrájej ovoce dle chuti."
        )
        RecipeIngredient.objects.create(jidlo=svacina1, ingredient=ingredient_objects["Banán"], amount=150)
        RecipeIngredient.objects.create(jidlo=svacina1, ingredient=ingredient_objects["Jablko"], amount=100)

        svacina2 = Jidlo.objects.create(
            name="Eidam sýr 30 % tuku",
            type = "druhe_snidane"
        )
        RecipeIngredient.objects.create(jidlo=svacina2, ingredient=ingredient_objects["Eidam sýr 30 % tuku"], amount=40)
        svacina3 = Jidlo.objects.create(
            name="Jogurt",
            type="svacina",
            preparation="Podávej jogurt samostatně nebo s ovocem."
        )
        RecipeIngredient.objects.create(jidlo=svacina3, ingredient=ingredient_objects["Řecký jogurt bíly 0 % tuku"], amount=220)
        svacina4 = Jidlo.objects.create(
            name="Sýr jako svačina",
            type="svacina",
            preparation="Podávejte plátek sýru jako lehkou svačinu."
        )
        RecipeIngredient.objects.create(jidlo=svacina4, ingredient=ingredient_objects["Eidam sýr 30 % tuku"], amount=45)
        svacina5 = Jidlo.objects.create(
            name="Ovoce: švestky a broskve",
            type="druhe_snidane",
            preparation="Omyjte ovoce, nakrájejte na kousky a podávejte jako lehkou dopolední svačinu."
        )
        RecipeIngredient.objects.create(jidlo=svacina5, ingredient=ingredient_objects["Švestky"], amount=100)
        RecipeIngredient.objects.create(jidlo=svacina5, ingredient=ingredient_objects["Broskev"], amount=120)
        svacina6 = Jidlo.objects.create(
            name="Ovoce: švestky a broskve",
            type="druhe_snidane",
            preparation="Omyjte ovoce, nakrájejte na kousky a podávejte jako lehkou dopolední svačinu."
        )
        RecipeIngredient.objects.create(jidlo=svacina6, ingredient=ingredient_objects["Švestky"], amount=100)
        RecipeIngredient.objects.create(jidlo=svacina6, ingredient=ingredient_objects["Broskev"], amount=120)
        svacina8 = Jidlo.objects.create(
            name="Míchané ovoce",
            type="druhe_snidane",
            preparation="Nakrájejte ovoce a podávejte čerstvé."
        )

        RecipeIngredient.objects.create(jidlo= svacina8, ingredient=ingredient_objects["Banán"], amount=50)
        RecipeIngredient.objects.create(jidlo= svacina8, ingredient=ingredient_objects["Jablko"], amount=50)
        RecipeIngredient.objects.create(jidlo= svacina8, ingredient=ingredient_objects["Švestky"],
                                        amount=50)  # если есть
        RecipeIngredient.objects.create(jidlo= svacina8, ingredient=ingredient_objects["Broskev"],
                                        amount=50)  # если есть
        svacina9 = Jidlo.objects.create(
            name="Ovoce: švestky a broskve",
            type="svacina",
            preparation="Omyjte ovoce, nakrájejte na kousky a podávejte jako lehkou dopolední svačinu."
        )
        RecipeIngredient.objects.create(jidlo=svacina9, ingredient=ingredient_objects["Švestky"], amount=100)
        RecipeIngredient.objects.create(jidlo=svacina9, ingredient=ingredient_objects["Broskev"], amount=150)
        svacina10 = Jidlo.objects.create(
            name="Vlašské ořechy",
            type="svacina",
            preparation="Podávejte 25 g vlašských ořechů jako rychlou svačinu."
        )


        RecipeIngredient.objects.create(jidlo=svacina10, ingredient=ingredient_objects["Vlašské ořechy"], amount=25)
        svacina11 = Jidlo.objects.create(
            name="Sušené ovoce",
            type="druhe_snidane",
            preparation="Podávejte směs sušeného ovoce jako rychlou svačinu."
        )

        RecipeIngredient.objects.create(jidlo=svacina11, ingredient=ingredient_objects["Sušené švestky"],
                                        amount=25)
        RecipeIngredient.objects.create(jidlo=svacina11, ingredient=ingredient_objects["Rozinky"], amount=10)
        RecipeIngredient.objects.create(jidlo=svacina11, ingredient=ingredient_objects["Sušené meruňky"],
                                        amount=15)



        # Обеды
        obed1 = Jidlo.objects.create(
            name="Kuře s bulgurem a salátem",
            type="obed",
            preparation="Uvař kuře a bulgur, podávej se zeleninovým salátem."
        )
        RecipeIngredient.objects.create(jidlo=obed1, ingredient=ingredient_objects["Kuřecí prsa"], amount=220)
        RecipeIngredient.objects.create(jidlo=obed1, ingredient=ingredient_objects["Okurka"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed1, ingredient=ingredient_objects["Rajčata"], amount=100)
        obed2 = Jidlo.objects.create(
            name="Houbová polévka",
            type="obed",
            preparation="Uvař houby s mrkví, pohankou, bramborem a olejem."
        )
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Žampiony"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Mrkev"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Pohanka vařená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Brambory vařené"], amount=40)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Olej slunečnicový"], amount=10)
        obed3 = Jidlo.objects.create(
            name="Kuřecí filé s salátem",
            type="obed",
            preparation="Uvařené kuřecí filé podávejte s čerstvým salátem ze zelených zelenin."
        )
        RecipeIngredient.objects.create(jidlo=obed3, ingredient=ingredient_objects["Kuřecí prsa"], amount=150)
        RecipeIngredient.objects.create(jidlo=obed3, ingredient=ingredient_objects["Ledový salát"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed3, ingredient=ingredient_objects["Okurka"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed3, ingredient=ingredient_objects["Rajčata"], amount=60)
        # Можно добавить огурce, rajčata, papriku по вкусу

        obed4 = Jidlo.objects.create(
            name="Zeleninový salát s avokádem",
            type="obed",
            preparation="Smíchejte všechny ingredience a dochuťte limetkou a olivovým olejem."
        )
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Rajčata"], amount=200)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Okurka"], amount=200)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Avokádo"], amount=150)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Červená cibule"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Olivový olej"], amount=5)

        obed5 = Jidlo.objects.create(
            name="Zeleninový salát s cuketou",
            type="obed",
            preparation="""Cuketu omyjeme a nakrájíme na kolečka.
        Na pánvi rozehřejeme olivový olej a opečeme kolečka cukety z obou stran 2-3 minuty.
        Cuketu necháme vychladnout a nakrájíme na čtvrtky.
        Rajčata cherry také nakrájíme na čtvrtky.
        Vložíme cuketu a rajčata do mísy.
        Česnek a petržel nasekáme najemno a přidáme do salátu.
        Osolíme, opepříme a promícháme.
        Salát dáme na 20 minut do lednice a podáváme jako přílohu nebo samostatné jídlo."""
        )
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Cuketa"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Rajčata cherry"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Petržel"], amount=10)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Česnek"], amount=3)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Olivový olej"], amount=30)
        obed6 = Jidlo.objects.create(
            name="Salát s tresčí játry a rýží",
            type="obed",
            preparation=(
                "Uvař vejce natvrdo. Nakrájej okurky, přidej tresčí játra, kukuřici, rýži a vejce. "
                "Osol, opepři a přidej nasekanou čerstvou zeleninu dle chuti. Vše smíchej."
            )
        )
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Vejce"], amount=120)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Tresčí játra"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Kukuřice konzervovaná"], amount=150)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Okurka"], amount=150)  # cca 2 ks
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"],
                                        amount=150)
        obed7 = Jidlo.objects.create(
            name="Dušené kuře se zeleninovým salátem",
            type="obed",
            preparation="Kuřecí maso podusíme na mírném ohni s trochou vody. "
                        "Zeleninu nakrájíme a smícháme v salát. Podáváme společně."
        )
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Kuřecí prsa"], amount=220)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Okurka"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Rajčata"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Paprika"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        obed6 = Jidlo.objects.create(
            name="Dušené zelí s houbami",
            type="obed",
            preparation="Nakrájej zelí a žampiony. Orestuj cibuli, přidej houby a po chvíli zelí. Osol, opepři a duste doměkka."
        )
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Zelí bílé"], amount=200)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Žampiony"], amount=160)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Rostlinný olej"], amount=10)
        obed8 = Jidlo.objects.create(
            name="Postní boršč a houbový pilaf",
            type="obed",
            preparation=(
                "Uvař postní boršč z červené řepy, zelí, mrkve, cibule a rajského protlaku. "
                "Na pánvi připrav houbový pilaf z vařené rýže, žampionů a zeleniny."
            )
        )

        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Červená řepa"],
                                        amount=60)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Mrkev"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Zelí bílé"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Brambory vařené"],
                                        amount=40)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Rajčatový protlak"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=5)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Sůl"], amount=1)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Pepř černý mletý"],
                                        amount=0.5)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Žampiony"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Mrkev"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=5)

        obed11 = Jidlo.objects.create(
            name="Zeleninová polévka a kuřecí rolky se sýrem",
            type="obed",
            preparation=(
                "Uvař zeleninovou polévku z mrkve, cibule, brambor a brokolice. "
                "Kuřecí prsa rozklepej, naplň sýrem a bylinkami, sroluj a upeč nebo osmaž."
            )
        )

        # 🥣 Суп
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Mrkev"], amount=60)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Brambory vařené"],
                                        amount=70)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Brokolice"], amount=40)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=5)

        # 🍗 Куриные рулеты
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Kuřecí prsa"], amount=140)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Eidam sýr 30 % tuku"],
                                        amount=40)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Petržel"], amount=10)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=5)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Sůl"], amount=1)
        RecipeIngredient.objects.create(jidlo=obed11, ingredient=ingredient_objects["Pepř černý mletý"],
                                        amount=0.5)
        obed9= Jidlo.objects.create(
            name="Polévka s masovými kuličkami a zeleninový salát",
            type="obed",
            preparation=(
                "Uvař polévku s masovými kuličkami z hovězího masa. "
                "Salát připrav z rajčat, papriky a okurky."
            )
        )
        RecipeIngredient.objects.create(jidlo=obed9, ingredient=ingredient_objects["Hovězí maso"], amount=350)
        RecipeIngredient.objects.create(jidlo=obed9, ingredient=ingredient_objects["Rajčata"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed9, ingredient=ingredient_objects["Paprika"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed9, ingredient=ingredient_objects["Okurka"], amount=60)
        obed10 = Jidlo.objects.create(
            name="Borsč s bramborem a zelím, pečená ryba se zeleninou",
            type="obed",
            preparation=(
                "Uvař boršč z brambor, zelí, mrkve a cibule s trochou oleje. "
                "Rybu upeč v troubě a podávej se salátem z rajčat a okurek."
            )
        )

        # Борщ
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Červená řepa"],
                                        amount=60)
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Rajčatový protlak"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Brambory vařené"],
                                        amount=30)
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Zelí bílé"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Mrkev"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Cibule zelená"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=10)

        # Рыба
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Treska"], amount=170)

        # Овощи
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Rajčata"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed10, ingredient=ingredient_objects["Okurka"], amount=100)
        obed12 = Jidlo.objects.create(
            name="Rýže se zeleninou",
            type="obed",
            preparation="Uvař bílou rýži a smíchej s dušenou zeleninovou směsí."
        )

        RecipeIngredient.objects.create(jidlo=obed12,ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"], amount=150)
        RecipeIngredient.objects.create(jidlo=obed12, ingredient=ingredient_objects["Mražená zelenina havajská směs"], amount=100)
        obed13 = Jidlo.objects.create(
            name="Zeleninová polévka",
            type="obed",
            preparation="Uvař zeleninový vývar s bramborami, mrkví, cibulí a brokolicí."
        )

        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Brambory vařené"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Mrkev"], amount=60)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Brokolice"], amount=80)

        # 🔸 Dušené hovězí se zeleninou (тушеная говядина с овощами)
        obed13 = Jidlo.objects.create(
            name="Dušené hovězí se zeleninou",
            type="obed",
            preparation="Hovězí maso podusíme s mrkví, cibulí a paprikou."
        )

        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Hovězí maso"], amount=170)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Mrkev"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Paprika"], amount=20)
        obed14 = Jidlo.objects.create(
            name="Boršč bez brambor, pečené kuře a zeleninový salát",
            type="obed",
            preparation=(
                "Uvař boršč bez brambor. Kuře upeč v troubě. "
                "Připrav zeleninový salát ze sezónní zeleniny podle chuti."
            )
        )

        # Борщ без картошки
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Červená řepa"],
                                        amount=120)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Mrkev"], amount=40)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Zelí bílé"],
                                        amount=40)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=10)

        # Курица запечённая
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Kuřecí prsa"],
                                        amount=160)

        # Салат овощной (огурцы, помидоры, перец)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Okurka"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Rajčata"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Paprika"], amount=40)
        obed15 = Jidlo.objects.create(
            name="Dušené kuře s vinaigrettem a chlebem",
            type="obed",
            preparation=(
                "Kuřecí maso podusit na pánvi s cibulí a trochou oleje. "
                "Podávej s vinaigrettem a krajíčkem chleba."
            )
        )

        # 🥩 Тушёная курица
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Kuřecí prsa"],
                                        amount=200)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Cibule zelená"],
                                        amount=30)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Rostlinný olej"],
                                        amount=10)

        # 🥗 Винегрет (предположительно классический: řepa, brambory, kyselé okurky, hrášek, olej)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Červená řepa"],
                                        amount=80)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Brambory vařené"],
                                        amount=60)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Okurky nakládané"],
                                        amount=30)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Hrášek zelený"],
                                        amount=30)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=10)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Chléb žitný"], amount=30)
        obed16 = Jidlo.objects.create(
            name="Tefteli v rajčatovo-smetanové omáčce s okurkou a chlebem",
            type="obed",
            preparation=(
                "Smíchejte mleté maso, vařenou rýži, nastrouhanou mrkev, nakrájenou cibuli, vejce, sůl a pepř. "
                "Vytvarujte kuličky, smažte na oleji. Omáčku připravte z rajčatové pasty, smetany a vody. "
                "Vložte kuličky do omáčky a duste přikryté cca 20 minut. Podávejte s okurkou a chlebem."
            )
        )

        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Mleté maso (vepřové)"],
                                        amount=100)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Mrkev"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed16,
                                        ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Vejce"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Smetana"], amount=8)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Rajčatový protlak"],
                                        amount=8)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Rostlinný olej"], amount=8)

        # Дополнительно:
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Okurka"], amount=150)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Chléb žitný"], amount=50)
        # 🍞 Хлеб
        vecere2 = Jidlo.objects.create(
            name="Kuřecí a havajský kastrol",
            type="vecere",
            preparation=(
                "Kuřecí řízek nakrájejte na kostky a smažte na pánvi s olejem 10–15 min. "
                "Osolte, opepřete a posypte kořením na kuře. Přendejte kuře na talíř. "
                "Do stejné pánve dejte havajský mix se 75 ml vody, duste 10 min. "
                "Troubu předehřejte na 210 °C. Zapékací misku potřete olejem, vložte směs, "
                "navrch kuře. Vejce rozšlehejte, osolte a nalijte do misky. "
                "Pečte 20–25 min při 210 °C."
            )
        )
        RecipeIngredient.objects.create(jidlo=vecere2, ingredient=ingredient_objects["Kuřecí prsa"], amount=150)
        RecipeIngredient.objects.create(jidlo=vecere2, ingredient=ingredient_objects["Mražená zelenina havajská směs"],
                                        amount=100)
        RecipeIngredient.objects.create(jidlo=vecere2, ingredient=ingredient_objects["Vejce"], amount=120)
        RecipeIngredient.objects.create(jidlo=vecere2, ingredient=ingredient_objects["Rostlinný olej"], amount=10)


        # Ужины
        vecere1 = Jidlo.objects.create(
            name="Kuře se zeleninou pečené",
            type="vecere",
            preparation="Smíchej kuře se zeleninou a peč v troubě."
        )
        RecipeIngredient.objects.create(jidlo=vecere1, ingredient=ingredient_objects["Kuřecí prsa"], amount=220)
        RecipeIngredient.objects.create(jidlo=vecere1, ingredient=ingredient_objects["Brokolice"], amount=200)
        vecere3 = Jidlo.objects.create(
            name="Tvorog na večeři",
            type="vecere",
            preparation="Podávejte 180 g tvarohu."
        )
        RecipeIngredient.objects.create(jidlo=vecere3, ingredient=ingredient_objects["Tvaroh"], amount=180)
        vecere4 = Jidlo.objects.create(
            name="Kuřecí bitky se salátem z červené řepy",
            type="vecere",
            preparation=(
                "Kousky kuřecího masa osolíme, opepříme, obalíme ve vajíčku a mouce. "
                "Smažíme na pánvi s olejem. "
                "Salát: nastrouháme červenou řepu a jablko, přidáme pokrájené sušené švestky a vlašské ořechy. "
                "Vrstvy promažeme jogurtem a necháme odležet."
            )
        )

        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Kuřecí prsa"], amount=120)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Vejce"], amount=60)  # 1 ks
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Mouka"], amount=32)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Rostlinný olej"], amount=10)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Sůl"], amount=5)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Pepř černý mletý"], amount=2)

        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Červená řepa"], amount=80)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Jablko"], amount=80)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Sušené švestky"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Vlašské ořechy"], amount=20)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Řecký jogurt bíly 0 % tuku"],
                                        amount=20)
        vecere5 = Jidlo.objects.create(
            name="Zeleninové ragú s Zelí bílé",
            type="vecere",
            preparation=(
                "Na oleji osmaž cibuli, přidej mrkev, cuketu, papriku, rajčata a kapustu. "
                "Osol, opepři a dus cca 15 minut. Nakonec přidej předvařené brambory a krátce prohřej."
            )
        )

        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Zelí bílé"], amount=90)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Brambory vařené"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Mrkev"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Cuketa"], amount=80)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Paprika"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Rajčata"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=10)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Sůl"], amount=1)
        RecipeIngredient.objects.create(jidlo=vecere5, ingredient=ingredient_objects["Pepř černý mletý"],
                                        amount=0.5)
        vecere6= Jidlo.objects.create(
            name="Vařená hovězí s Ledový salát-okurkovým salátem",
            type="vecere",
            preparation="Podávej vařené hovězí maso s čerstvým salátem z kapusty a okurek. Dochutit solí, pepřem a trochou oleje."
        )

        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Hovězí maso"], amount=170)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Ledový salát"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Okurka"], amount=80)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Sůl"], amount=1)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Pepř černý mletý"],
                                        amount=0.5)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=5)
        vecere7 = Jidlo.objects.create(
            name="Zeleninová zapekanka s kuřecím masem a havajskou směsí",
            type="vecere",
            preparation=(
                "Nakrájej kuřecí maso, přidej havajskou zeleninovou směs smažte na pánvi 10 minut přidat trochou oleje. "
                "V míse smíchej vejce se smetanou a dochuť solí. "
                "Vše vlož do zapékací mísy a peč v troubě při 180 °C asi 20-25 minut."
            )
        )

        RecipeIngredient.objects.create(jidlo= vecere7, ingredient=ingredient_objects["Kuřecí prsa"], amount=100)
        RecipeIngredient.objects.create(jidlo= vecere7,
                                        ingredient=ingredient_objects["Mražená zelenina havajská směs"], amount=90)
        RecipeIngredient.objects.create(jidlo= vecere7, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo= vecere7, ingredient=ingredient_objects["Smetana"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere7, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=10)
        # 🔸 Kuřecí karbanátky (куриные котлеты)
        vecere8 = Jidlo.objects.create(
            name="Kuřecí karbanátky",
            type="vecere",
            preparation=(
                "Mleté kuřecí maso smíchej s vejcem, solí a pepřem. "
                "Vytvoř kotlety a smaž je na pánvi s trochou oleje."
            )
        )
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Kuřecí prsa"], amount=150)
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Vejce"], amount=20)
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Rostlinný olej"],
                                        amount=10)

        # 🔸 Salát z kapusty a okurky
        vecere8 = Jidlo.objects.create(
            name="Salát z Zelí bílé a okurky",
            type="vecere",
            preparation="Nakrájej čerstvou kapustu a okurky, smíchej a dochuť dle chuti."
        )
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Zelí bílé"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Okurka"], amount=80)
        vecere9 = Jidlo.objects.create(
            name="Pečená treska",
            type="vecere",
            preparation=(
                "Tresku osol, opepři a upeč v troubě na 180 °C cca 20 minut. "
                "Můžeš přidat bylinky dle chuti."
            )
        )
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Treska"], amount=170)
        vecere9 = Jidlo.objects.create(
            name="Řecký salát se sýrem feta",
            type="vecere",
            preparation=(
                "Nakrájej zeleninu a sýr feta na kostky. Přidej koření, bylinky a důkladně promíchej. "
                "Podávej vychlazený jako lehkou večeři."
            )
        )

        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Sýr feta"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Okurka"], amount=70)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Rajčata"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Paprika"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Červená cibule"],
                                        amount=10)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Petržel"], amount=5)
        vecere10 = Jidlo.objects.create(
            name="Pohanková kaše se zeleninovým salátem",
            type="vecere",
            preparation="Uvař pohanku a podávej s nakrájej mladou kapustu, okurky a smíchej s kukuřicí. "
        "Přidej špetku soli, nasekanou petrželku a majonézu. Promíchej."
        )

        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Pohanka vařená"], amount=180)
        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Kapusta"],
                                        amount=60)
        RecipeIngredient.objects.create(jidlo=vecere10,
                                        ingredient=ingredient_objects["Kukuřice konzervovaná"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Okurka"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Majonéza"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Petržel"], amount=5)
        vecere11  = Jidlo.objects.create(
            name="Pečená ryba se salátem s tuňákem a vejcem",
            type="vecere",
            preparation=(
                "Rybu upečeme v troubě. "
                "Zatím připravíme salát z vařeného vejce, tuňáka, kyselých okurek, kukuřice, červené cibule. "
                "Dochutíme solí a pepřem, promícháme se zakysanou smetanou."
            )
        )

        # Ингредиенты:
        RecipeIngredient.objects.create(jidlo=vecere11 , ingredient=ingredient_objects["Treska"],
                                        amount=210)
        RecipeIngredient.objects.create(jidlo=vecere11 , ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere11 ,
                                        ingredient=ingredient_objects["Tuňák konzerva ve vlastní šťávě"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere11 ,
                                        ingredient=ingredient_objects["Okurky sterilované"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere11 ,
                                        ingredient=ingredient_objects["Kukuřice konzervovaná"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere11 , ingredient=ingredient_objects["Červená cibule"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=vecere11 , ingredient=ingredient_objects["Smetana"],
                                        amount=20)
        vecere12 = Jidlo.objects.create(
            name="Hovězí maso na smetaně s cibulí a rajčatovým protlakem",
            type="vecere",
            preparation=(
                "Nakrájej cibuli a osmahni ji na pánvi. Přidej mouku, rajčatový protlak a smetanu, "
                "promíchej a zalij vodou. Přidej na kousky nakrájené hovězí maso, osol a opepři. "
                "Vař pod pokličkou na mírném ohni do změknutí masa."
            )
        )

        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Hovězí maso"],
                                        amount=500)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Červená cibule"],
                                        amount=180)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Smetana"],
                                        amount=150)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Mouka"],
                                        amount=10)  # 1 lžíce ≈ 10 g
        RecipeIngredient.objects.create(jidlo=vecere12,
                                        ingredient=ingredient_objects["Rajčatový protlak"],
                                        amount=5)  # 1 čajová lžička ≈ 5 g
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Sůl"], amount=3)
        RecipeIngredient.objects.create(jidlo=vecere12,
                                        ingredient=ingredient_objects["Pepř černý mletý"], amount=1)
        vecere12 = Jidlo.objects.create(
            name="Zeleninový salát (k večeři)",
            type="vecere",
            preparation="Nakrájej čerstvé okurky, rajčata a zelí. Promíchej se solí a trochou oleje nebo citronové šťávy."
        )

        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Okurka"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Rajčata"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Ledový salát"], amount=40)


        self.stdout.write(self.style.SUCCESS("✅ Seed выполнен с категориями!"))
        for j in Jidlo.objects.all():
            self.stdout.write(f"{j.name} → {j.get_macros_display()}")