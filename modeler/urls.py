from django.urls import path
from . import views

urlpatterns = [
    # Project URLs
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('project/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # Hub URLs
    path('project/<int:project_pk>/hub/new/', views.create_hub, name='create_hub'),
    path('hub/<int:pk>/edit/', views.update_hub, name='update_hub'),
    path('hub/<int:pk>/delete/', views.delete_hub, name='delete_hub'),

    # Link URLs
    path('project/<int:project_pk>/link/new/', views.create_link, name='create_link'),
    path('link/<int:pk>/edit/', views.update_link, name='update_link'),
    path('link/<int:pk>/delete/', views.delete_link, name='delete_link'),

    # Satellite URLs
    path('project/<int:project_pk>/satellite/new/', views.create_satellite, name='create_satellite'),
    path('satellite/<int:pk>/edit/', views.update_satellite, name='update_satellite'),
    path('satellite/<int:pk>/delete/', views.delete_satellite, name='delete_satellite'),

    # Visualization URLs
    path('project/<int:pk>/visualize/', views.visualize, name='visualize'),
    path('project/<int:pk>/view_ddl/', views.view_ddl, name='view_ddl'),
    path('project/<int:pk>/generate_ddl/', views.generate_ddl, name='generate_ddl'),
] 