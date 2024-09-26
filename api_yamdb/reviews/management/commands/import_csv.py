import csv

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from reviews.models import (
    Category,
    Genre,
    Title,
    GenreTitle,
    User,
    Review,
    Comment,
)

# Словарь соответствий моделей и названий файлов CSV
MODEL_FILES = {
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    GenreTitle: 'genre_title.csv',
    User: 'users.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    help = 'Загрузка данных из CSV файлов в базу данных.'

    def handle(self, *args, **options):
        for model, csv_file in MODEL_FILES.items():
            self.stdout.write(
                self.style.SUCCESS(f'Загрузка данных из {csv_file}...')
            )
            with open(
                f'static/data/{csv_file}', 'r', encoding='utf-8'
            ) as file:
                reader = csv.DictReader(file)

                for row in reader:
                    data = row.copy()  # Создаем копию строки для модификации

                    # Обработка внешних ключей
                    for field_name in data.copy():
                        if field_name.endswith('_id'):
                            try:
                                related_model_name = field_name[
                                    :-3
                                ].capitalize()
                                related_model = globals()[related_model_name]
                                related_instance = related_model.objects.get(
                                    id=data[field_name]
                                )
                                data[field_name[:-3]] = related_instance
                                del data[field_name]
                            except KeyError:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'Ошибка целостности: Модель для '
                                        f'поля {field_name} не найдена, '
                                        f'строка {row} пропущена.'
                                    )
                                )
                                continue
                            except related_model.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'Ошибка целостности: '
                                        f'{related_model_name} '
                                        f'с id={data[field_name]} не найден, '
                                        f'строка {row} пропущена.'
                                    )
                                )
                                continue

                    try:
                        model.objects.create(**data)
                    except IntegrityError:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Запись {row} пропущена (нарушение '
                                f'ограничения целостности).'
                            )
                        )
            self.stdout.write(
                self.style.SUCCESS(f'Данные из {csv_file} успешно загружены.')
            )
