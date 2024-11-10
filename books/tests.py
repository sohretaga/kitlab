from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Book, Category, Publishing, Language, City, Condition
from .forms import SaleBookForm

# Create your tests here.

class SaleBookFormTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.category = Category.objects.create(name='Fiction')
        cls.sub_category = Category.objects.create(name='Mystery')
        cls.publishing = Publishing.objects.create(name='Test Publishing')
        cls.language = Language.objects.create(name='English', order=1)
        cls.city = City.objects.create(name='New York')
        cls.condition = Condition.objects.create(name='New', order=1)
    
    def test_sale_book_form_valid_data(self):
        #  Valid data to populate the form
        form_data = {
            'name': 'Test Book',
            'category': self.category.id,
            'sub_category': self.sub_category.id,
            'author': 'Test Author',
            'publishing': self.publishing.id,
            'language': self.language.id,
            'city': self.city.id,
            'condition': self.condition.id,
            'price': '29.99',
            'description': 'A test book description.',
        }

        form = SaleBookForm(data=form_data)
        self.assertTrue(form.is_valid())
        # Save form instance and check if it doesn't raise errors
        book = form.save(commit=False)
        book.seller = self.user  # Simulating that seller will be added in form_valid
        book.save()
    
        # Validate saved instance
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(book.name, 'Test Book')
        self.assertEqual(book.seller, self.user)
        self.assertEqual(book.price, 29.99)

    def test_sale_book_form_missing_required_field(self):
        # Missing the 'name' field
        form_data = {
            'category': self.category.id,
            'sub_category': self.sub_category.id,
            'author': 'Test Author',
            'publishing': self.publishing.id,
            'language': self.language.id,
            'city': self.city.id,
            'condition': self.condition.id,
            'price': '29.99',
            'description': 'A test book description.',
        }
        
        form = SaleBookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_sale_book_view(self):
        # Login the user
        self.client.login(username='testuser', password='password')

        # Form data for view test
        form_data = {
            'name': 'View Test Book',
            'category': self.category.id,
            'sub_category': self.sub_category.id,
            'author': 'View Author',
            'publishing': self.publishing.id,
            'language': self.language.id,
            'city': self.city.id,
            'condition': self.condition.id,
            'price': '39.99',
            'description': 'Testing sale book view.',
        }

        # Submit a POST request to the SaleBookView
        response = self.client.post(reverse('sale'), data=form_data)

        # Check that the view redirects to the success URL
        self.assertRedirects(response, reverse('index'))
        
        # Confirm that the book was created and associated with the user
        book = Book.objects.get(name='View Test Book')
        self.assertEqual(book.seller, self.user)
        self.assertEqual(book.price, 39.99)