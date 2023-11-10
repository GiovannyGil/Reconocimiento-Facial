from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("addUser", views.usuariosAdd, name="AddUser"),
    path("userDetail/<int:pk>/", views.usuariosDetail, name="UserDetail"),
    path("", views.usuariosList, name="ListUsers"),
    path("UserRemove/<int:pk>/", views.usuariosRemove, name="UserRemove"),
    path("userUpdate/<int:pk>/", views.usuariosUpdate, name="UserUpdate"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # vinvula para la ruta de los archivos multimedia en el admin 