from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employees/', views.employees_list, name='employees_list'),
    path('time_tracking/', views.time_tracking, name='time_tracking'),
    path('start_session/', views.start_session, name='start_session'),
    path('stop_session/', views.stop_session, name='stop_session'),
    path('add_manual_entry/', views.add_manual_entry, name='add_manual_entry'),
    path('reports/', views.reports, name='reports'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('approve_entry/<int:entry_id>/', views.approve_entry, name='approve_entry'),
    path('toggle_employee_status/<int:employee_id>/', views.toggle_employee_status, name='toggle_employee_status'),
    path('delete_entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
]