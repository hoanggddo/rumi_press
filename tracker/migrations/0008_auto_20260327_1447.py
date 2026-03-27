from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0006_alter_book_authors_alter_book_distribution_expense_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='book',
            unique_together=set(),  # remove unique constraint
        ),
    ]