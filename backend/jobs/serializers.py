from django.contrib.auth.models import User
from rest_framework import serializers

from .models import CandidateProfile, JobRole, ProfessionalReference, WorkExperience


class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = ("id", "name")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        CandidateProfile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        exclude = ("profile",)


class ProfessionalReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalReference
        exclude = ("profile",)


class CandidateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    experiences = WorkExperienceSerializer(many=True, read_only=True)
    references = ProfessionalReferenceSerializer(many=True, read_only=True)
    personal_photo = serializers.ImageField(required=False, allow_null=True)
    personal_photo_url = serializers.SerializerMethodField()
    role = serializers.PrimaryKeyRelatedField(queryset=JobRole.objects.all(), required=False, allow_null=True)
    roles = serializers.PrimaryKeyRelatedField(queryset=JobRole.objects.all(), many=True, required=False)
    role_name = serializers.CharField(source="role.name", read_only=True)
    role_names = serializers.SerializerMethodField()

    def validate(self, attrs):
        role = attrs.get("role")
        roles = attrs.get("roles", serializers.empty)
        current_roles = list(self.instance.roles.all()) if self.instance is not None else []

        if role is None and self.instance and self.instance.role_id:
            role = self.instance.role

        if roles is not serializers.empty and not roles:
            raise serializers.ValidationError({"roles": "Debes seleccionar al menos un rubro."})

        if role is None and roles is serializers.empty and not current_roles:
            raise serializers.ValidationError({"role": "Debes seleccionar un rubro."})

        if role is None and roles is not serializers.empty and roles:
            attrs["role"] = roles[0]

        if role is not None and roles is serializers.empty:
            attrs["roles"] = [role]

        return attrs

    def get_personal_photo_url(self, obj):
        if not obj.personal_photo:
            return ""

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.personal_photo.url)
        return obj.personal_photo.url

    def get_role_names(self, obj):
        roles = [role.name for role in obj.roles.all()]
        if roles:
            return roles
        return [obj.role.name] if obj.role_id else []

    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        profile = super().create(validated_data)
        selected_roles = roles or ([validated_data["role"]] if validated_data.get("role") else [])
        if selected_roles:
            profile.roles.set(selected_roles)
        return profile

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", None)
        profile = super().update(instance, validated_data)
        if roles is not None:
            profile.roles.set(roles)
        elif validated_data.get("role") is not None:
            profile.roles.set([validated_data["role"]])
        return profile

    class Meta:
        model = CandidateProfile
        fields = (
            "id",
            "user",
            "first_name",
            "last_name",
            "personal_photo",
            "personal_photo_url",
            "phone",
            "city",
            "role",
            "role_name",
            "roles",
            "role_names",
            "years_experience",
            "availability",
            "bio",
            "experiences",
            "references",
        )
