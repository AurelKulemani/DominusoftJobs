from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Job, Category, CV, UserProfile, Application, ContactMessage
from .oauth import verify_google_token
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

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

    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query))

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
    }
    return render(request, 'jobs.html', context)

@login_required
@login_required
def profile(request):
    if request.method == 'POST':
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
                return render(request, 'profile.html')
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

    return render(request, 'profile.html')

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
        cv, created = CV.objects.get_or_create(user=request.user)
        cv.resume_file = cv_file
        if not cv.title:
            cv.title = f"CV - {request.user.username}"
        cv.save()
        messages.success(request, "CV uploaded successfully!")
        return redirect('student_dashboard')

    applications = Application.objects.filter(student=request.user).order_by('-applied_at')
    return render(request, 'student-dashboard.html', {'applications': applications})

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
        messages.info(request, "Please create an account to apply for jobs.")
        return redirect(f"{reverse('signup')}?next={request.path}")

    job = get_object_or_404(Job, id=job_id)

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
                    description=description
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
            Q(user__cv__summary__icontains=keyword)
        ).distinct()

    if location:
        students = students.filter(location__icontains=location)

    if selected_category_id:
        try:
            category = Category.objects.get(id=selected_category_id)
            students = students.filter(
                Q(user__cv__title__icontains=category.name) |
                Q(user__cv__summary__icontains=category.name)
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
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')
        company_name = request.POST.get('company_name')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'signup.html', {'next': next_url})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'signup.html', {'next': next_url})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, user_type=user_type, company_name=company_name)

        login(request, user)

        if next_url:
            return redirect(next_url)

        if user_type == 'company':
            return redirect('company_dashboard')
        return redirect('student_dashboard')

    return render(request, 'signup.html', {'next': next_url})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            try:
                profile = user.profile
                if profile.user_type == 'company':
                    return redirect('company_dashboard')
                return redirect('student_dashboard')
            except UserProfile.DoesNotExist:
                return redirect('index')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'login.html')

    return render(request, 'login.html')

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