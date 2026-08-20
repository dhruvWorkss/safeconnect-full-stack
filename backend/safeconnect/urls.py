from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from moderation.views import AuditLogViewSet, BlockViewSet, CaseViewSet, NotificationViewSet, ReportViewSet, RegisterView, UserViewSet, dashboard_stats, health

router=DefaultRouter()
router.register("users",UserViewSet,"users"); router.register("reports",ReportViewSet,"reports"); router.register("blocks",BlockViewSet,"blocks"); router.register("cases",CaseViewSet,"cases"); router.register("notifications",NotificationViewSet,"notifications"); router.register("audit-logs",AuditLogViewSet,"audit-logs")
urlpatterns=[path("admin/",admin.site.urls),path("api/health/",health),path("api/auth/register/",RegisterView.as_view()),path("api/auth/token/",TokenObtainPairView.as_view()),path("api/auth/token/refresh/",TokenRefreshView.as_view()),path("api/dashboard/stats/",dashboard_stats),path("api/",include(router.urls))]
