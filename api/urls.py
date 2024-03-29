from django.urls import path, re_path

from rest_framework.routers import DefaultRouter
from rest_framework import permissions

from api.views import AdminApiView, HistoricalStocks, RealTimeStocks, TrackerViewSet, UserRegisterView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


schema_view = get_schema_view(
    openapi.Info(
        title="Solai",
        default_version='v1',
        description="Solai is an open-source project providing realtime and historical stocks pricing and performance populated by public data",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mwevibrian@gmail.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


routes = DefaultRouter()
routes.register('tracker', TrackerViewSet, 'tracker')

urlpatterns = [
    path('realtime/', RealTimeStocks.as_view(), name="realtime_stocks"),
    path('realtime/admin/', AdminApiView.as_view(), name="admin"),
    path('history/', HistoricalStocks.as_view(), name="history_stocks"),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
                                         cache_timeout=0), name='schema-swagger-ui'),
    path('', schema_view.with_ui('redoc',
                                 cache_timeout=0), name='schema-redoc'),
    path('auth/register/', UserRegisterView.as_view(), name="register"),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += routes.urls
