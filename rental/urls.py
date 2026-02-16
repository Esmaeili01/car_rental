from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('signout/', views.signout_view, name='signout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/add/', views.add_car, name='add_car'),
    path('car/<int:car_id>/edit/', views.edit_car, name='edit_car'),
    path('car/<int:car_id>/rent/', views.request_rent, name='request_rent'),
    path('car/<int:car_id>/review/', views.add_review, name='add_review'),
    path('car/<int:car_id>/score/', views.add_score, name='add_score'),
    path('admin-action/<str:action>/<str:target_type>/<int:target_id>/', views.admin_action, name='admin_action'),
    path('reports/', views.reports, name='reports'),
    path('rent/<int:rent_id>/action/<str:action>/', views.rent_action, name='rent_action'),
    path('car-mgmt/<int:car_id>/<str:action>/', views.car_management, name='car_management'),
]
