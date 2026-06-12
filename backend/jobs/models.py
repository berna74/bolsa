from django.conf import settings
from django.db import models


class JobRole(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile")
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    personal_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=120, blank=True)
    role = models.ForeignKey(JobRole, on_delete=models.PROTECT, null=True, blank=True, related_name="profiles")
    roles = models.ManyToManyField(JobRole, blank=True, related_name="candidate_profiles")
    years_experience = models.PositiveIntegerField(default=0)
    availability = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class WorkExperience(models.Model):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="experiences")
    company_name = models.CharField(max_length=160)
    role = models.CharField(max_length=140)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.role} en {self.company_name}"


class ProfessionalReference(models.Model):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="references")
    full_name = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True)
    relation = models.CharField(max_length=120)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name
