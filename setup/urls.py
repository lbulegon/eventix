from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin

from app_eventos import views  

urlpatterns = [
    path("", views.health_check, name="health_check"),
    path("admin/", admin.site.urls),

    # JWT
    path("auth/jwt/create/", TokenObtainPairView.as_view(), name="jwt-create"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),

    

]

    # API v1 (negócio + auth de signup)
   # path("api/", include("api_v01.urls")),
]
