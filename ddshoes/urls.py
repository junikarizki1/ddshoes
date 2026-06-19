from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static
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
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)