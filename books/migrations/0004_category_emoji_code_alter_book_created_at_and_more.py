# Generated by Django 5.1.2 on 2024-10-22 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_alter_book_options_book_approved_at_book_author_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='emoji_code',
            field=models.CharField(blank=True, help_text='Emojinin HTML kodu yazılmalıdır', max_length=9, null=True, verbose_name='Emoji Kodu'),
        ),
        migrations.AlterField(
            model_name='book',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Yaranma Tarixi'),
        ),
        migrations.AlterField(
            model_name='book',
            name='is_approved',
            field=models.BooleanField(verbose_name='İcazə'),
        ),
    ]