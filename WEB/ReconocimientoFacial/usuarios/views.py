from django.shortcuts import render, redirect, get_object_or_404
from .models import Persona, Cargo
from .forms import PersonaForm
from django.contrib.auth.models import User  # registrar usuarios
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='/login/')
def usuariosList(request):
    GetPersonas = Persona.objects.all() # traer todos los registros de la tabla Persona
    return render(request, "usuarios/index.html", {
        'peronsas':GetPersonas # pasarle los registros a la vista
    })
    
@login_required(login_url='/login/')
def usuariosAdd(request):
    # if request.method == 'GET':
    #     return render(request, "usuarios/addUser.html")
    # else:
        try:
            form = PersonaForm(request.POST) # valia que sea el metodo post y envia
            NuevaPersona = form.save(commit=False)
            #NuevaPersona.user = request.user # muestra/trae al usuario que registro a la persona
            if 'foto' in request.FILES:  # Verifica si se envió una foto
                NuevaPersona.foto = request.FILES['foto']  # Asigna la foto al campo 'foto'
            NuevaPersona.save() # guardar registro
            return redirect('ListUsers')
        except ValueError:
            return render(request, 'usuarios/addUser.html',{
                'form' : PersonaForm,
                'error' : "Comprueba que los datos esten correctos"
            })
            
@login_required(login_url='/login/')
def usuariosRemove(request, UsuarioID):
    usuarioPersona = get_object_or_404(pk=UsuarioID)
    if(request.method == 'POST'):
        usuarioPersona.delete() # elimine el usuario/Persona
        return redirect('ListUsers') 

@login_required(login_url='/login/')
def usuariosDetail(request):
    return render(request, "usuarios/UserDetail.html")

@login_required(login_url='/login/')
def usuariosUpdate(request):
    return render(request, "usuarios/UpdateUser.html")