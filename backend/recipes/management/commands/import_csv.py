import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from CSV to db'

    def handle(self, *args, **options):
        file = 'ingredients.csv'
        with open(file, encoding='utf-8') as f:
            reader = csv.reader(f)
            total = 0
            for row in reader:
                obj, status = Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1])
                if status:
                    total += 1
                print(file, ': загружено ', total, ' записей.')
        return 'Operation complete!'
