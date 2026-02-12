from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Job, Category, CV, UserProfile, Application, ContactMessage, Project
from .oauth import verify_google_token
from .utils import extract_text_from_file, parse_cv_data, process_cv_and_update_profile, calculate_match_score, extract_skills
from hitcount.views import HitCountDetailView
from hitcount.utils import get_hitcount_model
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

def index(request):
    jobs = Job.objects.all().order_by('-created_at')[:6]
    categories = Category.objects.all()
    context = {
        'jobs': jobs,
        'categories': categories,
        **get_filter_options()
    }
    return render(request, 'index.html', context)

from django.db.models import Q

def get_filter_options(job_type='', experience='', work_location='', posted=''):
    return {
        'job_types': [
            {'value': 'Remote', 'label': 'Remote', 'is_selected': job_type == 'Remote'},
            {'value': 'Contract', 'label': 'Contract', 'is_selected': job_type == 'Contract'},
            {'value': 'Internship', 'label': 'Internship', 'is_selected': job_type == 'Internship'},
            {'value': 'Part-time', 'label': 'Part-time', 'is_selected': job_type == 'Part-time'},
            {'value': 'Full-time', 'label': 'Full-time', 'is_selected': job_type == 'Full-time'},
        ],
        'experience_levels': [
            {'value': 'entry', 'label': 'Entry Level', 'is_selected': experience == 'entry'},
            {'value': 'intermediate', 'label': 'Intermediate', 'is_selected': experience == 'intermediate'},
            {'value': 'expert', 'label': 'Expert', 'is_selected': experience == 'expert'},
        ],
        'work_locations': [
            {'value': 'remote', 'label': 'Remote', 'is_selected': work_location == 'remote'},
            {'value': 'hybrid', 'label': 'Hybrid', 'is_selected': work_location == 'hybrid'},
            {'value': 'onsite', 'label': 'On-site', 'is_selected': work_location == 'onsite'},
        ],
        'posted_options': [
            {'value': '1', 'label': 'Within 24H', 'is_selected': posted == '1'},
            {'value': '3', 'label': 'Within 3 days', 'is_selected': posted == '3'},
            {'value': '7', 'label': 'Within 7 days', 'is_selected': posted == '7'},
            {'value': '30', 'label': 'Within 30 days', 'is_selected': posted == '30'},
            {'value': 'any', 'label': 'Any time', 'is_selected': posted == 'any' or not posted},
        ]
    }

