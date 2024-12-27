from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=55, verbose_name='Kateqoriya Adı')
    emoji_code = models.CharField(max_length=9, blank=True, null=True, help_text='Emojinin HTML kodu yazılmalıdır və sadəcə paret kateqoriyalarda əlavə edilməlidir. (emojiguide.org)', verbose_name='Emoji Kodu')
    parent = models.ForeignKey('self', verbose_name='Üst Kateqoriya', on_delete=models.CASCADE, blank=True, null=True, related_name='childrens')
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Kateqoriya'
        verbose_name_plural = 'Kateqoriyalar'

        ordering = ['name']

    def __str__(self) -> str:
        # If the parent field is selected, return the full category path (parent > child).
        if self.parent:
            return f'{self.parent} > {self.name}'
        return self.name
    
    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

class Publishing(models.Model):
    name = models.CharField(max_length=55, verbose_name='Nəşriyyat Adı')
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Nəşriyyat'
        verbose_name_plural = 'Nəşriyyat'

        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super(Publishing, self).save(*args, **kwargs)

class Language(models.Model):
    order = models.PositiveIntegerField(unique=True, verbose_name='Sıra')
    name = models.CharField(max_length=55, verbose_name='Dil Adı')
    code = models.CharField(max_length=2, verbose_name='Dil Kodu')

    class Meta:
        verbose_name = 'Dil'
        verbose_name_plural = 'Dillər'
        ordering = ['order']

    def __str__(self) -> str:
        return self.name

class City(models.Model):
    name = models.CharField(max_length=55, verbose_name='Şəhər Adı')
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Şəhər'
        verbose_name_plural = 'Şəhərlər'
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super(City, self).save(*args, **kwargs)

class Condition(models.Model):
    order = models.PositiveIntegerField(unique=True, verbose_name='Sıra')
    name = models.CharField(max_length=55, verbose_name='Kitab Vəziyyəti')
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Vəziyyət'
        verbose_name_plural = 'Vəziyyət'
        ordering = ['order']
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super(Condition, self).save(*args, **kwargs)

class Book(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    name = models.CharField(max_length=255, verbose_name='Kitab Adı')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books', verbose_name='Kateqoriya')
    sub_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='sub_books', verbose_name='Alt Kateqoriya')
    author = models.CharField(max_length=150, blank=True, null=True, verbose_name='Yazar')
    publishing = models.ForeignKey(Publishing, on_delete=models.SET_NULL, blank=True, null=True, related_name='books', verbose_name='Nəşriyyat')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name='books', verbose_name='Kitab Dili')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='books', verbose_name='Şəhər')
    condition = models.ForeignKey(Condition, on_delete=models.SET_NULL, null=True, related_name='books', verbose_name='Kitab Vəziyyəti')
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Qiymət')
    description = models.TextField(verbose_name='Açıqlama')
    cover_photo = models.ImageField(upload_to='book-images/%Y/%m/%d')

    slug = models.SlugField(unique=True, blank=True, null=True)
    is_approved = models.BooleanField(default=False, verbose_name='İcazə')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='Yaranma Tarixi')
    approved_at = models.DateTimeField(blank=True, null=True, editable=False)

    class Meta:
        verbose_name = 'Kitab'
        verbose_name_plural = 'Kitablar'

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        # If approved, update the approval time
        if self.is_approved:
            self.approved_at = timezone.now()

        # If no slug exists, generate a unique slug
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            queryset = self.__class__.objects.filter(slug=self.slug)
            counter = 1

            # If the slug already exists, append a number to make it unique
            while queryset.exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                queryset = self.__class__.objects.filter(slug=self.slug)

        super(Book, self).save(*args, **kwargs)

class Image(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='book-images/%Y/%m/%d')

    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return self.book.name