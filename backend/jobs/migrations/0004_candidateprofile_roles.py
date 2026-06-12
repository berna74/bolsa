from django.db import migrations, models


def copy_primary_role_to_roles(apps, schema_editor):
    CandidateProfile = apps.get_model("jobs", "CandidateProfile")

    for profile in CandidateProfile.objects.select_related("role").all().iterator():
        if profile.role_id:
            profile.roles.add(profile.role_id)


def copy_roles_to_primary_role(apps, schema_editor):
    CandidateProfile = apps.get_model("jobs", "CandidateProfile")

    for profile in CandidateProfile.objects.prefetch_related("roles").all().iterator():
        first_role = profile.roles.first()
        if first_role:
            profile.role_id = first_role.id
            profile.save(update_fields=["role"])


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0003_jobrole_and_profile_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidateprofile",
            name="roles",
            field=models.ManyToManyField(blank=True, related_name="candidate_profiles", to="jobs.jobrole"),
        ),
        migrations.RunPython(copy_primary_role_to_roles, copy_roles_to_primary_role),
    ]