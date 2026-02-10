from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('jobs/', views.jobs_list, name='jobs_list'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.profile, name='public_profile'),
    path('cvbuilder/', views.cv_builder, name='cv_builder'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),
    path('post-job/', views.post_job, name='post_job'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('work/', views.work, name='work'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('applicants/<int:job_id>/', views.view_applicants, name='view_applicants'),
    path('students/', views.students_list, name='students_list'),
    path('update-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
    path('google-login/', views.google_login_backend, name='google_login_backend'),
    path('add-project/', views.add_project, name='add_project'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
]