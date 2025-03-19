from django.contrib import admin
from django.urls import path
from .views import HelloWorldView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
]
