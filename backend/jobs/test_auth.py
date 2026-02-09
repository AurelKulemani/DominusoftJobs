from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.student_dashboard_url = reverse('student_dashboard')
        self.company_dashboard_url = reverse('company_dashboard')

    def test_student_signup_redirect(self):
        response = self.client.post(self.signup_url, {
            'username': 'teststudent',
            'email': 'student@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'user_type': 'student'
        })
        self.assertRedirects(response, self.student_dashboard_url)
        self.assertTrue(User.objects.filter(username='teststudent').exists())
        user = User.objects.get(username='teststudent')
        self.assertEqual(user.profile.user_type, 'student')

    def test_company_signup_redirect(self):
        response = self.client.post(self.signup_url, {
            'username': 'testcompany',
            'email': 'company@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'user_type': 'company',
            'company_name': 'Test Company'
        })
        self.assertRedirects(response, self.company_dashboard_url)
        self.assertTrue(User.objects.filter(username='testcompany').exists())
        user = User.objects.get(username='testcompany')
        self.assertEqual(user.profile.user_type, 'company')

    def test_login_student_redirect(self):
        user = User.objects.create_user(username='stud', password='password123')
        UserProfile.objects.create(user=user, user_type='student')

        response = self.client.post(self.login_url, {
            'username': 'stud',
            'password': 'password123'
        })
        self.assertRedirects(response, self.student_dashboard_url)

    def test_login_company_redirect(self):
        user = User.objects.create_user(username='comp', password='password123')
        UserProfile.objects.create(user=user, user_type='company')

        response = self.client.post(self.login_url, {
            'username': 'comp',
            'password': 'password123'
        })
        self.assertRedirects(response, self.company_dashboard_url)