from django.urls import path

from . import views

urlpatterns = [
    path("addUser", views.usuariosAdd, name="AddUser"),
    path("userDetail/<int:pk>/", views.usuariosDetail, name="UserDetail"),
    path("", views.usuariosList, name="ListUsers"),
    path("UserRemove/<int:pk>/", views.usuariosRemove, name="UserRemove"),
    path("userUpdate/<int:pk>/", views.usuariosUpdate, name="UserUpdate"),
]