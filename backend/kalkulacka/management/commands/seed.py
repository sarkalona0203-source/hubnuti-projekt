from django.core.management.base import BaseCommand
from kalkulacka.models import Ingredient, Jidlo, RecipeIngredient
from django.core.files import File

from django.conf import settings
from PIL import Image
from django.core.files.base import ContentFile
import io, os, gc

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
            "Kuřecí prsa": ((120, 23, 3, 0), "maso", 22.5),
            "Hovězí maso": ((304, 26, 21, 0), "maso",38),
            "Kuřecí játra": ((170, 20, 12, 1), "maso",12),
            "Mleté maso (vepřové)": ((270, 17, 23, 0), "maso",28),
            "Kuřecí maso (mleté)": ((120, 22, 3, 0), "maso",25),
            "Kuřecí maso (vařené)": ((160, 30, 3, 0), "maso", 27),


            # 🐟 Ryby
            "Makrela": ((190, 20, 15, 0), "ryba",30),
            "Játra tresky": ((613, 4.2, 65.7, 1.2), "ryba",70),
            "Treska": ((82, 18, 0.7, 0), "ryba",28),

            # 🥛 Mléčné výrobky

            "Tvaroh": ((120, 11, 4, 3), "mlecne", 25),
            "Řecký jogurt bíly 0 % tuku": ((114, 10, 0, 4), "mlecne", 16),
            "Jogurt": ((80, 5, 2.5, 6), "mlecne",13),
            "Kefír": ((59, 3.3, 3.2, 4.6), "mlecne",5),
            "Mléko polotučné 1,5 % tuku": ((46, 3.3, 1.5, 4.8), "mlecne", 3),
            "Smetana": ((228, 2, 20, 3), "mlecne", 17),
            "Sýr feta": ((264, 14, 21, 4),"mlecne", 40),
            "Máslo": ((717, 0.8, 81, 0),"mlecne", 3),

            # 🧀 Sýry
            "Eidam sýr 30 % tuku": ((263, 27, 17, 1.6), "syry", 27),
            "Tvrdý sýr (průměr)": ((250, 26, 27, 2), "syry", 34),
            "Mozzarella": ((280, 18, 17, 3), "syry",40),
            "Sýr suluguni": ((320, 25, 25, 0), "syry", 62),

            # 🥦 Zelenina
            "Okurka": ((31, 1, 0, 4), "zelenina", 8),
            "Rajčata": ((42, 1, 0, 6), "zelenina", 7),
            "Rajčata cherry": ((18, 1, 0, 4), "zelenina", 12),
            "Mrkev": ((42, 1, 0, 10), "zelenina", 4),
            "Paprika": ((40, 1, 0, 14), "zelenina", 10),
            "Brokolice": ((48, 4, 0, 7), "zelenina", 8),
            "Ledový salát": ((14, 1, 0, 3), "zelenina", 6),
            "Žampiony": ((22, 3, 0, 3), "zelenina", 12),
            "Mražená zelenina havajská směs": ((90, 2.0, 1.0, 16), "zelenina", 8),
            "Cuketa": ((17, 1.2, 0.3, 3.1), "zelenina", 6),
            "Petržel": ((36, 3, 0, 6), "zelenina", 12),
            "Česnek": ((149, 6, 0, 33), "zelenina", 33),
            "Cibule zelená": ((32, 1, 0, 6), "zelenina", 4),
            "Červená cibule": ((40, 1, 0, 9), "zelenina", 2.5),
            "Červená řepa": ((43, 1.6, 0.2, 10), "zelenina", 2.5),
            "Kapusta": ((27, 1.3, 0.2, 6), "zelenina",3),
            "Kukuřice konzervovaná": ((98, 3.2, 1.5, 19), "zelenina",15),
            "Okurky nakládané": ((18, 0.6, 0.1, 2.4),"zelenina",10),
            "Hrášek zelený": ((81, 5.4, 0.4, 14),"zelenina", 10),
            "Brambory": ((77, 2, 0.1, 17), "zelenina", 2.5),
            "Zelí": ((25, 1.3, 0.1, 6), "zelenina", 2.5),
            # 🍎 Ovoce
            "Banán": ((88, 1, 0, 23), "ovoce",4),
            "Jablko": ((52, 0, 0, 14), "ovoce",5),
            "Avokádo": ((160, 2, 15, 9), "ovoce", 14),
            "Švestky": ((46, 0.7, 0.3, 11), "ovoce", 6 ),
            "Broskev": ((39, 0.9, 0.3, 10), "ovoce", 8),
            "Dýně": ((26, 1, 0.1, 6),"ovoce", 6),
            "Sušené meruňky": ((284, 5, 0.5, 62),"ovoce", 72),
            "Sušené švestky": ((240, 2.3, 0.7, 64),"ovoce", 20),
            "Rozinky": ((299, 3.1, 0.5, 79),"ovoce", 14),
            "Sušené fíky": ((249, 3.3, 0.9, 58),"ovoce", 40),

            # 🌾 Obiloviny a přílohy
            "Ovesná kaše vařené": ((101, 2.5, 1.5, 12), "obiloviny", 12),
            "Pohanka vařená": ((110, 4, 1, 20), "obiloviny", 5),
            "Pšenice kaše vařené": ((109, 4.5, 0.4, 27), "obiloviny",6 ),
            "Rýže bílá dlouhozrnná vařená": ((130, 2.7, 0.3, 28), "obiloviny", 7),
            "Bulgur vařeni": ((83, 3.1, 0.2, 18), "obiloviny", 5),
            "Brambory vařené": ((86, 2, 0, 20), "obiloviny", 3),
            "Rýže suchá": ((365, 7, 1, 79),"obiloviny", 10),
            "Krupice suchá": ((360, 10, 1, 76),"obiloviny", 5.5),
            "Ovesná kaše suchá": ((350, 2.5, 1.5, 60), "obiloviny",4),

            # 🧈 Tuky
            "Rostlinný olej": ((884, 0, 100, 0), "tuky", 5),
            "Olej slunečnicový": ((884, 0, 100, 0), "tuky", 5),
            "Olivový olej": ((884, 0, 100, 0), "tuky", 30),

            # 🍬 Ostatní
            "Vejce": ((155, 13, 11, 1), "ostatni",12),
            "Mouka": ((364, 10, 1, 76), "ostatni", 2.5),
            "Cukr": ((387, 0, 0, 100), "ostatni", 2.5),
            "Vanilkový cukr": ((400, 0, 0, 100), "ostatni", 57),
            "Vlašské ořechy": ((654, 15, 65, 14),"ostatni", 40),
            "Tresčí játra": ((613, 13, 65, 0),"ostatni", 70),
            "Pepř černý mletý": ((251, 10.4, 3.3, 64), "ostatni", 100),
            "Sůl": ((0, 0, 0, 0),"ostatni", 1),
            "Čerstvé bylinky": ((43, 3, 1, 7),"ostatni", 35),
            "Rajčatový protlak": ((82, 1.5, 0.3, 18),"ostatni", 11),
            "Zelí bílé": ((25, 1.3, 0.1, 6),"ostatni", 2),
            "Lesní plody": ((50, 1, 0.3, 12),"ostatni", 35),
            "Majonéza": ((450, 1, 75, 2),"ostatni", 20),
            "Tuňák konzerva ve vlastní šťávě": ((116, 25, 1, 0),"ostatni", 33),
            "Okurky sterilované": ((19, 0.5, 0.2, 4),"ostatni", 8),
            "Chléb žitný": ((227, 5.6, 1.1, 43),"ostatni", 12),
            "Lavaš": ((260, 8, 2, 50), "ostatni", 20),
            "Čokoláda hořká 70 %+": ((600, 7, 42, 46), "ostatni", 70),  # в 100 г
            "Zefír (marshmallow bez cukru)": ((300, 2, 0, 75), "ostatni", 37.5 ),  # в 100 г
            "Želé bonbóny bez cukru": ((250, 2, 0.5, 60), "ostatni", 25),
            "Jogurt sladký (ovocný)": ((110, 3, 2.5, 15), "ostatni", 20),  # на 100 г# в 100 г
            "Croissant": ((410, 8, 22, 44), "ostatni", 24),
            "Proteinová tyčinka": ((162, 18, 2, 19), "ostatni", 60),
            "Protein": ((400, 80, 7, 5), "doplněk", 72),
        }

        # 🔹 Заполняем таблицу Ingredient
        ingredient_objects = {}
        for name, (nutrients, category, price) in produkty.items():
            kcal, protein, fat, carbs = nutrients
            ingr = Ingredient.objects.create(
                name=name,
                calories_per_100g=kcal,
                protein_per_100g=protein,
                fat_per_100g=fat,
                carbs_per_100g=carbs,
                unit="g",
                category=category,
                price=price,
            )
            ingredient_objects[name] = ingr

        # Завтраки
        snidane1 = Jidlo.objects.create(
            name="Tvaroh se smetanou",
            type="snidane",
            preparation="Smíchej tvaroh se smetanou."
        )

        img_path = os.path.join(settings.MEDIA_ROOT,
                                "jidla/depositphotos_73134653-stock-photo-cottage-cheese-with-strawberries-and.jpg")

        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane1.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane1.save()
        RecipeIngredient.objects.create(jidlo=snidane1, ingredient=ingredient_objects["Tvaroh"], amount=100)
        RecipeIngredient.objects.create(jidlo=snidane1, ingredient=ingredient_objects["Smetana"], amount=70)
        print("✅ Přidáno jídlo:", snidane1.name)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane1
        gc.collect()





        snidane2 = Jidlo.objects.create(
            name = "Vejce se zeleninou",
            type = "snidane",
            preparation = "Uvař vejce a podávej se zeleninovým salátem."
         )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/colorful-breakfast-bowl-with-eggs-and-vegetables.webp")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane2.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane2.save()
        print("✅ Přidáno jídlo:", snidane2.name)
        RecipeIngredient.objects.create(jidlo=snidane2, ingredient=ingredient_objects["Vejce"], amount=100)
        RecipeIngredient.objects.create(jidlo=snidane2, ingredient=ingredient_objects["Mrkev"], amount=80)
        RecipeIngredient.objects.create(jidlo=snidane2, ingredient=ingredient_objects["Paprika"], amount=80)

        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane2
        gc.collect()


        snidane_nove = Jidlo.objects.create(
            name="Tvarohové placky",
            preparation=(
                "Smíchej tvaroh, vejce, mouku, cukr a vanilkový cukr. "
                "Vytvoř placky, obalte v mouce a smažte na pánvi s olejem."
            )
        )

        # Добавляем изображение
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/breakfast-7160133_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane_nove.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane_nove.save()
        print("✅ Přidáno jídlo:", snidane_nove.name)
        # Добавляем ингредиенты
        RecipeIngredient.objects.create(jidlo=snidane_nove, ingredient=ingredient_objects["Tvaroh"], amount=120)
        RecipeIngredient.objects.create(jidlo=snidane_nove, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane_nove, ingredient=ingredient_objects["Mouka"], amount=30)
        RecipeIngredient.objects.create(jidlo=snidane_nove, ingredient=ingredient_objects["Cukr"], amount=16)
        RecipeIngredient.objects.create(jidlo=snidane_nove, ingredient=ingredient_objects["Rostlinný olej"], amount=10)
        RecipeIngredient.objects.create(jidlo=snidane_nove, ingredient=ingredient_objects["Vanilkový cukr"], amount=5)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane_nove
        gc.collect()


        snidane4, created = Jidlo.objects.get_or_create(
            name="Ovesná kaše s banánem",
            defaults={
                "type": "snidane",
                "preparation": "Uvař ovesnou kaši a přidej nakrájený banán."
            }
        )

        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/muesli.jpg.webp")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane4.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane4.save()
        print("✅ Přidáno jídlo:", snidane4.name)

        # ✅ Удаляем старые ингредиенты
        snidane4.ingredients.all().delete()

        # ✅ Добавляем новые ингредиенты
        RecipeIngredient.objects.create(
            jidlo=snidane4,
            ingredient=ingredient_objects["Ovesná kaše suchá"],
            amount=50
        )
        RecipeIngredient.objects.create(
            jidlo=snidane4,
            ingredient=ingredient_objects["Banán"],
            amount=100
        )
        RecipeIngredient.objects.create(
            jidlo=snidane4,
            ingredient=ingredient_objects["Mléko polotučné 1,5 % tuku"],
            amount=200
        )

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane4
        gc.collect()



        snidane5 = Jidlo.objects.create(
            name="Tvaroh s ovocem a ořechy",
            type="snidane",
            preparation="Smíchej tvaroh s nakrájeným ovocem a posyp ořechy."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/bowl-3366480_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane5.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane5.save()
        print("✅ Přidáno jídlo:", snidane5.name)
        RecipeIngredient.objects.create(jidlo=snidane5, ingredient=ingredient_objects["Tvaroh"], amount=150)
        RecipeIngredient.objects.create(jidlo=snidane5, ingredient=ingredient_objects["Jablko"], amount=100)
        RecipeIngredient.objects.create(jidlo=snidane5, ingredient=ingredient_objects["Banán"], amount=50)
        # Предположим, что у тебя есть "Vlašské ořechy" (грецкие орехи)
        RecipeIngredient.objects.create(jidlo=snidane5, ingredient=ingredient_objects["Vlašské ořechy"], amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane5
        gc.collect()



        snidane6 = Jidlo.objects.create(
            name="Vejce na tvrdo s okurkou",
            type="snidane",
            preparation="Uvař vejce na tvrdo a podávej s čerstvou okurkou."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/boiled-eggs-on-a-plate.jpg.webp")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane6.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane6.save()
        print("✅ Přidáno jídlo:", snidane6.name)
        RecipeIngredient.objects.create(jidlo=snidane6, ingredient=ingredient_objects["Vejce"], amount=120)
        RecipeIngredient.objects.create(jidlo=snidane6, ingredient=ingredient_objects["Okurka"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane6, ingredient=ingredient_objects["Rajčata"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane6, ingredient=ingredient_objects["Paprika"], amount=60)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane6
        gc.collect()


        snidane7 = Jidlo.objects.create(
            name="Omeleta se zeleninou",
            type="snidane",
            preparation="Rozšlehej vejce, osol, opepři. Přidej nakrájenou zeleninu a smaž na pánvi s trochou oleje."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/omelet-3433227_1280_7ubkP9N.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane7.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane7.save()
        print("✅ Přidáno jídlo:", snidane7.name)

        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Vejce"], amount=120)  # 2 vejce
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Paprika"], amount=40)
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Rajčata"], amount=40)
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=snidane7, ingredient=ingredient_objects["Rostlinný olej"], amount=5)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane7
        gc.collect()


        snidane8 = Jidlo.objects.create(
            name="Pohanková kaše a salát s játry tresky",
            type="snidane",
            preparation=(
                "Uvař pohanku. Připrav salát: smíchej játra tresky, kukuřici, nakrájenou okurku, osol a opepři. "
                "Přidej čerstvé bylinky podle chuti."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/c605467e-96dd-4acd-9fd1-3c3fe71b7611.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane8.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane8.save()
        print("✅ Přidáno jídlo:", snidane8.name)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Pohanka vařená"], amount=170)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Játra tresky"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Kukuřice konzervovaná"],
                                        amount=50)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Okurka"], amount=70)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Sůl"], amount=2)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Pepř černý mletý"], amount=1)
        RecipeIngredient.objects.create(jidlo=snidane8, ingredient=ingredient_objects["Čerstvé bylinky"], amount=5)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane8
        gc.collect()


        snidane9 = Jidlo.objects.create(
            name="Omeleta se sýrem",
            type="snidane",
            preparation="Rozšlehej vejce s mlékem, osol. Nalij na pánev, přidej nastrouhaný sýr a osmaž omeletu."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/breakfast-8266548_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane9.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane9.save()
        print("✅ Přidáno jídlo:", snidane9.name)
        RecipeIngredient.objects.create(jidlo=snidane9, ingredient=ingredient_objects["Vejce"], amount=120)
        RecipeIngredient.objects.create(jidlo=snidane9, ingredient=ingredient_objects["Eidam sýr 30 % tuku"],
                                        amount=40)
        RecipeIngredient.objects.create(jidlo=snidane9,
                                        ingredient=ingredient_objects["Smetana"], amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane9
        gc.collect()



        snidane10 = Jidlo.objects.create(
            name="Ovesná kaše s lesními plody",
            type="snidane",
            preparation="Uvař ovesnou kaši a podávej s čerstvými nebo mraženými lesními plody."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/breakfast-5422528_1280.jpg")
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                snidane10.obrazek.save(os.path.basename(img_path), File(f), save=True)
        else:
            print("⚠️ Obrázek nenalezen:", img_path)
        print("✅ Přidáno jídlo:", snidane10.name)
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane10.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane10.save()
        print("✅ Přidáno jídlo:", snidane10.name)
        RecipeIngredient.objects.create(jidlo=snidane10, ingredient=ingredient_objects["Ovesná kaše vařené"],
                                        amount=180)
        RecipeIngredient.objects.create(jidlo=snidane10, ingredient=ingredient_objects["Lesní plody"],
                                        amount=160)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane10
        gc.collect()


        snidane11 = Jidlo.objects.create(
            name="Tvarohová zapékaná",
            type="snidane",
            preparation=(
                "Smíchej tvaroh, vejce, trochu cukru a krupici. "
                "Peč v předehřáté troubě na 180 °C asi 35–40 minut."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/berry-delight-dessert-with-vanilla-crust.webp")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane11.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane11.save()
        print("✅ Přidáno jídlo:", snidane11.name)
        RecipeIngredient.objects.create(jidlo=snidane11, ingredient=ingredient_objects["Tvaroh"], amount=150)
        RecipeIngredient.objects.create(jidlo=snidane11, ingredient=ingredient_objects["Vejce"], amount=40)
        RecipeIngredient.objects.create(jidlo=snidane11, ingredient=ingredient_objects["Cukr"], amount=10)
        RecipeIngredient.objects.create(jidlo=snidane11, ingredient=ingredient_objects["Krupice suchá"], amount=20)


        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane11
        gc.collect()


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
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/pancakes-4657443_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane12.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane12.save()
        print("✅ Přidáno jídlo:", snidane12.name)
        RecipeIngredient.objects.create(jidlo=snidane12,
                                        ingredient=ingredient_objects["Mléko polotučné 1,5 % tuku"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane12, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane12, ingredient=ingredient_objects["Mouka"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane12, ingredient=ingredient_objects["Žampiony"], amount=50)
        RecipeIngredient.objects.create(jidlo=snidane12, ingredient=ingredient_objects["Smetana"], amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane12
        gc.collect()
        snidane13 = Jidlo.objects.create(
            name="Dýňová rýžová kaše",
            type="snidane",
            preparation="Uvař dýni s rýží, mlékem, vodou, cukrem a máslem do měkka. Podávej teplé."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/carving-halloween-pumpkin.jpg.webp")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane13.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane13.save()
        print("✅ Přidáno jídlo:", snidane13.name)

        RecipeIngredient.objects.create(jidlo=snidane13, ingredient=ingredient_objects["Dýně"], amount=90)
        RecipeIngredient.objects.create(jidlo=snidane13, ingredient=ingredient_objects["Rýže suchá"],
                                        amount=50)
        RecipeIngredient.objects.create(jidlo=snidane13,
                                        ingredient=ingredient_objects["Mléko polotučné 1,5 % tuku"], amount=60)
        RecipeIngredient.objects.create(jidlo=snidane13, ingredient=ingredient_objects["Cukr"], amount=6)
        RecipeIngredient.objects.create(jidlo=snidane13, ingredient=ingredient_objects["Máslo"], amount=9)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane13
        gc.collect()


        snidane14 = Jidlo.objects.create(
            name="Pečená jablka",
            type="snidane",
            preparation=(
                "Jablka omyj, vykroj jadřince a dej na plech. "
                "Můžeš je posypat skořicí, přidat pár kapek medu nebo oříšky. "
                "Peč v troubě na 180 °C asi 20–25 minut, dokud nezměknou."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/baked-apples-1833618_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snidane14.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snidane14.save()
        print("✅ Přidáno jídlo:", snidane14.name)
        # Ингредиент:
        RecipeIngredient.objects.create(jidlo=snidane14, ingredient=ingredient_objects["Jablko"],
                                        amount=280
                                        )

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snidane14
        gc.collect()


        croissant_syr = Jidlo.objects.create(
            name="Křupavý croissant se sýrem",
            type="snidane",
            preparation=(
                "Rozkroj croissant, vlož plátek sýra (např. Eidam nebo Gouda) a zapékej "
                "v troubě nebo toastovači, dokud sýr nezačne tát a croissant nezíská křupavou kůrku."
            )
        )

        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/bread-7279975_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                croissant_syr.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        croissant_syr.save()
        print("✅ Přidáno jídlo:", croissant_syr.name)

        # Ингредиенты
        RecipeIngredient.objects.create(jidlo=croissant_syr, ingredient=ingredient_objects["Croissant"], amount=60)
        RecipeIngredient.objects.create(jidlo=croissant_syr, ingredient=ingredient_objects["Eidam sýr 30 % tuku"],
                                        amount=20)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del croissant_syr
        gc.collect()


        toast_avokado = Jidlo.objects.create(
            name="Tosty s avokádem",
            type="snidane",
            preparation=(
                "Opékej plátky celozrnného chleba v toastovači. Mezitím rozmačkej avokádo, "
                "přidej špetku soli, pepř a pár kapek citronu. Namaž směs na teplé toasty."
            )
        )

        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/toast-6607782_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                toast_avokado.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        toast_avokado.save()
        print("✅ Přidáno jídlo:", toast_avokado.name)

        # Ингредиенты
        RecipeIngredient.objects.create(jidlo=toast_avokado, ingredient=ingredient_objects["Chléb žitný"],
                                        amount=60)
        RecipeIngredient.objects.create(jidlo=toast_avokado, ingredient=ingredient_objects["Avokádo"], amount=80)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del toast_avokado
        gc.collect()



        # Вторые завтраки / полдники
        svacina1 = Jidlo.objects.create(
            name="Ovoce",
            type ="druhe_snidane",
            preparation="Nakrájej ovoce dle chuti."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/banana-906443_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina1.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina1.save()
        print("✅ Přidáno jídlo:", svacina1.name)

        RecipeIngredient.objects.create(jidlo=svacina1, ingredient=ingredient_objects["Banán"], amount=150)
        RecipeIngredient.objects.create(jidlo=svacina1, ingredient=ingredient_objects["Jablko"], amount=100)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina1
        gc.collect()




        svacina12 = Jidlo.objects.create(
            name ="Jogurt sladký (ovocný)",
            type = "druhe_snidane"
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/raspberries-7213407_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina12.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina12.save()
        print("✅ Přidáno jídlo:", svacina12.name)
        RecipeIngredient.objects.create(jidlo=svacina12, ingredient=ingredient_objects["Jogurt sladký (ovocný)"],
                                        amount=120)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina12
        gc.collect()


        svacina2 = Jidlo.objects.create(
            name="Eidam sýr 30 % tuku",
            type="druhe_snidane"
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/cheese-platter-6153716_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina2.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina2.save()
        print("✅ Přidáno jídlo:", svacina2.name)
        RecipeIngredient.objects.create(jidlo=svacina2, ingredient=ingredient_objects["Eidam sýr 30 % tuku"], amount=40)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina2
        gc.collect()

        svacina3 = Jidlo.objects.create(
            name ="Jogurt",
            type ="svacina",
            preparation="Podávej jogurt samostatně nebo s ovocem."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/raspberries-1925178_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina3.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina3.save()
        print("✅ Přidáno jídlo:", svacina3.name)
        RecipeIngredient.objects.create(jidlo=svacina3, ingredient=ingredient_objects["Řecký jogurt bíly 0 % tuku"],
                                        amount=220)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina3
        gc.collect()


        svacina4 = Jidlo.objects.create(
            name="Sýr jako svačina",
            type="svacina",
            preparation="Podávejte plátek sýru jako lehkou svačinu."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/cheese-platter-6153716_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina4.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina4.save()
        print("✅ Přidáno jídlo:", svacina4.name)
        RecipeIngredient.objects.create(jidlo=svacina4, ingredient=ingredient_objects["Eidam sýr 30 % tuku"], amount=45)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina4
        gc.collect()


        svacina5 = Jidlo.objects.create(
            name="Ovoce: švestky a broskve",
            type="druhe_snidane",
            preparation="Omyjte ovoce, nakrájejte na kousky a podávejte jako lehkou dopolední svačinu."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/fruit-3060421_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina5.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina5.save()
        print("✅ Přidáno jídlo:", svacina5.name)
        RecipeIngredient.objects.create(jidlo=svacina5, ingredient=ingredient_objects["Švestky"], amount=100)
        RecipeIngredient.objects.create(jidlo=svacina5, ingredient=ingredient_objects["Broskev"], amount=120)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina5
        gc.collect()



        svacina8 = Jidlo.objects.create(
            name="Míchané ovoce",
            type="druhe_snidane",
            preparation="Nakrájejte ovoce a podávejte čerstvé."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/fruit-189246_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina8.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina8.save()
        print("✅ Přidáno jídlo:", svacina8.name)

        RecipeIngredient.objects.create(jidlo=svacina8, ingredient=ingredient_objects["Banán"], amount=50)
        RecipeIngredient.objects.create(jidlo=svacina8, ingredient=ingredient_objects["Jablko"], amount=50)
        RecipeIngredient.objects.create(jidlo=svacina8, ingredient=ingredient_objects["Švestky"],
                                        amount=50)  # если есть
        RecipeIngredient.objects.create(jidlo=svacina8, ingredient=ingredient_objects["Broskev"],
                                        amount=50)  # если есть

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina8
        gc.collect()

        svacina10 = Jidlo.objects.create(
            name="Vlašské ořechy",
            type="svacina",
            preparation="Podávejte 25 g vlašských ořechů jako rychlou svačinu."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/nuts-3841539_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina10.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina10.save()
        print("✅ Přidáno jídlo:", svacina10.name)
        RecipeIngredient.objects.create(jidlo=svacina10, ingredient=ingredient_objects["Vlašské ořechy"], amount=25)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina10
        gc.collect()


        svacina11 = Jidlo.objects.create(
            name="Sušené ovoce",
            type="druhe_snidane",
            preparation="Podávejte směs sušeného ovoce jako rychlou svačinu."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/o-mai-6087502_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina11.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina11.save()
        print("✅ Přidáno jídlo:", svacina11.name)
        RecipeIngredient.objects.create(jidlo=svacina11, ingredient=ingredient_objects["Sušené švestky"],
                                        amount=25)
        RecipeIngredient.objects.create(jidlo=svacina11, ingredient=ingredient_objects["Rozinky"], amount=10)
        RecipeIngredient.objects.create(jidlo=svacina11, ingredient=ingredient_objects["Sušené meruňky"],
                                        amount=15)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina11
        gc.collect()

        # 🍫 1. Чёрный шоколад
        svacina_choco = Jidlo.objects.create(
            name="Hořká čokoláda 70 % +",
            type="druhe_snidane",
            preparation="Podávejte Hořku čokoládu jako rychlou svačinu."
        )
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/dark-2562840_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina_choco.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina_choco.save()
        print("✅ Přidáno jídlo:", svacina_choco.name)

        RecipeIngredient.objects.create(jidlo=svacina_choco, ingredient=ingredient_objects["Čokoláda hořká 70 %+"],
                                        amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina_choco
        gc.collect()



        # 🍥 2. Зефир без сахара
        svacina_zephyr = Jidlo.objects.create(
            name="Zefír bez cukru",
            type="druhe_snidane",
            preparation="Podávejte Zefír bez cukru jako rychlou svačinu."
        )
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/zephyr-3106246_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina_zephyr.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina_zephyr.save()
        print("✅ Přidáno jídlo:", svacina_zephyr.name)
        RecipeIngredient.objects.create(jidlo=svacina_zephyr,
                                        ingredient=ingredient_objects["Zefír (marshmallow bez cukru)"], amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina_zephyr
        gc.collect()



        # 🍬 3. Желейные конфеты без сахара
        svacina_zele = Jidlo.objects.create(
            name="Želé bonbóny bez cukru",
            type="druhe_snidane",
            preparation="Podávejte Želé bonbóny bez cukru jako rychlou svačinu."
        )
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/gummybears-1618074_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                svacina_zele.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        svacina_zele.save()
        print("✅ Přidáno jídlo:", svacina_zele.name)

        RecipeIngredient.objects.create(jidlo=svacina_zele, ingredient=ingredient_objects["Želé bonbóny bez cukru"],
                                        amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del svacina_zele
        gc.collect()
        # Обеды
        obed1 = Jidlo.objects.create(
            name="Kuře s bulgurem a salátem",
            type="obed",
            preparation="Uvař kuře a bulgur, podávej se zeleninovým salátem."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/e754c5d7-32f7-48e1-a38f-772fd3a407f7.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed1.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed1.save()
        print("✅ Přidáno jídlo:", obed1.name)
        RecipeIngredient.objects.create(jidlo=obed1, ingredient=ingredient_objects["Bulgur vařeni"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed1, ingredient=ingredient_objects["Kuřecí prsa"], amount=170)
        RecipeIngredient.objects.create(jidlo=obed1, ingredient=ingredient_objects["Okurka"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed1, ingredient=ingredient_objects["Rajčata"], amount=100)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed1
        gc.collect()
        obed2 = Jidlo.objects.create(
            name="Houbová polévka",
            type="obed",
            preparation="Uvař houby s mrkví, pohankou, bramborem a olejem."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/mushroom-soup-6164651_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed2.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed2.save()
        print("✅ Přidáno jídlo:", obed2.name)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Žampiony"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Mrkev"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Pohanka vařená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Brambory vařené"], amount=40)
        RecipeIngredient.objects.create(jidlo=obed2, ingredient=ingredient_objects["Olej slunečnicový"], amount=10)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed2
        gc.collect()


        obed3 = Jidlo.objects.create(
            name="Kuřecí filé s salátem",
            type="obed",
            preparation="Uvařené kuřecí filé podávejte s čerstvým salátem ze zelených zelenin."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/chicken-breast-filet-2215709_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed3.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed3.save()
        print("✅ Přidáno jídlo:", obed3.name)
        RecipeIngredient.objects.create(jidlo=obed3, ingredient=ingredient_objects["Kuřecí prsa"], amount=150)
        RecipeIngredient.objects.create(jidlo=obed3, ingredient=ingredient_objects["Ledový salát"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed3, ingredient=ingredient_objects["Okurka"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed3, ingredient=ingredient_objects["Rajčata"], amount=60)
        # Можно добавить огурce, rajčata, papriku по вкусу

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed3
        gc.collect()

        obed4 = Jidlo.objects.create(
            name="Zeleninový salát s avokádem",
            type="obed",
            preparation="Smíchejte všechny ingredience a dochuťte limetkou a olivovým olejem."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/food-3791530_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed4.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed4.save()
        print("✅ Přidáno jídlo:", obed4.name)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Rajčata"], amount=200)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Okurka"], amount=200)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Avokádo"], amount=150)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Červená cibule"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed4, ingredient=ingredient_objects["Olivový olej"], amount=5)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed4
        gc.collect()

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
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/ratatule-4457141_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed5.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed5.save()
        print("✅ Přidáno jídlo:", obed5.name)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Cuketa"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Rajčata cherry"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Petržel"], amount=10)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Česnek"], amount=3)
        RecipeIngredient.objects.create(jidlo=obed5, ingredient=ingredient_objects["Olivový olej"], amount=30)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed5
        gc.collect()


        obed6 = Jidlo.objects.create(
            name="Salát s tresčí játry a rýží",
            type="obed",
            preparation=(
                "Uvař vejce natvrdo. Nakrájej okurky, přidej tresčí játra, kukuřici, rýži a vejce. "
                "Osol, opepři a přidej nasekanou čerstvou zeleninu dle chuti. Vše smíchej."
            )

        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/528c48ae-b438-4f2f-9c8f-a208fddae921.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed6.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed6.save()
        print("✅ Přidáno jídlo:", obed6.name)

        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Tresčí játra"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Kukuřice konzervovaná"], amount=40)
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Okurka"], amount=90)  # cca 2 ks
        RecipeIngredient.objects.create(jidlo=obed6, ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"],
                                        amount=100)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed6
        gc.collect()


        obed7 = Jidlo.objects.create(
            name="Dušené kuře se zeleninovým salátem",
            type="obed",
            preparation="Kuřecí maso podusíme na mírném ohni s trochou vody. "
                        "Zeleninu nakrájíme a smícháme v salát. Podáváme společně."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/salad-7295553_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed7.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed7.save()
        print("✅ Přidáno jídlo:", obed7.name)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Kuřecí prsa"], amount=220)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Okurka"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Rajčata"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Paprika"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed7, ingredient=ingredient_objects["Cibule zelená"], amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed7
        gc.collect()


        obed20 = Jidlo.objects.create(
            name="Dušené zelí s houbami",
            type="obed",
            preparation="Nakrájej zelí a žampiony. Orestuj cibuli, přidej houby a po chvíli zelí. Osol, opepři a duste doměkka."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/35a8b8f1-3f18-4928-a872-46818bac796e.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed20.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed20.save()
        print("✅ Přidáno jídlo:", obed20.name)
        RecipeIngredient.objects.create(jidlo=obed20, ingredient=ingredient_objects["Zelí bílé"], amount=200)
        RecipeIngredient.objects.create(jidlo=obed20, ingredient=ingredient_objects["Žampiony"], amount=160)
        RecipeIngredient.objects.create(jidlo=obed20, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed20, ingredient=ingredient_objects["Rostlinný olej"], amount=10)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed20
        gc.collect()


        obed8 = Jidlo.objects.create(
            name="Postní boršč a houbový pilaf",
            type="obed",
            preparation=(
                "Uvař postní boršč z červené řepy, zelí, brambory, mrkve, cibule a rajského protlaku. "
                "Na pánvi připrav houbový pilaf z vařené rýže, žampionů a zeleniny."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/shrimp-1024741_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed8.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed8.save()
        print("✅ Přidáno jídlo:", obed8.name)
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
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"],
                                        amount=100)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Žampiony"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Mrkev"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed8, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=5)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed8
        gc.collect()



        obed11 = Jidlo.objects.create(
            name="Zeleninová polévka a kuřecí rolky se sýrem",
            type="obed",
            preparation=(
                "Uvař zeleninovou polévku z mrkve, cibule, brambor a brokolice. "
                "Kuřecí prsa rozklepej, naplň sýrem a bylinkami, sroluj a upeč nebo osmaž."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/chicken-noodle-soup-6729002_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed11.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed11.save()
        print("✅ Přidáno jídlo:", obed11.name)
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
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed11
        gc.collect()


        obed21= Jidlo.objects.create(
            name="Polévka s masovými kuličkami a zeleninový salát",
            type="obed",
            preparation=(
                "Uvař polévku s masovými kuličkami z hovězího masa. "
                "Salát připrav z rajčat, papriky a okurky."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/knedlickova-3815789_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed21.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed21.save()
        print("✅ Přidáno jídlo:", obed21.name)
        RecipeIngredient.objects.create(jidlo=obed21, ingredient=ingredient_objects["Hovězí maso"], amount=150)
        RecipeIngredient.objects.create(jidlo=obed21, ingredient=ingredient_objects["Zelí bílé"], amount=60)
        RecipeIngredient.objects.create(jidlo=obed21, ingredient=ingredient_objects["Mrkev"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed21, ingredient=ingredient_objects["Cibule zelená"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=obed21, ingredient=ingredient_objects["Rajčata"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed21, ingredient=ingredient_objects["Paprika"], amount=70)
        RecipeIngredient.objects.create(jidlo=obed21, ingredient=ingredient_objects["Okurka"], amount=60)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed21
        gc.collect()


        obed10 = Jidlo.objects.create(
            name="Borsč s bramborem a zelím, pečená ryba se zeleninou",
            type="obed",
            preparation=(
                "Uvař boršč z brambor, zelí, mrkve a cibule s trochou oleje. "
                "Rybu upeč v troubě a podávej se salátem z rajčat a okurek."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/food-696305_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed10.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed10.save()
        print("✅ Přidáno jídlo:", obed10.name)

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

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed10
        gc.collect()


        obed12 = Jidlo.objects.create(
            name="Rýže se zeleninou",
            type="obed",
            preparation="Uvař bílou rýži a smíchej s dušenou zeleninovou směsí."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/fried-rice-4709645_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed12.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed12.save()
        print("✅ Přidáno jídlo:", obed12.name)

        RecipeIngredient.objects.create(jidlo=obed12, ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"],
                                        amount=150)
        RecipeIngredient.objects.create(jidlo=obed12, ingredient=ingredient_objects["Mražená zelenina havajská směs"],
                                        amount=100)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed12
        gc.collect()


        obed13 = Jidlo.objects.create(
            name="Zeleninová polévka",
            type="obed",
            preparation="Uvař zeleninový vývar s bramborami, mrkví, cibulí a brokolicí."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/soup-2897649_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed13.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed13.save()
        print("✅ Přidáno jídlo:", obed13.name)

        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Brambory vařené"], amount=80)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Mrkev"], amount=60)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed13, ingredient=ingredient_objects["Brokolice"], amount=80)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed13
        gc.collect()


        # 🔸 Dušené hovězí se zeleninou (тушеная говядина с овощами)
        obed14 = Jidlo.objects.create(
            name="Dušené hovězí se zeleninou",
            type="obed",
            preparation="Hovězí maso podusíme s mrkví, cibulí a paprikou."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/dice-cattle-2280690_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed14.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed14.save()
        print("✅ Přidáno jídlo:", obed14.name)

        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Hovězí maso"], amount=170)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Mrkev"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed14, ingredient=ingredient_objects["Paprika"], amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed14
        gc.collect()


        obed15 = Jidlo.objects.create(
            name="Boršč bez brambor, pečené kuře a zeleninový salát",
            type="obed",
            preparation=(
                "Uvař boršč (Červená řepa, Cibule zelená, Zelí bílé, Mrkev)." "Kuře upeč v troubě. "
                "Připrav zeleninový salát ze sezónní zeleniny podle chuti."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/8a52c48c-9395-478a-ac16-8d1ceb77a0cc.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed15.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed15.save()
        print("✅ Přidáno jídlo:", obed15.name)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Červená řepa"],
                                        amount=120)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Mrkev"], amount=40)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Cibule zelená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Zelí bílé"],
                                        amount=40)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=10)
        # Курица запечённая
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Kuřecí prsa"],
                                        amount=80)
        # Салат овощной (огурцы, помидоры, перец)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Okurka"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Rajčata"], amount=50)
        RecipeIngredient.objects.create(jidlo=obed15, ingredient=ingredient_objects["Paprika"], amount=40)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed15
        gc.collect()


        obed16 = Jidlo.objects.create(
            name="Dušené kuře s cibule a vinaigrettem:(Červená řepa, Brambory vařené, Okurky nakládané, Hrášek zelený, Olej slunečnicový)  a chlebem",
            type="obed",
            preparation=(
                "Kuřecí maso podusit na pánvi s cibulí a trochou oleje. "
                "Podávej s vinaigrettem a krajíčkem chleba."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/venegret-4204908_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed16.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed16.save()
        print("✅ Přidáno jídlo:", obed16.name)
        # 🥩 Тушёная курица
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Kuřecí prsa"],
                                        amount=90)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Cibule zelená"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Rostlinný olej"],
                                        amount=10)

        # 🥗 Винегрет (предположительно классический: řepa, brambory, kyselé okurky, hrášek, olej)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Červená řepa"],
                                        amount=40)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Brambory vařené"],
                                        amount=50)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Okurky nakládané"],
                                        amount=30)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Hrášek zelený"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=obed16, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=10)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed16
        gc.collect()

        obed17 = Jidlo.objects.create(
            name="Tefteli v rajčatovo-smetanové omáčce s okurkou a chlebem",
            type="obed",
            preparation=(
                "Smíchejte mleté maso, vařenou rýži, nastrouhanou mrkev, nakrájenou cibuli, vejce, sůl a pepř. "
                "Vytvarujte kuličky, smažte na oleji. Omáčku připravte z rajčatové pasty, smetany a vody. "
                "Vložte kuličky do omáčky a duste přikryté cca 20 minut. Podávejte s okurkou a chlebem."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/food-7239779_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed17.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed17.save()
        print("✅ Přidáno jídlo:", obed17.name)

        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Mleté maso (vepřové)"],
                                        amount=70)
        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Mrkev"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed17,
                                        ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"], amount=30)
        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Vejce"], amount=20)
        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Smetana"], amount=8)
        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Rajčatový protlak"],
                                        amount=8)
        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Rostlinný olej"], amount=8)

        # Дополнительно:
        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Okurka"], amount=100)
        RecipeIngredient.objects.create(jidlo=obed17, ingredient=ingredient_objects["Chléb žitný"], amount=30)
        # 🍞 Хлеб

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed17
        gc.collect()


        obed18 = Jidlo.objects.create(
            name="Bulgur s houbami a zeleninový salát",
            type="vecere",
            preparation=(
                "Bulgur uvař podle návodu na obalu. "
                "Houby nakrájej a osmahni na olivovém oleji s česnekem. "
                "Smíchej s bulgurem. "
                "Zeleninový salát připrav z čerstvé zeleniny dle chuti (např. okurka, rajče, paprika). "
                "Osol, opepři, zakápni citronem nebo olivovým olejem."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/crocus-rebel-5277799_1280 (1).jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed18.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed18.save()
        print("✅ Přidáno jídlo:", obed18.name)
        RecipeIngredient.objects.create(jidlo=obed18, ingredient=ingredient_objects["Bulgur vařeni"],
                                        amount=100)
        RecipeIngredient.objects.create(jidlo=obed18, ingredient=ingredient_objects["Žampiony"],
                                        amount=100)
        RecipeIngredient.objects.create(jidlo=obed18, ingredient=ingredient_objects["Mražená zelenina havajská směs"],
                                        # если у тебя есть общий ингредиент "овощная смесь"
                                        amount=120)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed18
        gc.collect()


        obed19 = Jidlo.objects.create(
            name="Kuřecí karbanátky, houbový pilaf a okurka",
            type="obed",
            preparation=(
                "Z mletého kuřecího masa připrav karbanátky – okořeň, vytvaruj a opeč. "
                "Pilaf uvař z rýže, hub, cibule a koření,  masa 50 g. "
                "Podávej s čerstvou okurkou jako lehkou přílohu."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/mediterranean-falafel-bowl-with-fresh-vegetables.webp")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                obed19.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        obed19.save()
        print("✅ Přidáno jídlo:", obed19.name)
        RecipeIngredient.objects.create(jidlo=obed19, ingredient=ingredient_objects["Kuřecí maso (mleté)"],
                                        amount=120)
        RecipeIngredient.objects.create(jidlo=obed19, ingredient=ingredient_objects["Rýže bílá dlouhozrnná vařená"],
                                        amount=48)
        RecipeIngredient.objects.create(jidlo=obed19, ingredient=ingredient_objects["Žampiony"], amount=40)
        RecipeIngredient.objects.create(jidlo=obed19, ingredient=ingredient_objects["Cibule zelená"], amount=12)
        RecipeIngredient.objects.create(jidlo=obed19, ingredient=ingredient_objects["Olej slunečnicový"], amount=5)
        RecipeIngredient.objects.create(jidlo=obed19, ingredient=ingredient_objects["Okurka"], amount=130)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del obed19
        gc.collect()


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
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/casserole-312852_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere2.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere2.save()
        print("✅ Přidáno jídlo:", vecere2.name)
        RecipeIngredient.objects.create(jidlo=vecere2, ingredient=ingredient_objects["Kuřecí prsa"], amount=120)
        RecipeIngredient.objects.create(jidlo=vecere2, ingredient=ingredient_objects["Mražená zelenina havajská směs"],
                                        amount=80)
        RecipeIngredient.objects.create(jidlo=vecere2, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere2, ingredient=ingredient_objects["Rostlinný olej"], amount=10)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere2
        gc.collect()




        # Ужины
        vecere1 = Jidlo.objects.create(
            name="Kuře se zeleninou pečené",
            type="vecere",
            preparation="Smíchej kuře se zeleninou a peč v troubě."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/972e7bb6-089c-4222-8de7-6bafc53e8679.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere1.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere1.save()
        print("✅ Přidáno jídlo:", vecere1.name)
        RecipeIngredient.objects.create(jidlo=vecere1, ingredient=ingredient_objects["Kuřecí prsa"], amount=150)
        RecipeIngredient.objects.create(jidlo=vecere1, ingredient=ingredient_objects["Brokolice"], amount=170)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere1
        gc.collect()


        vecere3 = Jidlo.objects.create(
            name="Tvorog na večeři",
            type="vecere",
            preparation="Podávejte 180 g tvarohu."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/bowl-3366480_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere3.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere3.save()
        print("✅ Přidáno jídlo:", vecere3.name)
        RecipeIngredient.objects.create(jidlo=vecere3, ingredient=ingredient_objects["Tvaroh"], amount=180)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere3
        gc.collect()


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
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/meal-6815344_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere4.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere4.save()
        print("✅ Přidáno jídlo:", vecere4.name)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Kuřecí prsa"], amount=90)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Vejce"], amount=30)  # 1 ks
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Mouka"], amount=12)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Rostlinný olej"], amount=10)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Sůl"], amount=5)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Pepř černý mletý"], amount=2)

        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Červená řepa"], amount=30)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Jablko"], amount=30)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Sušené švestky"], amount=20)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Vlašské ořechy"], amount=10)
        RecipeIngredient.objects.create(jidlo=vecere4, ingredient=ingredient_objects["Řecký jogurt bíly 0 % tuku"],
                                        amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere4
        gc.collect()

        vecere5 = Jidlo.objects.create(
            name="Zeleninové ragú s Zelí bílé",
            type="vecere",
            preparation=(
                "Na oleji osmaž cibuli, přidej mrkev, cuketu, papriku, rajčata a kapustu. "
                "Osol, opepři a dus cca 15 minut. Nakonec přidej předvařené brambory a krátce prohřej."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/bbq-pepper-stew-834071_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere5.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere5.save()
        print("✅ Přidáno jídlo:", vecere5.name)
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
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere5
        gc.collect()

        vecere6= Jidlo.objects.create(
            name="Vařená hovězí s Ledový salát-okurkovým salátem",
            type="vecere",
            preparation="Podávej vařené hovězí maso s čerstvým salátem z kapusty a okurek. Dochutit solí, pepřem a trochou oleje."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/steak-633323_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere6.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere6.save()
        print("✅ Přidáno jídlo:", vecere6.name)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Hovězí maso"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Ledový salát"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Okurka"], amount=80)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Sůl"], amount=1)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Pepř černý mletý"],
                                        amount=0.5)
        RecipeIngredient.objects.create(jidlo=vecere6, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=5)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere6
        gc.collect()
        vecere7 = Jidlo.objects.create(
            name="Zeleninová zapekanka s kuřecím masem a havajskou směsí",
            type="vecere",
            preparation=(
                "Nakrájej kuřecí maso, přidej havajskou zeleninovou směs smažte na pánvi 10 minut přidat trochou oleje. "
                "V míse smíchej vejce se smetanou a dochuť solí. "
                "Vše vlož do zapékací mísy a peč v troubě při 180 °C asi 20-25 minut."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/casserole-312852_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere7.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere7.save()
        print("✅ Přidáno jídlo:", vecere7.name)

        RecipeIngredient.objects.create(jidlo=vecere7, ingredient=ingredient_objects["Kuřecí prsa"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere7,
                                        ingredient=ingredient_objects["Mražená zelenina havajská směs"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere7, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere7, ingredient=ingredient_objects["Smetana"], amount=30)
        RecipeIngredient.objects.create(jidlo=vecere7, ingredient=ingredient_objects["Olej slunečnicový"],
                                        amount=10)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere7
        gc.collect()

        vecere8 = Jidlo.objects.create(
            name="Kuřecí karbanátky",
            type="vecere",
            preparation=(
                "Mleté kuřecí maso smíchej s vejcem, solí a pepřem. "
                "Vytvoř kotlety a smaž je na pánvi s trochou oleje."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/balloon-kebab-9813739_1280.webp")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere8.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere8.save()
        print("✅ Přidáno jídlo:", vecere8.name)
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Kuřecí prsa"], amount=120)
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Vejce"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Rostlinný olej"],
                                        amount=10)
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Mouka"],
                                        amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere8
        gc.collect()



        # 🔸 Salát z kapusty a okurky
        vecere8 = Jidlo.objects.create(
            name="Salát z Zelí bílé a okurky",
            type="vecere",
            preparation="Nakrájej čerstvou kapustu a okurky, smíchej a dochuť dle chuti."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/0638ec2d-1381-4028-8b7b-12c3b201596c.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere8.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere8.save()
        print("✅ Přidáno jídlo:", vecere8.name)

        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Zelí bílé"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere8, ingredient=ingredient_objects["Okurka"], amount=80)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere8
        gc.collect()


        vecere9 = Jidlo.objects.create(
            name="Pečená treska",
            type="vecere",
            preparation=(
                "Tresku osol, opepři a upeč v troubě na 180 °C cca 20 minut. "
                "Můžeš přidat bylinky dle chuti."
            )
        )

        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/fish-8031138_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere9.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere9.save()
        print("✅ Přidáno jídlo:", vecere9.name)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Treska"], amount=170)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere9
        gc.collect()


        vecere9 = Jidlo.objects.create(
            name="Řecký salát se sýrem feta",
            type="vecere",
            preparation=(
                "Nakrájej zeleninu a sýr feta na kostky. Přidej koření, bylinky a důkladně promíchej. "
                "Podávej vychlazený jako lehkou večeři."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/salad-2173214_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere9.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere9.save()
        print("✅ Přidáno jídlo:", vecere9.name)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Sýr feta"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Okurka"], amount=70)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Rajčata"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Paprika"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Červená cibule"],
                                        amount=10)
        RecipeIngredient.objects.create(jidlo=vecere9, ingredient=ingredient_objects["Petržel"], amount=5)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere9
        gc.collect()

        vecere10 = Jidlo.objects.create(
            name="Pohanková kaše se zeleninovým salátem",
            type="vecere",
            preparation="Uvař pohanku a podávej s nakrájej mladou kapustu, okurky a smíchej s kukuřicí. "
        "Přidej špetku soli, nasekanou petrželku a majonézu. Promíchej."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/buckwheat-3356778_1280 (1).jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere10.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere10.save()
        print("✅ Přidáno jídlo:", vecere10.name)

        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Pohanka vařená"], amount=180)
        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Kapusta"],
                                        amount=60)
        RecipeIngredient.objects.create(jidlo=vecere10,
                                        ingredient=ingredient_objects["Kukuřice konzervovaná"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Okurka"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Majonéza"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=vecere10, ingredient=ingredient_objects["Petržel"], amount=5)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere10
        gc.collect()

        vecere11  = Jidlo.objects.create(
            name="Pečená ryba se salátem s tuňákem a vejcem",
            type="vecere",
            preparation=(
                "Rybu upečeme v troubě (Treska). "
                "Zatím připravíme salát z vařeného vejce, tuňáka, kyselých okurek, kukuřice, červené cibule. "
                "Dochutíme solí a pepřem, promícháme se zakysanou smetanou."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/26a0b42f-71a4-4d9d-969b-835ecdb3d83c_3F0CfmA.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere11.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere11.save()
        print("✅ Přidáno jídlo:", vecere11.name)
        # Ингредиенты:
        RecipeIngredient.objects.create(jidlo=vecere11, ingredient=ingredient_objects["Treska"],
                                        amount=150)
        RecipeIngredient.objects.create(jidlo=vecere11, ingredient=ingredient_objects["Vejce"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere11,
                                        ingredient=ingredient_objects["Tuňák konzerva ve vlastní šťávě"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere11,
                                        ingredient=ingredient_objects["Okurky sterilované"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere11,
                                        ingredient=ingredient_objects["Kukuřice konzervovaná"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere11, ingredient=ingredient_objects["Červená cibule"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=vecere11, ingredient=ingredient_objects["Smetana"],
                                        amount=20)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere11
        gc.collect()

        vecere12 = Jidlo.objects.create(
            name="Hovězí maso na smetaně s cibulí a rajčatovým protlakem",
            type="vecere",
            preparation=(
                "Nakrájej cibuli a osmahni ji na pánvi. Přidej mouku, rajčatový protlak a smetanu, "
                "promíchej a zalij vodou. Přidej na kousky nakrájené hovězí maso, osol a opepři. "
                "Vař pod pokličkou na mírném ohni do změknutí masa."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/food-1285298_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere12.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere12.save()
        print("✅ Přidáno jídlo:", vecere12.name)

        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Hovězí maso"],
                                        amount=100)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Červená cibule"],
                                        amount=20)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Smetana"],
                                        amount=25)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Mouka"],
                                        amount=10)  # 1 lžíce ≈ 10 g
        RecipeIngredient.objects.create(jidlo=vecere12,
                                        ingredient=ingredient_objects["Rajčatový protlak"],
                                        amount=5)  # 1 čajová lžička ≈ 5 g
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Sůl"], amount=3)
        RecipeIngredient.objects.create(jidlo=vecere12,
                                        ingredient=ingredient_objects["Pepř černý mletý"], amount=1)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere12
        gc.collect()
        vecere12 = Jidlo.objects.create(
            name="Zeleninový salát (k večeři)",
            type="vecere",
            preparation="Nakrájej čerstvé okurky, rajčata a zelí. Promíchej se solí a trochou oleje nebo citronové šťávy."
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/salad-765382_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere12.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere12.save()
        print("✅ Přidáno jídlo:", vecere12.name)

        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Okurka"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Rajčata"], amount=100)
        RecipeIngredient.objects.create(jidlo=vecere12, ingredient=ingredient_objects["Ledový salát"], amount=40)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere12
        gc.collect()


        vecere13 = Jidlo.objects.create(
            name="Kuřecí karbanátek se zeleninovým salátem",
            type="vecere",
            preparation=(
                "Mleté kuřecí maso ochuť solí, pepřem a česnekem. "
                "Vytvoř karbanátky a opeč je na pánvi nebo upeč v troubě. "
                "Zeleninový salát připrav z nakrájených rajčat, okurek a papriky. "
                "Vše zabalte do lavaš. Dochucuj solí, pepřem a citronovou šťávou nebo olivovým olejem."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/kebab-meat-sandwich-7414529_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere13.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere13.save()
        print("✅ Přidáno jídlo:", vecere13.name)

        RecipeIngredient.objects.create(jidlo=vecere13, ingredient=ingredient_objects["Kuřecí maso (mleté)"],
                                        amount=140),
        RecipeIngredient.objects.create(jidlo=vecere13, ingredient=ingredient_objects["Mouka"], amount=20),
        RecipeIngredient.objects.create(jidlo=vecere13, ingredient=ingredient_objects["Lavaš"], amount=20)
        RecipeIngredient.objects.create(jidlo=vecere13, ingredient=ingredient_objects["Rajčata cherry"],  # помидор
                                        amount=70)
        RecipeIngredient.objects.create(jidlo=vecere13, ingredient=ingredient_objects["Okurka"],  # огурец
                                        amount=70)
        RecipeIngredient.objects.create(jidlo=vecere13, ingredient=ingredient_objects["Paprika"],  # перец
                                        amount=60)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere13
        gc.collect()


        vecere14 = Jidlo.objects.create(
            name="Kuřecí karbanátky, viněgret a chléb",
            type="vecere",
            preparation=(
                "Z mletého kuřecího masa připrav karbanátky – ochuť, vytvaruj a opeč na pánvi nebo v troubě. "
                "Viněgret připrav z vařené červené řepy, brambor, mrkve, hrášku a nakládané okurky. "
                "Podávej s krajíčkem chleba."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/venegret-4204908_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere14.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere14.save()
        print("✅ Přidáno jídlo:", vecere14.name)
        # Куриные котлеты
        RecipeIngredient.objects.create(jidlo=vecere14, ingredient=ingredient_objects["Kuřecí maso (mleté)"],
                                        amount=160)

        # Винегрет по отдельным ингредиентам
        RecipeIngredient.objects.create(jidlo=vecere14, ingredient=ingredient_objects["Červená řepa"], amount=60)
        RecipeIngredient.objects.create(jidlo=vecere14, ingredient=ingredient_objects["Brambory"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere14, ingredient=ingredient_objects["Mrkev"], amount=30)
        RecipeIngredient.objects.create(jidlo=vecere14, ingredient=ingredient_objects["Okurky nakládané"], amount=30)
        RecipeIngredient.objects.create(jidlo=vecere14, ingredient=ingredient_objects["Hrášek zelený"], amount=30)

        # Хлеб
        RecipeIngredient.objects.create(jidlo=vecere14, ingredient=ingredient_objects["Chléb žitný"], amount=30)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere14
        gc.collect()

        vecere15 = Jidlo.objects.create(
            name="Bulgur s vařeným kuřecím masem a okurkou",
            type="vecere",
            preparation=(
                "Bulgur uvař podle návodu na obalu. "
                "Kuřecí maso uvař v osolené vodě, poté nakrájej na plátky. "
                "Okurku nakrájej na kolečka nebo kostky. "
                "Podávej společně jako lehkou večeři."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/food-3700930_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere15.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere15.save()
        print("✅ Přidáno jídlo:", vecere15.name)
        # Ингредиенты:
        RecipeIngredient.objects.create(jidlo=vecere15, ingredient=ingredient_objects["Bulgur vařeni"], amount=90)
        RecipeIngredient.objects.create(jidlo=vecere15, ingredient=ingredient_objects["Kuřecí maso (vařené)"],
                                        amount=90)
        RecipeIngredient.objects.create(jidlo=vecere15, ingredient=ingredient_objects["Okurka"], amount=100)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere15
        gc.collect()


        vecere16 = Jidlo.objects.create(
            name="Dušená kuřecí játra, pšeničná kaše a zeleninový salát",
            type="vecere",
            preparation=(
                "Kuřecí játra osmahni s cibulkou, přidej trochu vody nebo vývaru a duste do měkka. "
                "Pšeničnou kaši uvař podle návodu. "
                "Zeleninový salát připrav z čerstvé zeleniny dle chuti – např. rajčata, okurky, paprika. "
                "Dochutit solí, pepřem a citronovou šťávou."
            )
        )
        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/chicken-liver-4141673_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere16.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere16.save()
        print("✅ Přidáno jídlo:", vecere16.name)
        RecipeIngredient.objects.create(jidlo=vecere16, ingredient=ingredient_objects["Kuřecí játra"],
                                        amount=80)
        RecipeIngredient.objects.create(jidlo=vecere16, ingredient=ingredient_objects["Pšenice kaše vařené"],
                                        amount=80)
        RecipeIngredient.objects.create(jidlo=vecere16, ingredient=ingredient_objects["Rajčata cherry"], amount=120)
        RecipeIngredient.objects.create(jidlo=vecere16, ingredient=ingredient_objects["Paprika"], amount=60)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere16
        gc.collect()


        vecere17 = Jidlo.objects.create(
            name="Boršč a havajská směs s bulgurem",
            type="vecere",
            preparation=(
                "Boršč připrav z červené řepy, zelí, brambor, mrkve a rajčatového protlaku, "
                "dochutíme česnekem a kořením. "
                "Havajskou zeleninovou směs (kukuřice, hrášek, paprika, mrkev) osmahni na pánvi "
                "a smíchej s uvařeným bulgurem. Podávej teplé."
            )
        )

        # ✅ Привязываем фото, если оно существует
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/russian-4005732_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                vecere17.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        vecere17.save()
        print("✅ Přidáno jídlo:", vecere17.name)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Červená řepa"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Zelí"], amount=50)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Brambory"], amount=40)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Mrkev"], amount=30)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Rajčatový protlak"], amount=10)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Cibule zelená"], amount=20)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Olej slunečnicový"], amount=5)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Brambory vařené"], amount=150)
        RecipeIngredient.objects.create(jidlo=vecere17, ingredient=ingredient_objects["Mražená zelenina havajská směs"],amount=80)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del vecere17
        gc.collect()


        snack1, created = Jidlo.objects.get_or_create(
            name="Proteinová tyčinka",
            defaults={
                "type": "snack_extra",
                "preparation": "Hotová proteinová tyčinka jako doplněk stravy."
            }
        )
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/premium_photo-1664392029345-eba492b172d8.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snack1.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snack1.save()
        print("✅ Přidáno jídlo:", snack1.name)
        RecipeIngredient.objects.create(jidlo=snack1, ingredient=ingredient_objects["Proteinová tyčinka"], amount=50)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snack1
        gc.collect()




        # 2️⃣ Ořechový mixVlašské ořechy
        snack2, created = Jidlo.objects.get_or_create(
            name="Ořechový mix (malá porce)",
            defaults={
                "type": "snack_extra",
                "preparation": "Malá hrst ořechů jako extra doplněk energie."
            }
        )
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/nuts-3841539_1280.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snack2.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snack2.save()
        print("✅ Přidáno jídlo:", snack2.name)
        RecipeIngredient.objects.create(jidlo=snack2, ingredient=ingredient_objects["Vlašské ořechy"], amount=30)
        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snack2
        gc.collect()



        # 3️⃣ Tvaroh s ovocem
        snack3, created = Jidlo.objects.get_or_create(
            name="Tvaroh s ovocem",
            defaults={
                "type": "snack_extra",
                "preparation": "Smíchej nízkotučný tvaroh s čerstvým ovocem podle chuti."
            }
        )
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/65836568-close-up-view-of-bowl-with-cottage-cheese-banana-and-nuts.jpg")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snack3.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snack3.save()
        print("✅ Přidáno jídlo:", snack3.name)

        RecipeIngredient.objects.create(jidlo=snack3, ingredient=ingredient_objects["Tvaroh"], amount=100),
        RecipeIngredient.objects.create(jidlo=snack3, ingredient=ingredient_objects["Banán"], amount=70)

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snack3
        gc.collect()




        # 4️⃣ Smoothie (banán + mléko)
        snack4, created = Jidlo.objects.get_or_create(
            name="Smoothie (banán + mléko)",
            defaults={
                "type": "snack_extra",
                "preparation": "Rozmixuj banán s mlékem nebo proteinem pro rychlou energii."
            }
        )
        img_path = os.path.join(settings.MEDIA_ROOT, "jidla/premium_photo-1695035006916-bb85c139c70c.avif")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                snack4.obrazek.save(os.path.basename(img_path), ContentFile(buffer.read()), save=False)

        snack4.save()
        print("✅ Přidáno jídlo:", snack4.name)
        RecipeIngredient.objects.create(jidlo=snack4, ingredient=ingredient_objects["Mléko polotučné 1,5 % tuku"],
                                        amount=100),
        RecipeIngredient.objects.create(jidlo=snack4, ingredient=ingredient_objects["Banán"], amount=100)
        RecipeIngredient.objects.create( jidlo=snack4,ingredient=ingredient_objects["Protein"],amount=20
        )

        # Очистка памяти
        if 'img' in locals():
            del img
        if 'buffer' in locals():
            del buffer
        gc.collect()
        del snack4
        gc.collect()



        self.stdout.write(self.style.SUCCESS("✅ Seed выполнен с категориями!"))
        for j in Jidlo.objects.all():
            self.stdout.write(f"{j.name} → {j.get_macros_display()}")
