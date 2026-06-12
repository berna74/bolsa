from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from .models import CandidateProfile, JobRole, ProfessionalReference, WorkExperience
from .serializers import (
    CandidateProfileSerializer,
    JobRoleSerializer,
    ProfessionalReferenceSerializer,
    RegisterSerializer,
    UserSerializer,
    WorkExperienceSerializer,
)


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class JobRoleViewSet(viewsets.ModelViewSet):
    queryset = JobRole.objects.all()
    serializer_class = JobRoleSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [IsSuperUser()]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class CandidateProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CandidateProfileSerializer

    def get_object(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return profile


class WorkExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkExperienceSerializer

    def get_queryset(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return WorkExperience.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class ProfessionalReferenceViewSet(viewsets.ModelViewSet):
    serializer_class = ProfessionalReferenceSerializer

    def get_queryset(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return ProfessionalReference.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class HealthCheckView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "contodogusto-bolsa-api"})


class PublicWorkersByRoleView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        profiles = CandidateProfile.objects.select_related("user", "role").prefetch_related("roles").all().order_by("last_name", "first_name")
        grouped = {}

        for profile in profiles:
            worker_roles = list(profile.roles.all()) or ([profile.role] if profile.role_id else [])
            if not worker_roles:
                continue

            full_name = f"{profile.first_name} {profile.last_name}".strip() or profile.user.username
            worker_payload = {
                "id": profile.id,
                "full_name": full_name,
                "personal_photo_url": request.build_absolute_uri(profile.personal_photo.url) if profile.personal_photo else "",
                "phone": profile.phone,
                "email": profile.user.email,
                "city": profile.city,
                "years_experience": profile.years_experience,
                "availability": profile.availability,
                "bio": profile.bio,
                "rubros": [role.name for role in worker_roles],
            }

            for role in worker_roles:
                if role.name not in grouped:
                    grouped[role.name] = []
                grouped[role.name].append(worker_payload)

        response = [{"rubro": rubro, "workers": workers} for rubro, workers in grouped.items()]
        return Response(response)
