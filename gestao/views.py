from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.db.models import Count, Sum
from .models import User, Local, Chamada, Presenca
from .forms import UsuarioRegistroForm, UsuarioForm, LocalForm, ChamadaForm, RelatorioForm
from .decorators import role_required

# Página inicial
def index(request):
    return render(request, 'index.html')

# Registro de usuário
def register(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cadastro realizado. Aguarde aprovação do encarregado.')
            return redirect('login')
    else:
        form = UsuarioRegistroForm()
    return render(request, 'registration/register.html', {'form': form})

# Dashboard por perfil
@login_required
def dashboard(request):
    role = request.user.role
    if role == 'encarregado':
        pendentes = User.objects.filter(role='usuario', aprovado=False).count()
        chamada_hoje = Chamada.objects.filter(data=timezone.now().date(), encarregado=request.user).first()
        return render(request, 'encarregado/dashboard.html', {'pendentes': pendentes, 'chamada_hoje': chamada_hoje})
    elif role == 'gerente':
        chamadas_pendentes = Chamada.objects.filter(status='pendente')
        return render(request, 'gerente/dashboard.html', {'chamadas': chamadas_pendentes})
    elif role == 'gestor':
        return render(request, 'gestor/dashboard.html')
    else:  # usuario
        return render(request, 'usuario/perfil.html')

# --- CRUD Usuários para Encarregado ---
@login_required
@role_required('encarregado', 'gestor')
def usuario_list(request):
    usuarios = User.objects.filter(role='usuario')
    return render(request, 'encarregado/usuario_list.html', {'usuarios': usuarios})

@login_required
@role_required('encarregado', 'gestor')
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) if 'password' in form.cleaned_data else None
            # Se encarregado criar, já pode aprovar?
            # Vamos deixar aprovado se o criador for encarregado
            if request.user.role == 'encarregado':
                user.aprovado = True
                user.aprovado_por = request.user
                user.aprovado_em = timezone.now()
            user.save()
            messages.success(request, 'Usuário criado com sucesso.')
            return redirect('usuario_list')
    else:
        form = UsuarioForm()
    return render(request, 'encarregado/usuario_form.html', {'form': form})

@login_required
@role_required('encarregado')
def usuario_aprovar(request, pk):
    user = get_object_or_404(User, pk=pk, role='usuario', aprovado=False)
    user.aprovado = True
    user.aprovado_por = request.user
    user.aprovado_em = timezone.now()
    user.save()
    messages.success(request, 'Usuário aprovado.')
    return redirect('usuario_list')

# --- CRUD Locais ---
@login_required
@role_required('encarregado')
def local_list(request):
    locais = Local.objects.all()
    return render(request, 'encarregado/local_list.html', {'locais': locais})

@login_required
@role_required('encarregado')
def local_create(request):
    if request.method == 'POST':
        form = LocalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Local criado.')
            return redirect('local_list')
    else:
        form = LocalForm()
    return render(request, 'encarregado/local_form.html', {'form': form})

@login_required
@role_required('encarregado')
def local_edit(request, pk):
    local = get_object_or_404(Local, pk=pk)
    if request.method == 'POST':
        form = LocalForm(request.POST, instance=local)
        if form.is_valid():
            form.save()
            messages.success(request, 'Local atualizado.')
            return redirect('local_list')
    else:
        form = LocalForm(instance=local)
    return render(request, 'encarregado/local_form.html', {'form': form})

@login_required
@role_required('encarregado')
def local_delete(request, pk):
    local = get_object_or_404(Local, pk=pk)
    local.delete()
    messages.success(request, 'Local removido.')
    return redirect('local_list')

# --- Chamadas (Encarregado) ---
@login_required
@role_required('encarregado')
def chamada_list(request):
    chamadas = Chamada.objects.filter(encarregado=request.user).order_by('-data')
    return render(request, 'encarregado/chamada_list.html', {'chamadas': chamadas})

