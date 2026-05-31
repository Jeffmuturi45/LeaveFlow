from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.apply_leave, name='apply_leave'),
    path('my-leaves/', views.my_leaves, name='my_leaves'),
    path('detail/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('action/<int:pk>/', views.leave_action, name='leave_action'),
    path('approvals/manager/', views.manager_approvals, name='manager_approvals'),
    path('approvals/hr/', views.hr_approvals, name='hr_approvals'),
    path('balance/', views.leave_balance, name='leave_balance'),
    path('calendar/', views.leave_calendar, name='leave_calendar'),
    path('types/', views.leave_types, name='leave_types'),
    path('holidays/', views.public_holidays, name='public_holidays'),
    path('reports/', views.reports, name='reports'),
]