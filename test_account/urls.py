from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin

admin.AdminSite.site_header = 'HiP House Voting System'
admin.AdminSite.site_title = 'HiP House Voting System'
admin.site_header = 'HiP House Voting System'
admin.site_title = 'HiP House Voting System'

urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^testapp/", include("testapp.urls")),
    url(r"^polls/", include("polls.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r"^invitations/", include("invitations.urls", namespace='invitations'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
