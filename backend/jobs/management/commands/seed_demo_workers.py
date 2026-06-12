import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from jobs.models import CandidateProfile, JobRole


DEMO_WORKERS = [
    {
        "username": "demo_sofia_moreno",
        "email": "sofia.moreno.demo@example.com",
        "first_name": "Sofía",
        "last_name": "Moreno",
        "role": "Cocinera",
        "city": "Rosario",
        "phone_prefix": "341",
        "years_experience": 8,
        "availability": "Full time",
        "bio": "Cocina de producción, mise en place prolijo y servicio de alto volumen.",
        "hair": (53, 35, 24),
        "skin": (241, 199, 170),
        "shirt": (214, 103, 60),
        "accent": (122, 74, 42),
    },
    {
        "username": "demo_lucas_pereyra",
        "email": "lucas.pereyra.demo@example.com",
        "first_name": "Lucas",
        "last_name": "Pereyra",
        "role": "Parrillero",
        "city": "Córdoba",
        "phone_prefix": "351",
        "years_experience": 11,
        "availability": "Noches y fines de semana",
        "bio": "Domina brasas, puntos de cocción y despacho coordinado en parrilla.",
        "hair": (35, 28, 24),
        "skin": (228, 182, 152),
        "shirt": (133, 81, 57),
        "accent": (85, 53, 36),
    },
    {
        "username": "demo_valentina_sosa",
        "email": "valentina.sosa.demo@example.com",
        "first_name": "Valentina",
        "last_name": "Sosa",
        "role": "Pastelera",
        "city": "Mendoza",
        "phone_prefix": "261",
        "years_experience": 6,
        "availability": "Turno mañana",
        "bio": "Pastelería fina, masas laminadas y montaje de postres para carta y eventos.",
        "hair": (75, 46, 35),
        "skin": (245, 208, 182),
        "shirt": (197, 103, 148),
        "accent": (123, 70, 99),
    },
    {
        "username": "demo_mateo_vidal",
        "email": "mateo.vidal.demo@example.com",
        "first_name": "Mateo",
        "last_name": "Vidal",
        "role": "Camarero",
        "city": "Mar del Plata",
        "phone_prefix": "223",
        "years_experience": 5,
        "availability": "Part time",
        "bio": "Atención de salón ágil, manejo de comanda y trato cercano con el cliente.",
        "hair": (26, 23, 23),
        "skin": (233, 194, 160),
        "shirt": (74, 120, 158),
        "accent": (42, 63, 82),
    },
    {
        "username": "demo_camila_rojas",
        "email": "camila.rojas.demo@example.com",
        "first_name": "Camila",
        "last_name": "Rojas",
        "role": "Bartender",
        "city": "Buenos Aires",
        "phone_prefix": "11",
        "years_experience": 9,
        "availability": "Noches",
        "bio": "Coctelería de autor, servicio de barra y armado de cartas de tragos.",
        "hair": (55, 34, 55),
        "skin": (240, 198, 168),
        "shirt": (94, 131, 110),
        "accent": (66, 87, 74),
    },
    {
        "username": "demo_tomas_farias",
        "email": "tomas.farias.demo@example.com",
        "first_name": "Tomás",
        "last_name": "Farías",
        "role": "Pizzero",
        "city": "Salta",
        "phone_prefix": "387",
        "years_experience": 7,
        "availability": "Full time",
        "bio": "Masa madre, horno de piedra y ritmo constante en producción de pizzas.",
        "hair": (86, 61, 49),
        "skin": (232, 186, 154),
        "shirt": (215, 146, 66),
        "accent": (128, 92, 49),
    },
    {
        "username": "demo_abrina_gomez",
        "email": "abrina.gomez.demo@example.com",
        "first_name": "Abrina",
        "last_name": "Gómez",
        "role": "Encargada de salón",
        "city": "Santa Fe",
        "phone_prefix": "342",
        "years_experience": 10,
        "availability": "Jornada completa",
        "bio": "Coordinación de equipo, resolución de incidencias y organización de salón.",
        "hair": (31, 46, 62),
        "skin": (241, 203, 175),
        "shirt": (109, 96, 158),
        "accent": (64, 59, 103),
    },
    {
        "username": "demo_nicolas_leiva",
        "email": "nicolas.leiva.demo@example.com",
        "first_name": "Nicolás",
        "last_name": "Leiva",
        "role": "Panadero",
        "city": "Tucumán",
        "phone_prefix": "381",
        "years_experience": 12,
        "availability": "Mañana temprano",
        "bio": "Fermentaciones largas, hornadas continuas y control de producción artesanal.",
        "hair": (71, 49, 30),
        "skin": (227, 185, 151),
        "shirt": (177, 124, 80),
        "accent": (109, 79, 50),
    },
    {
        "username": "demo_eugenia_flores",
        "email": "eugenia.flores.demo@example.com",
        "first_name": "Eugenia",
        "last_name": "Flores",
        "role": "Lavacopas",
        "city": "La Plata",
        "phone_prefix": "221",
        "years_experience": 4,
        "availability": "Turno noche",
        "bio": "Orden, velocidad y apoyo clave para que el servicio nunca se detenga.",
        "hair": (27, 31, 44),
        "skin": (236, 194, 162),
        "shirt": (88, 128, 146),
        "accent": (46, 69, 77),
    },
    {
        "username": "demo_agustin_vega",
        "email": "agustin.vega.demo@example.com",
        "first_name": "Agustín",
        "last_name": "Vega",
        "role": "Barista",
        "city": "Neuquén",
        "phone_prefix": "299",
        "years_experience": 7,
        "availability": "Tiempo completo",
        "bio": "Espresso, calibración de molino y atención amable en cafetería de especialidad.",
        "hair": (62, 41, 30),
        "skin": (239, 199, 169),
        "shirt": (171, 112, 76),
        "accent": (98, 63, 43),
    },
]

