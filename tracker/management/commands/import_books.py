import os
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from tracker.models import Book, Category

class Command(BaseCommand):
    help = 'Import books from an Excel file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(r'c:\Users\Thomas2\rumi_press', 'Books Distribution Expenses.xlsx')

        try:
            
            df = pd.read_excel(file_path)

            # Function to clean 'id' field by removing non-numeric characters
            def clean_id(id_value):
                return ''.join([char for char in str(id_value) if char.isdigit()])

            # Iterate through the rows and create Book objects
            for _, row in df.iterrows():
                # Clean the 'id' field to ensure it contains only digits
                cleaned_id = clean_id(row['id'])

                # Skip this row if the cleaned 'id' is empty or invalid
                if not cleaned_id:
                    print(f"Skipping row with invalid id: {row['id']}")
                    continue

                
                book_id = int(cleaned_id)

                
                category, _ = Category.objects.get_or_create(name=row['category'])

                
                published_date = row['published_date']
                if isinstance(published_date, (pd.Timestamp, datetime)):  # If it's already a datetime-like object
                    published_date = published_date.date()
                elif isinstance(published_date, str):  # If it's a string, parse it
                    published_date = datetime.strptime(published_date, '%Y-%m-%d').date()

                
                book = Book(
                    id=book_id,
                    title=row['title'],
                    subtitle=row['subtitle'],
                    authors=row['authors'],
                    publisher=row['publisher'],
                    published_date=published_date,
                    category=category,
                    distribution_expense=row['distribution_expense']
                )
                book.save()

            self.stdout.write(self.style.SUCCESS('Books imported successfully!'))

        except Exception as e:
            self.stderr.write(f"Error importing books: {e}")
