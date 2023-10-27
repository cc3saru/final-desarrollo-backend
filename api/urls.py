from django.urls import include, path
from rest_framework import routers
from api.viewsets import UserViewSet, AuthViewSet
from knox import views as knox_views

router = routers.DefaultRouter()

router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', AuthViewSet.as_view(), name='knox_login'),
    path('auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
]