CITY_POOL = [
    "Buenos Aires",
    "Córdoba",
    "Rosario",
    "Mendoza",
    "La Plata",
    "Mar del Plata",
    "Salta",
    "Santa Fe",
    "Tucumán",
    "Neuquén",
]


REAL_PHOTO_FILES = sorted((settings.MEDIA_ROOT / "profile_photos").glob("worker_*.jpg"))


def pick_real_photo(role_index, persona_index):
    if not REAL_PHOTO_FILES:
        raise RuntimeError("No se encontraron fotos reales en media/profile_photos/worker_*.jpg")

    photo_index = (role_index * 10 + persona_index - 1) % len(REAL_PHOTO_FILES)
    return REAL_PHOTO_FILES[photo_index]


class Command(BaseCommand):
    help = "Crea 10 perfiles demo por cada rubro existente con fotos ficticias."

    def clear_existing_demo_data(self):
        demo_users = User.objects.filter(username__startswith="demo_").select_related("candidate_profile")
        for user in demo_users:
            profile = getattr(user, "candidate_profile", None)
            if profile and profile.personal_photo:
                profile.personal_photo.delete(save=False)
            user.delete()

        demo_dirs = [
            settings.MEDIA_ROOT / "profile_photos" / "demo",
            settings.MEDIA_ROOT / "profile_photos" / "profile_photos" / "demo",
        ]
        for directory in demo_dirs:
            if directory.exists():
                shutil.rmtree(directory)

    @transaction.atomic
    def handle(self, *args, **options):
        self.clear_existing_demo_data()

        roles = list(JobRole.objects.order_by("name"))
        created_profiles = 0

        for role_index, role in enumerate(roles):
            role_slug = slugify(role.name)

            for persona_index, worker in enumerate(DEMO_WORKERS, start=1):
                username = f"demo_{role_slug}_{persona_index:02d}"
                email = f"{username}@example.com"

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="Demo12345!",
                    first_name=worker["first_name"],
                    last_name=worker["last_name"],
                )

                profile = CandidateProfile.objects.create(
                    user=user,
                    first_name=worker["first_name"],
                    last_name=worker["last_name"],
                    phone=f"+54 {worker['phone_prefix']} 555-{role_index + 10:02d}{persona_index:02d}",
                    city=CITY_POOL[(role_index + persona_index - 1) % len(CITY_POOL)],
                    role=role,
                    years_experience=worker["years_experience"] + (role_index % 3),
                    availability=worker["availability"],
                    bio=worker["bio"].format(role=role.name.lower()),
                )

                photo_path = pick_real_photo(role_index, persona_index)
                avatar_name = f"demo/{role_slug}_{persona_index:02d}{photo_path.suffix.lower()}"
                with photo_path.open("rb") as photo_file:
                    profile.personal_photo.save(avatar_name, ContentFile(photo_file.read()), save=True)
                created_profiles += 1

        self.stdout.write(self.style.SUCCESS(f"Creados {created_profiles} perfiles demo: 10 por cada uno de los {len(roles)} rubros."))