def jobs_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    category_id = request.GET.get('category', '')
    try:
        selected_category_id = int(category_id) if category_id else None
    except ValueError:
        selected_category_id = None

    job_type = request.GET.get('type', '')
    experience = request.GET.get('experience', '')
    work_location = request.GET.get('work_location', '')
    posted = request.GET.get('posted', 'any')

    jobs = Job.objects.all()
    matching_companies = UserProfile.objects.none()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(company__profile__company_name__icontains=query)
        ).distinct()
        
        matching_companies = UserProfile.objects.filter(
            user_type='company',
            company_name__icontains=query
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if category_id:
        jobs = jobs.filter(category_id=category_id)

    if job_type:
        jobs = jobs.filter(job_type__iexact=job_type)

    if work_location:
        if work_location.lower() == 'remote':
            jobs = jobs.filter(Q(location__icontains='remote') | Q(job_type__icontains='remote'))
        elif work_location.lower() == 'onsite':
            jobs = jobs.filter(~Q(location__icontains='remote'))

    if posted == '1':
        time_threshold = timezone.now() - timedelta(days=1)
        jobs = jobs.filter(created_at__gte=time_threshold)
    elif posted == '3':
        time_threshold = timezone.now() - timedelta(days=3)
        jobs = jobs.filter(created_at__gte=time_threshold)
    elif posted == '7':
        time_threshold = timezone.now() - timedelta(days=7)
        jobs = jobs.filter(created_at__gte=time_threshold)
    elif posted == '30':
        time_threshold = timezone.now() - timedelta(days=30)
        jobs = jobs.filter(created_at__gte=time_threshold)

    jobs = jobs.order_by('-created_at')

    categories = Category.objects.all()
    for cat in categories:
        cat.is_selected = (cat.id == selected_category_id)

    filter_options = get_filter_options(job_type, experience, work_location, posted)

    # Calculate match scores if user is a student
    user_cv = None
    if request.user.is_authenticated:
        try:
            if request.user.profile.user_type == 'student':
                user_cv = CV.objects.filter(user=request.user).first()
        except UserProfile.DoesNotExist:
            pass

    for job in jobs:
        if user_cv and job.skills:
            job.match_score = calculate_match_score(user_cv.skills, job.skills)
        else:
            job.match_score = None

    context = {
        'jobs': jobs,
        'categories': categories,
        **filter_options,
        'query': query,
        'location': location,
        'selected_category': selected_category_id,
        'selected_type': job_type,
        'selected_experience': experience,
        'selected_work_location': work_location,
        'selected_posted': posted,
        'matching_companies': matching_companies,
    }
    return render(request, 'jobs.html', context)

def profile(request, user_id=None):
    if user_id:
        viewed_user = get_object_or_404(User, id=user_id)
        is_own_profile = (viewed_user == request.user)
        
        # Track hit for public profile
        if not is_own_profile:
            profile_obj = viewed_user.profile
            hit_count = get_hitcount_model().objects.get_for_object(profile_obj)
            HitCountDetailView.hit_count(request, hit_count)
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        viewed_user = request.user
        is_own_profile = True

    if request.method == 'POST':
        if not is_own_profile:
            messages.error(request, "You cannot edit someone else's profile.")
            return redirect('public_profile', user_id=user_id)

        # Handle CV Upload for auto-fill
        if 'cv_file' in request.FILES:
            cv_file = request.FILES.get('cv_file')
            success, message = process_cv_and_update_profile(request.user, cv_file)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('profile')

        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        company_name = request.POST.get('company_name')

        user = request.user
        
        # Check if username is already taken by another user
        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' is already taken.")
                return render(request, 'profile.html', {
                    'viewed_user': viewed_user, 
                    'is_own_profile': is_own_profile,
                    'projects': viewed_user.projects.all().order_by('-created_at')
                })
            user.username = username

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.location = location
        if profile.user_type == 'company':
            profile.company_name = company_name
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    projects = viewed_user.projects.all().order_by('-created_at')
    applications = Application.objects.filter(student=viewed_user).order_by('-applied_at')
    
    # Fetch company jobs and total applicants if viewed user is a company
    company_jobs = []
    total_applicants = 0
    if viewed_user.profile.user_type == 'company':
        company_jobs = viewed_user.jobs_posted.all().order_by('-created_at')
        total_applicants = Application.objects.filter(job__in=company_jobs).count()

    # Pre-process skills and experiences for the overview tab
    user_skills = []
    user_soft_skills = []
    user_languages = []
    user_experiences = []
    
    try:
        if viewed_user.cv:
            if viewed_user.cv.skills:
                user_skills = [s.strip() for s in viewed_user.cv.skills.split(',') if s.strip()]
            if viewed_user.cv.soft_skills:
                user_soft_skills = [s.strip() for s in viewed_user.cv.soft_skills.split(',') if s.strip()]
            if viewed_user.cv.languages:
                user_languages = [s.strip() for s in viewed_user.cv.languages.split(',') if s.strip()]
            
            user_experiences = viewed_user.cv.experiences.all().order_by('-start_date')
    except Exception:
        pass

    return render(request, 'profile.html', {
        'viewed_user': viewed_user, 
        'is_own_profile': is_own_profile,
        'projects': projects,
        'applications': applications,
        'company_jobs': company_jobs,
        'total_applicants': total_applicants,
        'user_skills': user_skills[:8], # Limit to top 8 for overview
        'user_soft_skills': user_soft_skills[:8],
        'user_languages': user_languages[:8],
        'user_experiences': user_experiences
    })

@login_required
def cv_builder(request):
    try:
        profile = request.user.profile
        if profile.user_type != 'student':
            messages.error(request, "Only student accounts can access the CV Builder.")
            return redirect('company_dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('profile')
        
    return render(request, 'cvbuilder.html')

@login_required
def student_dashboard(request):
    if request.method == 'POST' and 'cv_file' in request.FILES:
        cv_file = request.FILES.get('cv_file')
        success, message = process_cv_and_update_profile(request.user, cv_file)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect('student_dashboard')

    applications = Application.objects.filter(student=request.user).order_by('-applied_at')
    
    # Get Recommended Jobs
    user_cv = CV.objects.filter(user=request.user).first()
    recommended_jobs = []
    if user_cv and user_cv.skills:
        # Get latest jobs and calculate match score
        all_jobs = Job.objects.all().order_by('-created_at')[:10]
        for job in all_jobs:
            if job.skills:
                score = calculate_match_score(user_cv.skills, job.skills)
                if score >= 30: # Only show jobs with 30%+ match
                    job.match_score = score
                    recommended_jobs.append(job)
        
        # Sort by match score
        recommended_jobs.sort(key=lambda x: x.match_score, reverse=True)
    
    context = {
        'applications': applications,
        'recommended_jobs': recommended_jobs[:3] # Show top 3
    }
    return render(request, 'student-dashboard.html', context)

@login_required
def company_dashboard(request):
    try:
        profile = request.user.profile
        if profile.user_type != 'company':
            messages.error(request, "Only company accounts can access this dashboard.")
            return redirect('student_dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('profile')

    jobs = Job.objects.filter(company=request.user).order_by('-created_at')
    active_jobs_count = jobs.count()
    
    total_applications_count = Application.objects.filter(job__company=request.user).count()
    shortlisted_count = Application.objects.filter(job__company=request.user, status='accepted').count()

    for job in jobs:
        job.applicant_count = job.applications.count()
        
    context = {
        'jobs': jobs,
        'active_jobs_count': active_jobs_count,
        'total_applications_count': total_applications_count,
        'shortlisted_count': shortlisted_count,
    }
    return render(request, 'company-dashboard.html', context)

def apply_job(request, job_id):
    from django.shortcuts import get_object_or_404
    from django.urls import reverse

    if not request.user.is_authenticated:
        messages.info(request, "Please log in to apply for jobs.")
        return redirect(f"{reverse('login')}?next={request.path}")

    job = get_object_or_404(Job, id=job_id)

    # Track hit for job
    hit_count = get_hitcount_model().objects.get_for_object(job)
    HitCountDetailView.hit_count(request, hit_count)

    try:
        profile = request.user.profile
        if profile.user_type != 'student':
            messages.error(request, "Only students can apply for jobs.")
            return redirect('jobs_list')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user, user_type='student')

    if Application.objects.filter(job=job, student=request.user).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('student_dashboard')

    try:
        cv = request.user.cv
        if not cv.resume_file and not cv.summary:
            messages.info(request, "Please complete your CV before applying.")
            return redirect('student_dashboard')
    except CV.DoesNotExist:
        messages.info(request, "Please create or upload your CV before applying.")
        return redirect('student_dashboard')

    if request.method == 'POST':
        cv_source = request.POST.get('cv_source')
        resume_file = None

        if cv_source == 'existing':
            try:
                cv = request.user.cv
                if cv.resume_file:
                    resume_file = cv.resume_file
                else:
                    messages.error(request, "You don't have a saved CV. Please upload one.")
                    return render(request, 'apply.html', {'job': job})
            except CV.DoesNotExist:
                messages.error(request, "You don't have a saved CV. Please upload one.")
                return render(request, 'apply.html', {'job': job})

        elif cv_source == 'upload':
            if 'resume' in request.FILES:
                resume_file = request.FILES['resume']
                if request.POST.get('save_as_default') == 'on':
                    cv, created = CV.objects.get_or_create(user=request.user)
                    cv.resume_file = resume_file
                    cv.save()
            else:
                messages.error(request, "Please upload a CV file.")
                return render(request, 'apply.html', {'job': job})

        if resume_file:
            Application.objects.create(
                job=job,
                student=request.user,
                resume_file=resume_file
            )
            messages.success(request, f"Successfully applied for {job.title}!")
            return redirect('student_dashboard')
        else:
            messages.error(request, "CV is required for application.")

    return render(request, 'apply.html', {'job': job})

@login_required
def view_applicants(request, job_id):
    job = Job.objects.get(id=job_id)
    if job.company != request.user:
        messages.error(request, "You do not have permission to view applicants for this job.")
        return redirect('company_dashboard')

    applicants = job.applications.all().order_by('-applied_at')
    for app in applicants:
        app.is_pending = app.status == 'pending'
        app.is_reviewed = app.status == 'reviewed'
        app.is_accepted = app.status == 'accepted'
        app.is_rejected = app.status == 'rejected'
        
        # Calculate match score for applicant
        try:
            student_cv = CV.objects.get(user=app.student)
            if student_cv.skills and job.skills:
                app.match_score = calculate_match_score(student_cv.skills, job.skills)
            else:
                app.match_score = 0
        except CV.DoesNotExist:
            app.match_score = 0

    return render(request, 'applicants.html', {'job': job, 'applicants': applicants})

@login_required
def update_application_status(request, application_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        application = Application.objects.get(id=application_id)

        if application.job.company != request.user:
            messages.error(request, "Unauthorized action.")
            return redirect('company_dashboard')

        application.status = status
        application.save()
        messages.success(request, f"Application status updated to {status}.")
        return redirect('view_applicants', job_id=application.job.id)
    return redirect('company_dashboard')

def post_job(request):

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        job_type = request.POST.get('job_type')
        location = request.POST.get('location')
        salary_range = request.POST.get('salary_range')
        description = request.POST.get('description')

        if title and category_id and job_type and location and description:
            try:
                category = Category.objects.get(id=category_id)
                Job.objects.create(
                    company=request.user,
                    category=category,
                    title=title,
                    job_type=job_type,
                    location=location,
                    salary_range=salary_range,
                    description=description,
                    skills=", ".join(extract_skills(description))
                )
                messages.success(request, f"Job '{title}' posted successfully!")
                return redirect('company_dashboard')
            except Category.DoesNotExist:
                messages.error(request, "Invalid category selected.")
        else:
            messages.error(request, "Please fill in all required fields.")

    categories = Category.objects.all()
    return render(request, 'postjob.html', {'categories': categories})

def students_list(request):
    keyword = request.GET.get('keyword', '')
    location = request.GET.get('location', '')
    category_id = request.GET.get('category', '')
    try:
        selected_category_id = int(category_id) if category_id else None
    except ValueError:
        selected_category_id = None

    experience = request.GET.get('experience', '')
    rate = request.GET.get('rate', '')
    availability = request.GET.get('availability', '')

    students = UserProfile.objects.filter(user_type='student')

    if keyword:
        students = students.filter(
            Q(user__username__icontains=keyword) |
            Q(user__first_name__icontains=keyword) |
            Q(user__last_name__icontains=keyword) |
            Q(user__cv__title__icontains=keyword) |
            Q(user__cv__summary__icontains=keyword) |
            Q(user__cv__skills__icontains=keyword)
        ).distinct()

    if location:
        students = students.filter(location__icontains=location)

    if selected_category_id:
        try:
            category = Category.objects.get(id=selected_category_id)
            students = students.filter(
                Q(user__cv__title__icontains=category.name) |
                Q(user__cv__summary__icontains=category.name) |
                Q(user__cv__skills__icontains=category.name)
            ).distinct()
        except Category.DoesNotExist:
            pass

    categories = Category.objects.all()
    for cat in categories:
        cat.is_selected = (cat.id == selected_category_id)

    experience_levels = [
        {'value': 'entry', 'label': 'Entry Level', 'is_selected': experience == 'entry'},
        {'value': 'intermediate', 'label': 'Intermediate', 'is_selected': experience == 'intermediate'},
        {'value': 'expert', 'label': 'Expert', 'is_selected': experience == 'expert'},
    ]

    context = {
        'students': students,
        'categories': categories,
        'experience_levels': experience_levels,
        'keyword': keyword,
        'location': location,
        'selected_category': selected_category_id,
        'selected_experience': experience,
        'selected_rate': rate,
        'selected_availability': availability,
    }
    return render(request, 'students.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, 'contact.html')

def work(request):
    categories = Category.objects.all()
    return render(request, 'work.html', {'categories': categories})

def signup_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url == 'None':
        next_url = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')
        company_name = request.POST.get('company_name')
        website = request.POST.get('website')
        location = request.POST.get('location')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'signup.html', {'next': next_url})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'signup.html', {'next': next_url})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(
            user=user, 
            user_type=user_type, 
            company_name=company_name,
            website=website,
            location=location
        )

        login(request, user)

        if next_url:
            return redirect(next_url)

        if user_type == 'company':
            return redirect('company_dashboard')
        return redirect('student_dashboard')

    return render(request, 'signup.html', {'next': next_url})

def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url == 'None':
        next_url = None
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            if next_url:
                return redirect(next_url)
                
            try:
                profile = user.profile
                if profile.user_type == 'company':
                    return redirect('company_dashboard')
                return redirect('student_dashboard')
            except UserProfile.DoesNotExist:
                return redirect('index')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'login.html', {'next': next_url})

    return render(request, 'login.html', {'next': next_url})

def logout_view(request):
    logout(request)
    return redirect('index')

@csrf_exempt
def google_login_backend(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('credential')

            if not token:
                return JsonResponse({'status': 'error', 'message': 'No token provided'}, status=400)

            user_data = verify_google_token(token)

            if user_data:
                email = user_data.get('email')
                name = user_data.get('name', email.split('@')[0])
                user_type = data.get('user_type', 'student')

                user = User.objects.filter(email=email).first()

                if not user:

                    username = email.split('@')[0]

                    original_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{original_username}{counter}"
                        counter += 1

                    user = User.objects.create_user(username=username, email=email)

                    UserProfile.objects.create(user=user, user_type=user_type)

                login(request, user)

                try:
                    profile = user.profile
                    redirect_url = '/company-dashboard/' if profile.user_type == 'company' else '/student-dashboard/'
                except UserProfile.DoesNotExist:
                    redirect_url = '/student-dashboard/'

                return JsonResponse({
                    'status': 'success',
                    'redirect_url': redirect_url,
                    'user_name': name
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

@login_required
def add_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        github_link = request.POST.get('github_link')
        live_link = request.POST.get('live_link')

        if title and description:
            Project.objects.create(
                user=request.user,
                title=title,
                description=description,
                github_link=github_link,
                live_link=live_link
            )
            messages.success(request, "Project added successfully!")
        else:
            messages.error(request, "Title and description are required.")
    
    return redirect('profile')

@login_required
@csrf_exempt
def save_cv_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            personal = data.get('personal', {})
            skills = data.get('skills', {})
            
            user = request.user
            
            # Update User fields
            if personal.get('firstName'):
                user.first_name = personal.get('firstName')
            if personal.get('lastName'):
                user.last_name = personal.get('lastName')
            user.save()
            
            # Update UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if personal.get('phone'):
                profile.phone = personal.get('phone')
            if personal.get('location'):
                profile.location = personal.get('location')
            if personal.get('website'):
                profile.website = personal.get('website')
            profile.save()
            
            # Update CV
            cv, _ = CV.objects.get_or_create(user=user)
            if personal.get('title'):
                cv.title = personal.get('title')
            if personal.get('summary'):
                cv.summary = personal.get('summary')
            if personal.get('linkedin'):
                cv.linkedin = personal.get('linkedin')
            if personal.get('github'):
                cv.github = personal.get('github')
                
            # Update Skill categories separately
            if skills.get('technical'):
                cv.skills = ", ".join(sorted(list(set(skills.get('technical')))))
            if skills.get('soft'):
                cv.soft_skills = ", ".join(sorted(list(set(skills.get('soft')))))
            if skills.get('languages'):
                cv.languages = ", ".join(sorted(list(set(skills.get('languages')))))
            
            cv.save()
            
            # Handle Experience
            experiences = data.get('experiences', [])
            from datetime import datetime
            
            if experiences:
                cv.experiences.all().delete()
                for exp in experiences:
                    from .models import Experience
                    
                    start_date = exp.get('startDate')
                    end_date = exp.get('endDate')
                    
                    try:
                        parsed_start = None
                        if start_date:
                            parsed_start = datetime.strptime(start_date, '%Y-%m').date() if len(start_date) == 7 else datetime.strptime(start_date, '%Y-%m-%d').date()
                        
                        parsed_end = None
                        if end_date:
                            parsed_end = datetime.strptime(end_date, '%Y-%m').date() if len(end_date) == 7 else datetime.strptime(end_date, '%Y-%m-%d').date()
                            
                        Experience.objects.create(
                            cv=cv,
                            company=exp.get('company'),
                            position=exp.get('position'),
                            start_date=parsed_start,
                            end_date=parsed_end,
                            description=exp.get('description', '')
                        )
                    except Exception as e:
                        print(f"Error saving experience: {e}")

            # Handle Education
            education_data = data.get('education', [])
            if education_data:
                cv.education.all().delete()
                for edu in education_data:
                    from .models import Education
                    
                    edu_start_date = edu.get('startDate')
                    edu_end_date = edu.get('endDate')
                    
                    try:
                        parsed_edu_start = None
                        if edu_start_date:
                            parsed_edu_start = datetime.strptime(edu_start_date, '%Y-%m').date() if len(edu_start_date) == 7 else datetime.strptime(edu_start_date, '%Y-%m-%d').date()
                        
                        parsed_edu_end = None
                        if edu_end_date:
                            parsed_edu_end = datetime.strptime(edu_end_date, '%Y-%m').date() if len(edu_end_date) == 7 else datetime.strptime(edu_end_date, '%Y-%m-%d').date()
                            
                        Education.objects.create(
                            cv=cv,
                            institution=edu.get('institution'),
                            degree=edu.get('degree'),
                            field_of_study=edu.get('field'),
                            start_date=parsed_edu_start,
                            end_date=parsed_edu_end,
                            gpa=edu.get('gpa'),
                            location=edu.get('location')
                        )
                    except Exception as e:
                        print(f"Error saving education: {e}")

            # Handle Certifications
            certs_data = data.get('certifications', [])
            if certs_data:
                cv.certifications.all().delete()
                for cert in certs_data:
                    from .models import Certification
                    
                    issue_date = cert.get('issueDate')
                    exp_date = cert.get('expiryDate')
                    
                    try:
                        parsed_issue = None
                        if issue_date:
                            parsed_issue = datetime.strptime(issue_date, '%Y-%m').date() if len(issue_date) == 7 else datetime.strptime(issue_date, '%Y-%m-%d').date()
                        
                        parsed_exp = None
                        if exp_date:
                            parsed_exp = datetime.strptime(exp_date, '%Y-%m').date() if len(exp_date) == 7 else datetime.strptime(exp_date, '%Y-%m-%d').date()
                            
                        Certification.objects.create(
                            cv=cv,
                            name=cert.get('name'),
                            issuing_organization=cert.get('organization'),
                            issue_date=parsed_issue,
                            expiration_date=parsed_exp,
                            credential_id=cert.get('credentialId')
                        )
                    except Exception as e:
                        print(f"Error saving certification: {e}")

            # Handle Projects
            projects_data = data.get('projects', [])
            if projects_data:
                user.projects.all().delete()
                for proj in projects_data:
                    from .models import Project
                    Project.objects.create(
                        user=user,
                        title=proj.get('name'),
                        description=proj.get('description', ''),
                        github_link=proj.get('url') if 'github.com' in (proj.get('url') or '') else None,
                        live_link=proj.get('url') if 'github.com' not in (proj.get('url') or '') else None
                    )
            
            return JsonResponse({'status': 'success', 'message': 'CV data saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

@login_required
def delete_project(request, project_id):
    from django.shortcuts import get_object_or_404
    project = get_object_or_404(Project, id=project_id, user=request.user)
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect('profile')

def link_callback(uri, rel):
    """
    Convert HTML images to specific system paths for xhtml2pdf
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL       # Typically /media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    # make sure that file exists
    if not os.path.isfile(path):
        return uri
    return path

@login_required
def download_cv_pdf(request):
    try:
        cv = request.user.cv
    except CV.DoesNotExist:
        messages.error(request, "Please create your CV first.")
        return redirect('student_dashboard')

    experiences = cv.experiences.all().order_by('-start_date')
    education = cv.education.all().order_by('-start_date')
    certifications = cv.certifications.all().order_by('-issue_date')
    
    context = {
        'user': request.user,
        'cv': cv,
        'experiences': experiences,
        'education': education,
        'certifications': certifications,
        'skills_tech': cv.skills,
        'skills_soft': cv.soft_skills,
        'languages': cv.languages,
    }

    # Create a Django response object, and specify content_type as pdf
    filename = f"{request.user.first_name or 'My'}_{request.user.last_name or 'CV'}_CV.pdf"
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # find the template and render it.
    template = get_template('cv_pdf.html')
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been permanently deleted.")
        return JsonResponse({'status': 'success', 'message': 'Account deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
