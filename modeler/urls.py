from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("hubs/create/", views.create_hub, name="create_hub"),
    path("hubs/<int:pk>/update/", views.update_hub, name="update_hub"),
    path("hubs/<int:pk>/delete/", views.delete_hub, name="delete_hub"),
    path("links/create/", views.create_link, name="create_link"),
    path("links/<int:pk>/update/", views.update_link, name="update_link"),
    path("links/<int:pk>/delete/", views.delete_link, name="delete_link"),
    path("satellites/create/", views.create_satellite, name="create_satellite"),
    path("satellites/<int:pk>/update/", views.update_satellite, name="update_satellite"),
    path("satellites/<int:pk>/delete/", views.delete_satellite, name="delete_satellite"),
    path("visualize/", views.visualize_model, name="visualize_model"),
    path("visualize-classdiagram/", views.visualize_classdiagram, name="visualize_classdiagram"),
] 