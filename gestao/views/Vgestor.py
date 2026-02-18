 #--- Gestor: Gerenciar todos os usuários ---
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, get_object_or_404, redirect, render
from flask_login import login_required

from gestao.decorators import role_required
from gestao.forms import UsuarioForm
from gestao.models import User


@login_required
@role_required('gestor')
def gestor_usuario_list(request):
    usuarios = User.objects.all().order_by('role', 'username')
    return render(request, 'gestor/usuario_list.html', {'usuarios': usuarios})

@login_required
@role_required('gestor')
def gestor_usuario_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado.')
            return redirect('gestor_usuario_list')
    else:
        form = UsuarioForm(instance=user)
    return render(request, 'gestor/usuario_form.html', {'form': form})
