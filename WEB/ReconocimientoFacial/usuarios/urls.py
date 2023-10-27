from django.urls import path

from . import views

urlpatterns = [
    path("addUser", views.usuariosAdd, name="AddUser"),
    path("userDetail", views.usuariosDetail, name="UserDetail"),
    path("", views.usuariosList, name="ListUsers"),
    path("UserRemove", views.usuariosRemove, name="UserRemove"),
    path("userUpdate", views.usuariosUpdate, name="UserUpdate"),
]