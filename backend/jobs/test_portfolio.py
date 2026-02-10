from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Project
from django.urls import reverse

class PortfolioShowcaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='teststudent', password='password123')
        self.client.login(username='teststudent', password='password123')

    def test_add_project(self):
        url = reverse('add_project')
        data = {
            'title': 'Test Project',
            'description': 'Test Description',
            'github_link': 'https://github.com/test',
            'live_link': 'https://live.test'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirect to profile
        self.assertEqual(Project.objects.count(), 1)
        project = Project.objects.first()
        self.assertEqual(project.title, 'Test Project')
        self.assertEqual(project.user, self.user)

    def test_delete_project(self):
        project = Project.objects.create(
            user=self.user,
            title='Delete Me',
            description='Delete Description'
        )
        url = reverse('delete_project', args=[project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 0)

    def test_unauthorized_delete(self):
        other_user = User.objects.create_user(username='other', password='password')
        project = Project.objects.create(
            user=other_user,
            title='Other Project',
            description='Other Description'
        )
        url = reverse('delete_project', args=[project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404) # Should return 404 since it checks user=request.user
        self.assertEqual(Project.objects.count(), 1)
