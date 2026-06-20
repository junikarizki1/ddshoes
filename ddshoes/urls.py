from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.contrib import admin
from django.views.generic import TemplateView

admin.site.site_header = "DD Shoes Admin"
admin.site.site_title = "DD Shoes Store Portal"
admin.site.index_title = "Dashboard DD Shoes"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include ('store.urls')),
    path('cart/', include('cart.urls')),
    path('order/', include('order.urls')),
    path('account/', include('account.urls')),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    # Serve media files unconditionally (works with DEBUG=False in production)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]