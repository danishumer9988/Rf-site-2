import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from apps.jobs.models import Job
from apps.internships.models import Internship
from apps.categories.models import Category


class Command(BaseCommand):
    help = 'Generate one rich job and one rich internship (or more if specified)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--jobs',
            type=int,
            default=1,
            help='Number of jobs to create (default: 1)'
        )
        parser.add_argument(
            '--internships',
            type=int,
            default=1,
            help='Number of internships to create (default: 1)'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete existing fake data first'
        )

    def handle(self, *args, **options):
        job_count = options['jobs']
        internship_count = options['internships']
        delete_existing = options['delete']

        self.stdout.write(self.style.WARNING('🚀 Generating data...'))
        self.stdout.write(self.style.WARNING(f'📊 Jobs: {job_count} | Internships: {internship_count}'))

        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'is_active': True
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Created test user: {user.username}'))

        # Delete existing fake data if requested
        if delete_existing:
            fake_jobs = Job.objects.filter(is_user_submitted=True)
            fake_internships = Internship.objects.filter(is_user_submitted=True)
            jobs_deleted = fake_jobs.count()
            internships_deleted = fake_internships.count()
            fake_jobs.delete()
            fake_internships.delete()
            self.stdout.write(self.style.WARNING(f'🗑️ Deleted {jobs_deleted} jobs and {internships_deleted} internships'))

        # Get or create categories
        categories = self._get_or_create_categories()

        # --- CREATE RICH JOBS ---
        self.stdout.write(self.style.WARNING(f'📝 Creating {job_count} rich job(s)...'))
        jobs_created = self._create_rich_jobs(job_count, user, categories)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {jobs_created} job(s)'))

        # --- CREATE RICH INTERNSHIPS ---
        self.stdout.write(self.style.WARNING(f'📝 Creating {internship_count} rich internship(s)...'))
        internships_created = self._create_rich_internships(internship_count, user, categories)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {internships_created} internship(s)'))

        self.stdout.write(self.style.SUCCESS('🎉 Data generation complete!'))

    def _get_or_create_categories(self):
        """Get or create default categories"""
        categories_data = [
            {'name': 'Technology', 'slug': 'technology', 'icon': '💻'},
            {'name': 'Healthcare', 'slug': 'healthcare', 'icon': '🏥'},
            {'name': 'Finance', 'slug': 'finance', 'icon': '💰'},
            {'name': 'Education', 'slug': 'education', 'icon': '📚'},
            {'name': 'Retail', 'slug': 'retail', 'icon': '🛍️'},
            {'name': 'Construction', 'slug': 'construction', 'icon': '🏗️'},
            {'name': 'Marketing', 'slug': 'marketing', 'icon': '📢'},
            {'name': 'Design', 'slug': 'design', 'icon': '🎨'},
            {'name': 'Hospitality', 'slug': 'hospitality', 'icon': '🏨'},
            {'name': 'Manufacturing', 'slug': 'manufacturing', 'icon': '🏭'},
            {'name': 'Transportation', 'slug': 'transportation', 'icon': '🚚'},
            {'name': 'Engineering', 'slug': 'engineering', 'icon': '⚙️'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created category: {category.name}'))

        return categories

    # ============================================================
    # RICH JOB GENERATION (uses templates)
    # ============================================================

    def _create_rich_jobs(self, count, user, categories):
        """Create jobs using rich templates"""
        job_templates = [
            {
                'title': 'Senior Full Stack Python (Django) Developer',
                'company': 'TechNova Solutions Pvt. Ltd.',
                'location': 'Lahore, Punjab, Pakistan',
                'description': 'TechNova Solutions is looking for an experienced Full Stack Python (Django) Developer to join our growing engineering team. You will be responsible for designing, developing, and maintaining scalable web applications using Django, Django REST Framework, PostgreSQL, JavaScript, HTML, and CSS.\n\nYou will work closely with UI/UX designers, product managers, and backend engineers to build secure, high-performance applications used by thousands of users worldwide.\n\nThis is an excellent opportunity for developers who enjoy solving complex technical challenges and building modern web platforms in an agile environment.',
                'requirements': 'Bachelor\'s degree in Computer Science, Software Engineering, or a related field.\n3+ years of experience with Python and Django.\nStrong knowledge of Django REST Framework.\nExperience with PostgreSQL or MySQL.\nGood understanding of HTML5, CSS3, JavaScript, and Bootstrap.\nExperience with Git and GitHub.\nFamiliarity with REST APIs.\nUnderstanding of authentication using JWT or OAuth.\nKnowledge of Docker is a plus.\nExperience deploying applications on Linux servers.\nStrong debugging and problem-solving skills.\nExcellent communication skills.\nAbility to work independently in a remote environment.',
                'work_type': 'remote',
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'salary_min': 220000.00,
                'salary_max': 350000.00,
                'salary_currency': 'USD',
                'salary_period': 'monthly',
                'benefits': 'Health Insurance\nAnnual Bonus\nRemote Work\nPaid Annual Leave\nFlexible Working Hours\nPerformance Bonus\nCareer Growth\nLearning Budget\nPaid Certifications\nTeam Retreats',
                'is_remote': True,
                'apply_url': 'https://careers.technovasolutions.com/jobs/senior-full-stack-python-django-developer',
                'company_website': 'https://www.technovasolutions.com',
                'contact_email': 'careers@technovasolutions.com',
                'contact_phone': '+92 42 3512 4567',
                'is_active': True,
                'is_featured': True,
                'is_urgent': False,
                'expires_at': timezone.now() + timedelta(days=45),
                'category': 'Technology',
            },
            # You can add more templates here if you want variety
        ]

        created = 0
        for i in range(count):
            # Pick a template (if multiple, cycle or pick random)
            template = random.choice(job_templates) if len(job_templates) > 1 else job_templates[0]

            # Find the category object
            category = next((c for c in categories if c.name == template['category']), categories[0])

            # Build the job dict
            job_data = {
                'title': template['title'],
                'company': template['company'],
                'location': template['location'],
                'description': template['description'],
                'requirements': template['requirements'],
                'work_type': template['work_type'],
                'employment_type': template['employment_type'],
                'experience_level': template.get('experience_level'),
                'salary_min': template.get('salary_min'),
                'salary_max': template.get('salary_max'),
                'salary_currency': template.get('salary_currency', 'USD'),
                'salary_period': template.get('salary_period', 'monthly'),
                'benefits': template.get('benefits', ''),
                'is_remote': template.get('is_remote', False),
                'apply_url': template.get('apply_url', ''),
                'company_website': template.get('company_website', ''),
                'contact_email': template.get('contact_email', ''),
                'contact_phone': template.get('contact_phone', ''),
                'is_active': template.get('is_active', True),
                'is_featured': template.get('is_featured', False),
                'is_urgent': template.get('is_urgent', False),
                'expires_at': template.get('expires_at', timezone.now() + timedelta(days=30)),
                'posted_by': user,
                'is_user_submitted': True,
                'category': category,
                'posted_at': timezone.now() - timedelta(days=random.randint(0, 5)),
                'views': random.randint(10, 200),
                'likes': random.randint(1, 30),
                'clicks': random.randint(5, 50),
                'applications_count': random.randint(0, 10),
            }

            # Add any missing fields for specific types
            if job_data['employment_type'] == 'full_time':
                job_data.setdefault('experience_level', 'mid')
                job_data.setdefault('salary_min', 60000)
                job_data.setdefault('salary_max', 80000)
                job_data.setdefault('salary_currency', 'USD')
                job_data.setdefault('salary_period', 'yearly')
                job_data.setdefault('benefits', 'Health Insurance, 401k, Paid Time Off')

            elif job_data['employment_type'] == 'part_time':
                job_data.setdefault('hourly_rate', random.randint(15, 30))
                job_data.setdefault('shift_type', random.choice(['morning', 'evening', 'flexible']))
                job_data.setdefault('hours_per_week', random.randint(10, 30))
                job_data.setdefault('salary_range', f"${job_data.get('hourly_rate', 20)}/hour")
                job_data.setdefault('is_flexible_schedule', random.choice([True, False]))
                job_data.setdefault('is_weekend_available', random.choice([True, False]))
                job_data.setdefault('is_immediate', random.choice([True, False]))

            elif job_data['employment_type'] == 'contract':
                job_data.setdefault('contract_type', random.choice(['fixed', 'hourly']))
                job_data.setdefault('budget_min', random.randint(1000, 5000))
                job_data.setdefault('budget_max', job_data['budget_min'] + random.randint(1000, 5000))
                job_data.setdefault('contract_currency', 'USD')
                job_data.setdefault('contract_experience_level', random.choice(['entry', 'mid', 'senior']))
                job_data.setdefault('duration_type', random.choice(['short', 'medium', 'long']))
                job_data.setdefault('estimated_duration', random.choice(['3 months', '6 months']))
                job_data.setdefault('contract_start_date', (timezone.now() + timedelta(days=random.randint(1, 10))).date())
                job_data.setdefault('contract_end_date', (timezone.now() + timedelta(days=random.randint(60, 120))).date())
                job_data.setdefault('is_contract_remote', random.choice([True, False]))
                job_data.setdefault('is_contract_urgent', random.choice([True, False]))

            elif job_data['employment_type'] == 'daily':
                job_data.setdefault('payment_method', random.choice(['daily', 'hourly']))
                job_data.setdefault('payment_amount', random.randint(50, 300))
                job_data.setdefault('currency', 'USD')
                job_data.setdefault('start_date', (timezone.now() + timedelta(days=1)).date())
                job_data.setdefault('end_date', (timezone.now() + timedelta(days=random.randint(7, 30))).date())
                job_data.setdefault('working_hours', random.choice(['9 AM - 5 PM', '8 AM - 4 PM', '10 AM - 6 PM']))
                job_data.setdefault('is_immediate_joining', random.choice([True, False]))

            # Create the job
            job = Job(**job_data)
            job.save()
            created += 1

            if created % 10 == 0:
                self.stdout.write(f'  Created {created} job(s)...')

        return created

    # ============================================================
    # RICH INTERNSHIP GENERATION (uses templates)
    # ============================================================

    def _create_rich_internships(self, count, user, categories):
        """Create internships using rich templates"""
        internship_templates = [
            {
                'title': 'Software Engineering Intern (Remote)',
                'company': 'TechNova Solutions Pvt. Ltd.',
                'location': 'Remote',
                'type': 'remote',
                'internship_type': 'full_time',
                'description': 'We are looking for a motivated Software Engineering Intern to join our remote team. You will work on real-world projects, collaborate with senior engineers, and gain hands-on experience in full-stack development using Django, React, and PostgreSQL.',
                'requirements': 'Currently pursuing a Bachelor\'s or Master\'s degree in Computer Science or related field.\nFamiliarity with Python, Django, or JavaScript.\nBasic understanding of web development.\nGood communication skills.\nAbility to work remotely and self-motivated.',
                'stipend': '$1,200/month',
                'duration': '6 months',
                'category': 'Technology',
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=60),
                'apply_url': 'https://technovasolutions.com/internships/software-engineering-remote',
                'company_website': 'https://technovasolutions.com',
                'is_user_submitted': True,
                'posted_by': user,
                'posted_at': timezone.now() - timedelta(days=2),
                'views': random.randint(10, 100),
                'likes': random.randint(1, 20),
                'clicks': random.randint(5, 30),
                'applications_count': random.randint(1, 10),
            },
        ]

        created = 0
        for i in range(count):
            template = random.choice(internship_templates) if len(internship_templates) > 1 else internship_templates[0]

            category = next((c for c in categories if c.name == template['category']), categories[0])

            internship_data = {
                'title': template['title'],
                'company': template['company'],
                'location': template['location'],
                'type': template['type'],
                'internship_type': template['internship_type'],
                'description': template['description'],
                'requirements': template['requirements'],
                'stipend': template['stipend'],
                'duration': template['duration'],
                'category': category,
                'is_active': template.get('is_active', True),
                'expires_at': template.get('expires_at', timezone.now() + timedelta(days=45)),
                'apply_url': template.get('apply_url', ''),
                'company_website': template.get('company_website', ''),
                'posted_by': user,
                'is_user_submitted': True,
                'posted_at': template.get('posted_at', timezone.now() - timedelta(days=random.randint(0, 5))),
                'views': template.get('views', random.randint(10, 100)),
                'likes': template.get('likes', random.randint(1, 20)),
                'clicks': template.get('clicks', random.randint(5, 30)),
                'applications_count': template.get('applications_count', random.randint(1, 10)),
            }

            internship = Internship(**internship_data)
            internship.save()
            created += 1

            if created % 10 == 0:
                self.stdout.write(f'  Created {created} internship(s)...')

        return created