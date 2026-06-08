from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField
from django.utils.text import slugify


class Job(models.Model):
    SIZE_1_9 = 'size_1_9'
    SIZE_10_49 = 'size_10_49'
    SIZE_50_99 = 'size_50_99'
    SIZE_100 = 'size_100'
    
    SIZE_CHOICES = (
        (SIZE_1_9, '1-9'),
        (SIZE_10_49, '10-49'),
        (SIZE_50_99, '50-99'),
        (SIZE_100, '100+'),
    )
    
    OPEN = 'open'
    CLOSED = 'closed'
    ARCHIVED = 'archived'
    
    STATUS_CHOICES = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
        (ARCHIVED, 'Archived'),
    )

    REMOTE = 'remote'
    ONSITE = 'onsite'
    HYBRID = 'hybrid'

    WORK_TYPE_CHOICES = (
        (REMOTE, 'Remote'),
        (ONSITE, 'On-site'),
        (HYBRID, 'Hybrid'),
    )
    
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True, db_index=False)
    summary = models.TextField()
    full_description = models.TextField()
    
    company_name = models.CharField(max_length=100)
    company_location = models.CharField(max_length=100, blank=True, null=True)
    company_country = CountryField(blank_label="(select country)", default="NG")
    company_size = models.CharField(max_length=20, choices=SIZE_CHOICES, default=SIZE_1_9)
    
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, default=ONSITE)
    
    created_by = models.ForeignKey(User, related_name='jobs', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['company_country', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.company_name}")
        super().save(*args, **kwargs)

    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.2f} - ${self.salary_max:,.2f}"
        elif self.salary_min:
            return f"From ${self.salary_min:,.2f}"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,.2f}"
        return "Salary not specified"


class JobApplication(models.Model):
    job = models.ForeignKey(Job, related_name='applications', on_delete=models.CASCADE)
    content = models.TextField()
    experience = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='applications', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.job.title