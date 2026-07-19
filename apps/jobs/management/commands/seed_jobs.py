import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from apps.jobs.models import Job
from apps.internships.models import Internship
from apps.categories.models import Category


class Command(BaseCommand):
    help = 'Generate fake jobs (all types) and internships for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--jobs',
            type=int,
            default=500,                     # ← changed from 50 to 500
            help='Number of fake jobs to create (default: 500)'
        )
        parser.add_argument(
            '--internships',
            type=int,
            default=500,                     # ← changed from 20 to 500
            help='Number of fake internships to create (default: 500)'
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

        self.stdout.write(self.style.WARNING('🚀 Generating fake data...'))
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

        # Generate jobs
        self.stdout.write(self.style.WARNING(f'📝 Creating {job_count} fake jobs...'))
        jobs_created = self._create_fake_jobs(job_count, user, categories)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {jobs_created} jobs'))

        # Generate internships
        self.stdout.write(self.style.WARNING(f'📝 Creating {internship_count} fake internships...'))
        internships_created = self._create_fake_internships(internship_count, user, categories)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {internships_created} internships'))

        self.stdout.write(self.style.SUCCESS('🎉 Fake data generation complete!'))

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

    def _create_fake_jobs(self, count, user, categories):
        """Create fake jobs of all types"""

        # Job titles by type
        job_titles = {
            'full_time': [
                'Senior Software Engineer', 'Project Manager', 'Data Scientist',
                'DevOps Engineer', 'Product Manager', 'UX Designer',
                'Sales Director', 'Marketing Manager', 'Financial Analyst',
                'Operations Manager', 'HR Manager', 'Business Analyst'
            ],
            'part_time': [
                'Part-Time Developer', 'Weekend Sales Associate', 'Part-Time Accountant',
                'Evening Customer Support', 'Part-Time Designer', 'Weekend Receptionist',
                'Part-Time Teacher', 'Evening Data Entry', 'Part-Time Social Media Manager'
            ],
            'contract': [
                'Contract Developer', 'Freelance Designer', 'Contract Project Manager',
                'Contract Writer', 'Freelance Consultant', 'Contract Marketing Specialist',
                'Contract QA Tester', 'Freelance Photographer', 'Contract Business Analyst'
            ],
            'daily': [
                'Daily Warehouse Worker', 'Event Staff', 'Daily Construction Worker',
                'Daily Delivery Driver', 'Daily Cleaner', 'Daily Security Guard',
                'Daily Kitchen Helper', 'Daily Farm Worker', 'Daily Store Associate'
            ]
        }

        # Company names
        companies = [
            'TechCorp', 'HealthPlus', 'FinancePro', 'EduWorld', 'RetailHub',
            'BuildRight', 'MarketMasters', 'DesignStudio', 'HospitalityInc',
            'ManufactureCo', 'TransportPros', 'EngineeringSolutions',
            'CloudNine', 'DataFlow', 'SecureNet', 'GreenEnergy', 'SmartInnovations'
        ]

        # Locations
        locations = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Miami, FL', 'Seattle, WA', 'Boston, MA', 'Austin, TX',
            'San Francisco, CA', 'Denver, CO', 'Atlanta, GA', 'Dallas, TX',
            'Phoenix, AZ', 'Philadelphia, PA', 'San Diego, CA', 'Orlando, FL',
            'Remote', 'Portland, OR', 'Nashville, TN', 'Charlotte, NC'
        ]

        # Descriptions
        descriptions = [
            'We are looking for a talented professional to join our growing team.',
            'Exciting opportunity for a motivated individual to make a real impact.',
            'Join our dynamic team and help us build the future of our industry.',
            'We are seeking a dedicated person to contribute to our success.',
            'Great opportunity for someone looking to grow their career.',
            'We need a skilled professional to help us achieve our goals.',
            'Come work with us and be part of something amazing!',
            'We are expanding and need talented individuals to join us.',
            'Join our innovative team and help shape the future.',
            'We are looking for a passionate person to join our mission.'
        ]

        # Requirements
        requirements = [
            'Strong communication skills and team player mindset.',
            'Minimum 2 years of experience in a related field.',
            'Bachelor\'s degree or equivalent experience required.',
            'Proficiency in relevant tools and technologies.',
            'Ability to work independently and in a team environment.',
            'Excellent problem-solving and analytical skills.',
            'Strong attention to detail and organizational skills.',
            'Ability to manage multiple tasks and meet deadlines.',
            'Positive attitude and willingness to learn.',
            'Experience working in a fast-paced environment.'
        ]

        jobs_created = 0
        employment_types = ['full_time', 'part_time', 'contract', 'daily']

        for i in range(count):
            employment_type = random.choice(employment_types)
            titles = job_titles[employment_type]
            category = random.choice(categories)

            # Generate random dates within the last 30 days
            days_ago = random.randint(0, 30)
            posted_at = timezone.now() - timedelta(days=days_ago)

            # Generate expiry date (30-90 days from now)
            expires_days = random.randint(30, 90)
            expires_at = timezone.now() + timedelta(days=expires_days)

            # Base fields
            job_data = {
                'title': random.choice(titles),
                'company': random.choice(companies),
                'location': random.choice(locations),
                'description': random.choice(descriptions),
                'requirements': random.choice(requirements),
                'category': category,
                'employment_type': employment_type,
                'work_type': random.choice(['remote', 'physical', 'hybrid']),
                'posted_at': posted_at,
                'expires_at': expires_at,
                'is_active': True,
                'is_user_submitted': True,
                'posted_by': user,
                'views': random.randint(10, 500),
                'likes': random.randint(0, 100),
                'clicks': random.randint(5, 200),
                'applications_count': random.randint(0, 50),
                'apply_url': f'https://{random.choice(companies).lower()}.com/careers/{i}',
                'company_website': f'https://{random.choice(companies).lower()}.com',
                'contact_email': f'hr@{random.choice(companies).lower()}.com',
            }

            # Add type-specific fields
            if employment_type == 'full_time':
                job_data['salary_range'] = random.choice([
                    '$60,000 - $80,000', '$80,000 - $100,000',
                    '$100,000 - $120,000', '$70,000 - $90,000',
                    '$90,000 - $110,000', '$120,000 - $150,000'
                ])
                job_data['salary_min'] = random.randint(60000, 80000)
                job_data['salary_max'] = job_data['salary_min'] + random.randint(10000, 40000)
                job_data['salary_currency'] = 'USD'
                job_data['salary_period'] = random.choice(['yearly', 'monthly', 'hourly'])

            elif employment_type == 'part_time':
                job_data['salary_range'] = random.choice([
                    '$20 - $25/hr', '$25 - $30/hr', '$18 - $22/hr',
                    '$30 - $35/hr', '$15 - $20/hr', '$22 - $28/hr'
                ])
                job_data['salary_min'] = random.randint(15, 25)
                job_data['salary_max'] = job_data['salary_min'] + random.randint(5, 15)
                job_data['salary_currency'] = 'USD'
                job_data['salary_period'] = 'hourly'

            elif employment_type == 'contract':
                job_data['contract_type'] = random.choice(['fixed', 'hourly', 'milestone'])
                job_data['budget_min'] = random.randint(1000, 5000)
                job_data['budget_max'] = job_data['budget_min'] + random.randint(1000, 10000)
                job_data['currency'] = 'USD'
                job_data['experience_level'] = random.choice(['entry', 'intermediate', 'expert'])
                job_data['duration_type'] = random.choice(['short', 'medium', 'long', 'ongoing'])
                job_data['estimated_duration'] = random.choice([
                    '2-3 months', '3-6 months', '6-12 months', '1 year', 'Ongoing'
                ])
                job_data['start_date'] = (timezone.now() + timedelta(days=random.randint(1, 30))).date()
                job_data['end_date'] = (timezone.now() + timedelta(days=random.randint(60, 180))).date()
                job_data['is_urgent'] = random.choice([True, False])

            elif employment_type == 'daily':
                job_data['payment_method'] = random.choice(['hourly', 'daily', 'weekly'])
                job_data['payment_amount'] = random.randint(50, 500)
                job_data['currency'] = 'USD'
                job_data['start_date'] = (timezone.now() + timedelta(days=random.randint(1, 7))).date()
                job_data['end_date'] = (timezone.now() + timedelta(days=random.randint(7, 60))).date()
                job_data['working_hours'] = random.choice([
                    '9 AM - 5 PM', '8 AM - 4 PM', '10 AM - 6 PM',
                    '7 AM - 3 PM', '11 AM - 7 PM', '6 AM - 2 PM'
                ])
                job_data['is_immediate'] = random.choice([True, False])
                job_data['contact_phone'] = f'+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}'

            # Create the job
            job = Job(**job_data)
            job.save()
            jobs_created += 1

            if jobs_created % 50 == 0:
                self.stdout.write(f'  Created {jobs_created} jobs...')

        return jobs_created

    def _create_fake_internships(self, count, user, categories):
        """Create fake internships"""

        internship_titles = [
            'Software Engineering Intern', 'Marketing Intern', 'Finance Intern',
            'HR Intern', 'Design Intern', 'Data Analytics Intern',
            'Business Development Intern', 'Content Writing Intern',
            'Social Media Intern', 'Accounting Intern', 'Legal Intern',
            'Research Intern', 'Engineering Intern', 'Sales Intern',
            'Customer Success Intern', 'Product Management Intern',
            'UI/UX Design Intern', 'DevOps Intern', 'Data Science Intern'
        ]

        companies = [
            'TechStart', 'HealthHub', 'FinFocus', 'EduLearn', 'RetailNow',
            'BuildSmart', 'MarketPulse', 'DesignLab', 'HospitalityWorld',
            'ManufacturePlus', 'TransportFast', 'EngineerPro', 'CloudSolutions',
            'DataVault', 'SecureNet', 'GreenFuture', 'SmartTech'
        ]

        locations = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Miami, FL', 'Seattle, WA', 'Boston, MA', 'Austin, TX',
            'San Francisco, CA', 'Denver, CO', 'Remote', 'Atlanta, GA',
            'Portland, OR', 'Nashville, TN', 'Charlotte, NC'
        ]

        descriptions = [
            'Gain valuable experience in a fast-paced environment.',
            'Learn from industry experts and grow your career.',
            'Exciting opportunity to kickstart your professional journey.',
            'Work on real projects and build your portfolio.',
            'Develop skills that will set you up for success.',
            'Join our team and make a meaningful contribution.',
            'Get hands-on experience in a dynamic work environment.',
            'Start your career with a leading company in the industry.'
        ]

        requirements = [
            'Currently enrolled in a Bachelor\'s or Master\'s program.',
            'Strong communication and interpersonal skills.',
            'Eagerness to learn and take on new challenges.',
            'Basic knowledge of relevant tools and technologies.',
            'Ability to work in a team environment.',
            'Detail-oriented and well-organized.',
            'Passion for learning and professional growth.'
        ]

        internships_created = 0

        for i in range(count):
            category = random.choice(categories)
            days_ago = random.randint(0, 30)
            posted_at = timezone.now() - timedelta(days=days_ago)

            internship_data = {
                'title': random.choice(internship_titles),
                'company': random.choice(companies),
                'location': random.choice(locations),
                'description': random.choice(descriptions),
                'requirements': random.choice(requirements),
                'category': category,
                'type': random.choice(['remote', 'physical']),
                'stipend': random.choice([
                    '$500 - $1,000/month', '$1,000 - $1,500/month',
                    '$1,500 - $2,000/month', 'Unpaid', '$2,000 - $3,000/month',
                    '$3,000 - $4,000/month', '$800 - $1,200/month'
                ]),
                'duration': random.choice([
                    '3 months', '6 months', '12 months', '4 months', '2 months'
                ]),
                'posted_at': posted_at,
                'is_active': True,
                # If your model has these fields, uncomment:
                # 'is_user_submitted': True,
                # 'posted_by': user,
                # 'apply_url': f'https://{random.choice(companies).lower()}.com/internships/{i}',
                # 'company_website': f'https://{random.choice(companies).lower()}.com',
                # 'contact_email': f'hr@{random.choice(companies).lower()}.com',
            }

            internship = Internship(**internship_data)
            internship.save()
            internships_created += 1

            if internships_created % 50 == 0:
                self.stdout.write(f'  Created {internships_created} internships...')

        return internships_created