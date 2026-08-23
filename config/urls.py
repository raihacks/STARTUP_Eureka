"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.auth import logout
from django.shortcuts import redirect

def simple_logout(request):
    logout(request)
    return redirect('/product/catalog/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('product/', include('products.urls')), 
    
     
    # NEW — Booking Service (web/template flow)
    path("booking/", include("bookings.urls")),

    # NEW — Payment & Escrow Service (web checkout page)
    path("payments/", include(("payments.urls", "payments"), namespace="payments")),

    # NEW — Mobile REST API (both services)
    path("api/bookings/", include(("bookings.api_urls", "bookings_api"), namespace="bookings_api")),
    path("api/payments/", include(("payments.api_urls", "payments_api"), namespace="payments_api")),



    path('logout/', simple_logout, name='logout'),      
    path('', RedirectView.as_view(pattern_name='accounts:dashboard', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
