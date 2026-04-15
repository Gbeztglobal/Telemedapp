import os
from django.core.management.base import BaseCommand
from apps.accounts.models import User, DoctorProfile


class Command(BaseCommand):
    help = 'Auto-create a superuser from environment variables if one does not exist'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@telemed.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_PASSWORD not set — skipping superuser creation.'
            ))
            return

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            # Ensure the DoctorProfile exists
            if user.role == User.Role.DOCTOR and not hasattr(user, 'doctor_profile'):
                DoctorProfile.objects.create(
                    user=user,
                    specialty='General Medicine',
                    license_number='ADMIN-001',
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Created missing DoctorProfile for "{username}".'
                ))
            self.stdout.write(self.style.SUCCESS(
                f'Superuser "{username}" already exists — skipping.'
            ))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role=User.Role.DOCTOR,
            first_name='Admin',
            last_name='Doctor',
        )

        # Create the DoctorProfile so the dashboard works
        DoctorProfile.objects.create(
            user=user,
            specialty='General Medicine',
            license_number='ADMIN-001',
        )

        self.stdout.write(self.style.SUCCESS(
            f'Superuser "{username}" with DoctorProfile created successfully.'
        ))
