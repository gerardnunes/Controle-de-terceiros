
from django.contrib import admin
from django.urls import path, include
from gestao import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestao.urls')),
]
