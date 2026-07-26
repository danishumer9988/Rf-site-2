from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.jobs.models import Job
from apps.internships.models import Internship


class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Job.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class InternshipSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Internship.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    """Home page and static listing/info pages that don't come from a model."""
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return [
            "home",
            "job_list",
            "internship_list",
            "contact",
            "faq",
            "privacy",
            "terms",
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "jobs": JobSitemap,
    "internships": InternshipSitemap,
    "static": StaticViewSitemap,
}
