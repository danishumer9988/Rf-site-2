from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .views import home, robots_txt
from .sitemaps import sitemaps
from apps.accounts.views import logout_view

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', home, name='home'),
                  path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
                  path('robots.txt', robots_txt, name='robots_txt'),
                  path('jobs/', include('apps.jobs.urls')),
                  path('internships/', include('apps.internships.urls')),
                  path('accounts/', include('apps.accounts.urls')),
                  path('categories/', include('apps.categories.urls')),
                  path('contact/', include('apps.contact.urls')),
                  path('newsletter/', include('apps.newsletter.urls')),
                  path('dashboard/', include('apps.dashboard.urls')),
                  path('pages/', include('apps.pages.urls')),

                  # Direct logout path
                  path('logout/', logout_view, name='logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)