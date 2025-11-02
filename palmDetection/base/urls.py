from django.contrib import admin
from django.urls import path
from .views import homePage, aboutPage, contactPage, techPage, techPageTabel, adminPage, adminPageTabel, farmsPage, farmsPageTabel, farmsPageDate
from . import views
from .views import analyze_drone_images
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import homePage
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', homePage, name="homePage"),
    path('about/', aboutPage, name="aboutPage"),
    path('contact/', contactPage, name="contactPage"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='homePage'), name="logout"),  # ✅ الحل الصحيح
    #path('logout/', auth_views.LogoutView.as_view(next_page='homePage'), name='logout'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('tech/', techPage, name="techPage"),
    path('tech_page/', views.techPage, name='techPage'),
    path('tech-tabel/<int:farm_id>/', views.techPageTabel, name="techPageTabel"),
    path('adminstrator/', adminPage, name="adminPage"),
    path('adminstrator-tabel/', adminPageTabel, name="adminPageTabel"),
    path("add-technician/", views.add_technician, name="add_technician"),
    path("delete-technician/<int:technician_id>/", views.delete_technician, name="delete_technician"),
    path("edit-technician/<int:technician_id>/", views.edit_technician, name="edit_technician"),
    path('farms/', farmsPage, name="farmsPage"),
    path('farms/tabel/', views.farmsPageTabel, name='farmsPageTabel'),
    path('farms/add/', views.add_farm, name='add_farm'), 
    path('farms/delete/<int:farm_id>/', views.delete_farm, name='delete_farm'), 
    path('farms/edit/<int:farm_id>/', views.edit_farm, name='edit_farm'),  
    path('farms/<int:farm_id>/history/', views.farmsPageDate, name="farm_history"),
    path('analyze-drone-images/', analyze_drone_images, name="analyze_drone_images"),
    path("farms/<int:farm_id>/end/", views.end_analysis, name="end_analysis"),  
    
]  

