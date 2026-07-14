from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from apps.internships.models import Internship
from apps.categories.models import Category
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed 30 test internships (15 physical + 15 remote)'

    def handle(self, *args, **options):
        # Get existing categories
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found! Run seed_jobs first or create categories.'))
            return

        physical_internships = [
            {
                'title': 'Software Engineering Intern',
                'company': 'Google',
                'location': 'Mountain View, CA',
                'description': 'Join Google as a Software Engineering Intern. Work on real projects with experienced engineers and make an impact on millions of users.',
                'requirements': '- Currently pursuing CS degree\n- Strong programming skills\n- Data structures & algorithms\n- Problem-solving ability',
                'stipend': '$8,000/month',
                'duration': '3 months',
            },
            {
                'title': 'Data Science Intern',
                'company': 'Microsoft',
                'location': 'Redmond, WA',
                'description': 'Work alongside data scientists at Microsoft to analyze large datasets and build machine learning models.',
                'requirements': '- Statistics/CS background\n- Python/R proficiency\n- ML coursework\n- SQL knowledge',
                'stipend': '$7,500/month',
                'duration': '12 weeks',
            },
            {
                'title': 'Frontend Development Intern',
                'company': 'Meta',
                'location': 'Menlo Park, CA',
                'description': 'Build user interfaces for Meta products. Learn from top engineers and contribute to production code.',
                'requirements': '- JavaScript/React knowledge\n- HTML/CSS skills\n- Portfolio projects\n- Currently enrolled student',
                'stipend': '$7,000/month',
                'duration': '3 months',
            },
            {
                'title': 'DevOps Intern',
                'company': 'Amazon Web Services',
                'location': 'Seattle, WA',
                'description': 'Learn cloud infrastructure management at AWS. Work on deployment pipelines and monitoring systems.',
                'requirements': '- Linux fundamentals\n- Scripting (Bash/Python)\n- Networking basics\n- Cloud interest',
                'stipend': '$7,200/month',
                'duration': '4 months',
            },
            {
                'title': 'UX Design Intern',
                'company': 'Apple',
                'location': 'Cupertino, CA',
                'description': 'Design intuitive user experiences for Apple products. Collaborate with world-class designers.',
                'requirements': '- Design portfolio\n- Figma/Sketch skills\n- Design thinking\n- Currently pursuing degree',
                'stipend': '$6,500/month',
                'duration': '3 months',
            },
            {
                'title': 'Machine Learning Intern',
                'company': 'NVIDIA',
                'location': 'Santa Clara, CA',
                'description': 'Research and implement ML algorithms at NVIDIA. Work on cutting-edge AI hardware and software.',
                'requirements': '- ML/DL coursework\n- PyTorch/TensorFlow\n- CUDA knowledge (plus)\n- Strong math background',
                'stipend': '$8,500/month',
                'duration': '4 months',
            },
            {
                'title': 'Backend Engineering Intern',
                'company': 'Stripe',
                'location': 'San Francisco, CA',
                'description': 'Build payment infrastructure that powers millions of businesses. Learn distributed systems at scale.',
                'requirements': '- Backend programming\n- API design knowledge\n- Database basics\n- Problem-solving skills',
                'stipend': '$7,800/month',
                'duration': '3 months',
            },
            {
                'title': 'Cybersecurity Intern',
                'company': 'Palo Alto Networks',
                'location': 'Santa Clara, CA',
                'description': 'Learn network security and threat analysis. Protect enterprise customers from cyber attacks.',
                'requirements': '- Security fundamentals\n- Network knowledge\n- Python scripting\n- Security+ (plus)',
                'stipend': '$6,800/month',
                'duration': '3 months',
            },
            {
                'title': 'Full Stack Intern',
                'company': 'Airbnb',
                'location': 'San Francisco, CA',
                'description': 'Build features for Airbnb platform. Work across frontend and backend with modern technologies.',
                'requirements': '- JavaScript/Python\n- React experience\n- Web development basics\n- Collaborative mindset',
                'stipend': '$7,000/month',
                'duration': '12 weeks',
            },
            {
                'title': 'QA Testing Intern',
                'company': 'Salesforce',
                'location': 'San Francisco, CA',
                'description': 'Learn software testing methodologies at Salesforce. Write test cases and automate testing processes.',
                'requirements': '- Attention to detail\n- Basic programming\n- Testing concepts\n- Analytical thinking',
                'stipend': '$5,500/month',
                'duration': '3 months',
            },
            {
                'title': 'Blockchain Intern',
                'company': 'Coinbase',
                'location': 'New York, NY',
                'description': 'Explore blockchain technology and cryptocurrency at Coinbase. Build decentralized applications.',
                'requirements': '- Blockchain interest\n- Solidity (plus)\n- JavaScript/Python\n- Cryptography basics',
                'stipend': '$7,500/month',
                'duration': '4 months',
            },
            {
                'title': 'Mobile App Intern',
                'company': 'Uber',
                'location': 'San Francisco, CA',
                'description': 'Develop mobile features for Uber app. Work on iOS or Android with experienced mobile engineers.',
                'requirements': '- Swift or Kotlin\n- Mobile development interest\n- UI/UX awareness\n- Currently enrolled',
                'stipend': '$7,000/month',
                'duration': '3 months',
            },
            {
                'title': 'Data Engineering Intern',
                'company': 'Netflix',
                'location': 'Los Gatos, CA',
                'description': 'Build data pipelines at Netflix scale. Process petabytes of data for analytics and recommendations.',
                'requirements': '- Python/SQL skills\n- Big data interest\n- ETL concepts\n- Cloud platforms',
                'stipend': '$8,000/month',
                'duration': '12 weeks',
            },
            {
                'title': 'Site Reliability Intern',
                'company': 'LinkedIn',
                'location': 'Sunnyvale, CA',
                'description': 'Learn SRE practices at LinkedIn. Ensure platform reliability for 800M+ users worldwide.',
                'requirements': '- Linux skills\n- Programming (Python/Go)\n- Monitoring tools\n- Problem-solving',
                'stipend': '$7,200/month',
                'duration': '3 months',
            },
            {
                'title': 'Product Management Intern',
                'company': 'Atlassian',
                'location': 'San Francisco, CA',
                'description': 'Learn product management at Atlassian. Work with engineering and design to build developer tools.',
                'requirements': '- Technical background\n- Communication skills\n- User empathy\n- MBA or CS student',
                'stipend': '$6,500/month',
                'duration': '3 months',
            },
        ]

        remote_internships = [
            {
                'title': 'Remote Software Engineering Intern',
                'company': 'GitHub',
                'location': 'Remote - Global',
                'description': 'Contribute to open-source tools at GitHub. Work remotely with a distributed team of engineers.',
                'requirements': '- Programming skills\n- Git knowledge\n- Open-source contributions\n- Self-motivated',
                'stipend': '$6,000/month',
                'duration': '3 months',
            },
            {
                'title': 'Remote Web Development Intern',
                'company': 'Automattic',
                'location': 'Remote - Anywhere',
                'description': 'Join Automattic (WordPress.com) as a remote intern. Build features used by millions of websites.',
                'requirements': '- PHP/JavaScript\n- WordPress knowledge\n- Remote work skills\n- Communication',
                'stipend': '$5,000/month',
                'duration': '4 months',
            },
            {
                'title': 'Remote AI Research Intern',
                'company': 'OpenAI',
                'location': 'Remote - US',
                'description': 'Contribute to AI research remotely. Work on language models and generative AI technologies.',
                'requirements': '- ML research experience\n- PyTorch proficiency\n- Published papers (plus)\n- PhD/Masters student',
                'stipend': '$9,000/month',
                'duration': '4 months',
            },
            {
                'title': 'Remote Data Science Intern',
                'company': 'Shopify',
                'location': 'Remote - Americas',
                'description': 'Analyze e-commerce data at Shopify. Build models to help merchants succeed online.',
                'requirements': '- Python/R skills\n- SQL proficiency\n- Statistics knowledge\n- Remote collaboration',
                'stipend': '$6,500/month',
                'duration': '3 months',
            },
            {
                'title': 'Remote Frontend Intern',
                'company': 'Vercel',
                'location': 'Remote - Worldwide',
                'description': 'Learn Next.js and modern frontend at Vercel. Contribute to the future of web development.',
                'requirements': '- React/Next.js\n- TypeScript\n- CSS skills\n- Portfolio projects',
                'stipend': '$5,500/month',
                'duration': '3 months',
            },
            {
                'title': 'Remote DevOps Intern',
                'company': 'GitLab',
                'location': 'Remote - Global',
                'description': 'Learn DevOps practices at GitLab. Work on CI/CD pipelines and cloud infrastructure remotely.',
                'requirements': '- Linux/Unix skills\n- Docker/Kubernetes\n- Scripting languages\n- Remote discipline',
                'stipend': '$6,000/month',
                'duration': '4 months',
            },
            {
                'title': 'Remote Cybersecurity Intern',
                'company': 'Cloudflare',
                'location': 'Remote - US/EU',
                'description': 'Protect websites from attacks at Cloudflare. Learn about DDoS protection and web security.',
                'requirements': '- Security fundamentals\n- Networking (TCP/IP)\n- Programming skills\n- Problem-solving',
                'stipend': '$7,000/month',
                'duration': '3 months',
            },
            {
                'title': 'Remote Mobile Development Intern',
                'company': 'Spotify',
                'location': 'Remote - Europe',
                'description': 'Build mobile features for Spotify app. Work on iOS or Android from anywhere in Europe.',
                'requirements': '- Swift/Kotlin\n- Mobile dev basics\n- Music lover (plus)\n- European timezone',
                'stipend': '€5,000/month',
                'duration': '4 months',
            },
            {
                'title': 'Remote Content Writing Intern',
                'company': 'HubSpot',
                'location': 'Remote - Global',
                'description': 'Create technical content and tutorials at HubSpot. Learn content marketing and SEO.',
                'requirements': '- Writing skills\n- Technical knowledge\n- SEO basics\n- English proficiency',
                'stipend': '$4,000/month',
                'duration': '3 months',
            },
            {
                'title': 'Remote Game Development Intern',
                'company': 'Unity Technologies',
                'location': 'Remote - Worldwide',
                'description': 'Build game development tools at Unity. Work on the platform used by millions of game developers.',
                'requirements': '- C# programming\n- Unity experience\n- 3D math basics\n- Game development passion',
                'stipend': '$6,000/month',
                'duration': '4 months',
            },
            {
                'title': 'Remote Community Management Intern',
                'company': 'Discord',
                'location': 'Remote - US',
                'description': 'Help manage online communities at Discord. Learn community engagement and moderation strategies.',
                'requirements': '- Discord user\n- Communication skills\n- Community experience\n- Social media knowledge',
                'stipend': '$4,500/month',
                'duration': '3 months',
            },
            {
                'title': 'Remote Technical Support Intern',
                'company': 'Zapier',
                'location': 'Remote - Anywhere',
                'description': 'Help users automate workflows at Zapier. Provide technical support and create documentation.',
                'requirements': '- Technical aptitude\n- Problem-solving\n- Communication skills\n- Patience and empathy',
                'stipend': '$4,000/month',
                'duration': '3 months',
            },
            {
                'title': 'Remote Database Intern',
                'company': 'MongoDB',
                'location': 'Remote - Americas',
                'description': 'Learn database technologies at MongoDB. Work on database drivers and tools remotely.',
                'requirements': '- Database basics\n- Python/JavaScript\n- Open-source interest\n- Documentation skills',
                'stipend': '$6,500/month',
                'duration': '3 months',
            },
            {
                'title': 'Remote API Development Intern',
                'company': 'Twilio',
                'location': 'Remote - Global',
                'description': 'Build communication APIs at Twilio. Learn about REST APIs, webhooks, and cloud communications.',
                'requirements': '- API knowledge\n- Backend programming\n- HTTP/REST concepts\n- Documentation',
                'stipend': '$6,000/month',
                'duration': '4 months',
            },
            {
                'title': 'Remote Accessibility Intern',
                'company': 'Mozilla',
                'location': 'Remote - Worldwide',
                'description': 'Make the web more accessible at Mozilla. Work on Firefox accessibility features and standards.',
                'requirements': '- Web technologies\n- Accessibility passion\n- HTML/CSS/JS\n- Testing skills',
                'stipend': '$5,500/month',
                'duration': '3 months',
            },
        ]

        internships_created = 0

        self.stdout.write('\n📍 Creating Physical Internships...')
        for i, intern_data in enumerate(physical_internships):
            category = random.choice(categories)
            days_ago = random.randint(0, 45)
            posted_date = timezone.now() - timedelta(days=days_ago)

            internship = Internship.objects.create(
                title=intern_data['title'],
                slug=slugify(intern_data['title'] + '-' + str(i)),
                company=intern_data['company'],
                location=intern_data['location'],
                description=intern_data['description'],
                requirements=intern_data['requirements'],
                stipend=intern_data['stipend'],
                duration=intern_data['duration'],
                type='physical',
                category=category,
                apply_url=f'https://example.com/apply/{slugify(intern_data["title"])}',
                company_website=f'https://{slugify(intern_data["company"])}.com',
                is_active=True,
                posted_at=posted_date,
            )
            internships_created += 1
            self.stdout.write(f'  ✓ [{internships_created}/15] {internship.title}')

        self.stdout.write('\n🏠 Creating Remote Internships...')
        for i, intern_data in enumerate(remote_internships):
            category = random.choice(categories)
            days_ago = random.randint(0, 45)
            posted_date = timezone.now() - timedelta(days=days_ago)

            internship = Internship.objects.create(
                title=intern_data['title'],
                slug=slugify(intern_data['title'] + '-' + str(i + 15)),
                company=intern_data['company'],
                location=intern_data['location'],
                description=intern_data['description'],
                requirements=intern_data['requirements'],
                stipend=intern_data['stipend'],
                duration=intern_data['duration'],
                type='remote',
                category=category,
                apply_url=f'https://example.com/apply/{slugify(intern_data["title"])}',
                company_website=f'https://{slugify(intern_data["company"])}.com',
                is_active=True,
                posted_at=posted_date,
            )
            internships_created += 1
            self.stdout.write(f'  ✓ [{internships_created}/30] {internship.title}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {internships_created} internships!'))
        self.stdout.write(f'   📍 Physical internships: 15')
        self.stdout.write(f'   🏠 Remote internships: 15')