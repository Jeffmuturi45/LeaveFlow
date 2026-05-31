from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_redirect),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/customize/', views.dashboard_customization_view, name='dashboard_customize'),
    path('core/settings/', views.company_settings_view, name='company_settings'),
    path('core/audit-log/', views.audit_log_view, name='audit_log'),
    path('core/notifications/mark-read/', views.mark_notifications_read, name='mark_read'),
]