@login_required
@role_required('encarregado')
def chamada_create(request):
    if request.method == 'POST':
        form = ChamadaForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['data']
            # Verificar se já existe chamada para esta data
            if Chamada.objects.filter(data=data, encarregado=request.user).exists():
                messages.error(request, 'Já existe uma chamada para esta data.')
                return redirect('chamada_create')
            chamada = form.save(commit=False)
            chamada.encarregado = request.user
            chamada.save()
            # Processar presenças
            usuarios_ids = request.POST.getlist('usuarios')
            for uid in usuarios_ids:
                local_id = request.POST.get(f'local_{uid}')
                hora = request.POST.get(f'hora_{uid}')
                if local_id:
                    presenca = Presenca(
                        chamada=chamada,
                        usuario_id=uid,
                        local_id=local_id,
                        hora_chegada=hora or None
                    )
                    presenca.save()
            messages.success(request, 'Chamada registrada.')
            return redirect('chamada_list')
    else:
        form = ChamadaForm(initial={'data': timezone.now().date()})
        usuarios_aprovados = User.objects.filter(role='usuario', aprovado=True)
        locais = Local.objects.all()
        return render(request, 'encarregado/chamada_form.html', {
            'form': form,
            'usuarios': usuarios_aprovados,
            'locais': locais
        })

@login_required
@role_required('encarregado')
def chamada_detail(request, pk):
    chamada = get_object_or_404(Chamada, pk=pk, encarregado=request.user)
    presencas = chamada.presencas.all()
    return render(request, 'encarregado/chamada_detail.html', {'chamada': chamada, 'presencas': presencas})

# --- Gerente: Aprovação de Chamadas ---
@login_required
@role_required('gerente')
def gerente_chamada_detail(request, pk):
    chamada = get_object_or_404(Chamada, pk=pk)
    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'aprovar':
            chamada.status = 'aprovado'
            chamada.aprovado_por = request.user
            chamada.aprovado_em = timezone.now()
            chamada.save()
            messages.success(request, 'Chamada aprovada.')
        elif acao == 'rejeitar':
            chamada.status = 'rejeitado'
            chamada.aprovado_por = request.user
            chamada.aprovado_em = timezone.now()
            chamada.save()
            messages.success(request, 'Chamada rejeitada.')
        return redirect('dashboard')
    presencas = chamada.presencas.all()
    return render(request, 'gerente/chamada_detail.html', {'chamada': chamada, 'presencas': presencas})

# --- Relatórios (Gerente e Gestor) ---
@login_required
@role_required('gerente', 'gestor')
def relatorio(request):
    if request.method == 'POST':
        form = RelatorioForm(request.POST)
        if form.is_valid():
            inicio = form.cleaned_data['data_inicio']
            fim = form.cleaned_data['data_fim']
            # Consulta: usuários com presenças em chamadas aprovadas no período
            dados = User.objects.filter(
                role='usuario',
                presencas__chamada__status='aprovado',
                presencas__chamada__data__range=[inicio, fim]
            ).annotate(
                dias=Count('presencas', distinct=True)
            ).values('id', 'first_name', 'dias').order_by('first_name')
            # Calcular valor (dias * 100)
            for d in dados:
                d['valor'] = d['dias'] * 100
            return render(request, 'gerente/relatorio_result.html', {'dados': dados, 'inicio': inicio, 'fim': fim})
    else:
        form = RelatorioForm()
    # Para gestor, pode ter template diferente? Usaremos o mesmo mas com verificação de role no template se necessário
    template = 'gerente/relatorio_form.html' if request.user.role == 'gerente' else 'gestor/relatorio_form.html'
    return render(request, template, {'form': form})

# --- Gestor: Gerenciar todos os usuários ---
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


from django.shortcuts import redirect

@login_required
def redirect_dashboard(request):
    user = request.user

    if user.role == 'gestor':
        return redirect('gestor_dashboard')

    elif user.role == 'gerente':
        return redirect('gerente_dashboard')

    elif user.role == 'encarregado':
        return redirect('encarregado_dashboard')

    else:
        return redirect('home')
