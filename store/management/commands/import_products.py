import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File
from store.models import Products, Category

class Command(BaseCommand):
    help = 'Import products from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category_name = row['Category']
                category, created = Category.objects.get_or_create(name=category_name)
                product = Products(
                    name=row['Product_title'],
                    description=row['Product_description'],
                    price=float(row['Price'][1:]),  # Assuming price starts with a currency symbol
                    category=category,
                )

                # Construct the full path to the image file within the product_photos folder
                image_file_path = os.path.join(
                    settings.MEDIA_ROOT, row['Product_photo_filename'])
                print(image_file_path)
                if os.path.exists(image_file_path):
                    with open(image_file_path, 'rb') as image_file:
                        product.image.save(
                            row['Product_photo_filename'], File(image_file), save=False)

                product.save()

        self.stdout.write(self.style.SUCCESS('Products imported successfully!'))
