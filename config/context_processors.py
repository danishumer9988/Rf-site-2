from django.utils import timezone
from apps.jobs.models import Job
from apps.internships.models import Internship


def last_updated_context(request):
    latest_job = Job.objects.filter(is_active=True).order_by("-posted_at").first()
    latest_internship = Internship.objects.filter(is_active=True).order_by("-posted_at").first()

    timestamps = []

    if latest_job:
        timestamps.append(latest_job.posted_at)

    if latest_internship:
        timestamps.append(latest_internship.posted_at)

    last_updated = max(timestamps) if timestamps else timezone.now()

    return {
        "last_updated": last_updated
    }