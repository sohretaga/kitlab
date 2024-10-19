# Generated by Django 5.1.2 on 2024-10-19 22:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, verbose_name='Şəhər Adı')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
            options={
                'verbose_name': 'Şəhər',
                'verbose_name_plural': 'Şəhərlər',
            },
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(verbose_name='Sıra')),
                ('name', models.CharField(max_length=55, verbose_name='Kitab Vəziyyəti')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
            options={
                'verbose_name': 'Vəziyyət',
                'verbose_name_plural': 'Vəziyyət',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(verbose_name='Sıra')),
                ('name', models.CharField(max_length=55, verbose_name='Dil Adı')),
                ('code', models.CharField(max_length=2, verbose_name='Dil Kodu')),
            ],
            options={
                'verbose_name': 'Dil',
                'verbose_name_plural': 'Dillər',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Publishing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, verbose_name='Nəşriyyat Adı')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
            options={
                'verbose_name': 'Nəşriyyat',
                'verbose_name_plural': 'Nəşriyyat',
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'Kateqoriya', 'verbose_name_plural': 'Kateqoriyalar'},
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=55, verbose_name='Kateqoriya Adı'),
        ),
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='childrens', to='books.category', verbose_name='Alt Kateqoriya'),
        ),
    ]
