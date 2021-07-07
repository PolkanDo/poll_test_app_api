from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url

urlpatterns = [
    path('api/', include('myapi.urls')),
]

schema_view = get_schema_view(
   openapi.Info(
      title="Polls API",
      default_version='v1',
      description="Документация для тестового задания 'API для опросов'",
      # terms_of_service="URL страницы с пользовательским соглашением",
      contact=openapi.Contact(email="admin@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
   url(r'^swagger(?P<format>\.json|\.yaml)$',
       schema_view.without_ui(cache_timeout=0), name='schema-json'),
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
       name='schema-swagger-ui'),
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
       name='schema-redoc'),
]