from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from hitcount.models import HitCountMixin, HitCount

class UserProfile(models.Model, HitCountMixin):
    USER_TYPES = (
        ('student', 'Student'),
        ('company', 'Company'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation'
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class CV(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cv')
    title = models.CharField(max_length=100)
    summary = models.TextField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated technical skills")
    soft_skills = models.TextField(blank=True, null=True, help_text="Comma-separated soft skills")
    languages = models.TextField(blank=True, null=True, help_text="Comma-separated languages")

    def __str__(self):
        return f"CV of {self.user.username}"

class Experience(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.position} at {self.company}"

class Education(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    gpa = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Certification(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} from {self.issuing_organization}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Boxicon name, e.g., bx-code-alt")

    def __str__(self):
        return self.name

class Job(models.Model, HitCountMixin):
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='jobs')
    title = models.CharField(max_length=200)
    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation'
    )
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=50)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills required for this job")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    resume_file = models.FileField(upload_to='applications/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.job.title}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    github_link = models.URLField(blank=True, null=True)
    live_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"