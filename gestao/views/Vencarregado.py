from datetime import timedelta
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from pytz import timezone
from streamlit import json
from django.utils import timezone
import json

from gestao.decorators import role_required
from gestao.forms import ChamadaForm, LocalForm, UsuarioForm, UsuarioRegistroForm
from gestao.models import Chamada, Local, Presenca, User
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



def dashboard_encarregado(request):
    hoje = timezone.now().date()
    data_limite_30 = hoje - timedelta(days=30)
    
    # KPIs principais
    usuarios_totais = User.objects.filter(role='usuario').count()
    usuarios_ativos = User.objects.filter(role='usuario', aprovado=True).count()
    usuarios_pendentes = User.objects.filter(role='usuario', aprovado=False).count()
    
    chamadas_hoje = Chamada.objects.filter(data=hoje).first()
    total_presentes_hoje = chamadas_hoje.presencas.count() if chamadas_hoje else 0
    
    chamadas_pendentes_aprovacao = Chamada.objects.filter(status='pendente').count()
    
    # Frequência média últimos 30 dias
    chamadas_periodo = Chamada.objects.filter(data__gte=data_limite_30)
    total_dias_periodo = chamadas_periodo.dates('data', 'day').count()
    if total_dias_periodo > 0 and usuarios_ativos > 0:
        total_presencas_periodo = Presenca.objects.filter(chamada__data__gte=data_limite_30).count()
        frequencia_media = (total_presencas_periodo / (usuarios_ativos * total_dias_periodo)) * 100
    else:
        frequencia_media = 0
    
    # Gráfico de tendência (últimos 30 dias)
    datas = []
    presencas_dia = []
    for i in range(30):
        dia = hoje - timedelta(days=29 - i)  # para ir do mais antigo ao mais recente
        datas.append(dia.strftime('%d/%m'))
        chamada_dia = Chamada.objects.filter(data=dia).first()
        count = chamada_dia.presencas.count() if chamada_dia else 0
        presencas_dia.append(count)
    
    # Distribuição por setor (últimos 30 dias)
    setores = []
    for local in Local.objects.all():
        count = Presenca.objects.filter(
            local=local,
            chamada__data__gte=data_limite_30
        ).count()
        if count > 0:
            setores.append({'nome': local.nome, 'total': count})
    
    # Top 5 funcionários com mais presenças
    top_funcionarios = []
    for usuario in User.objects.filter(role='usuario', aprovado=True):
        presencas = Presenca.objects.filter(
            usuario=usuario,
            chamada__data__gte=data_limite_30
        ).count()
        top_funcionarios.append({
            'nome': usuario.get_full_name() or usuario.username,
            'presencas': presencas
        })
    top_funcionarios = sorted(top_funcionarios, key=lambda x: x['presencas'], reverse=True)[:5]
    
    # Chamadas pendentes de aprovação (últimas 5)
    chamadas_pendentes = Chamada.objects.filter(status='pendente').order_by('-data')[:5]
    
    # Mapa de calor (presenças por dia da semana)
    dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    calor_data = []
    for usuario in User.objects.filter(role='usuario', aprovado=True)[:10]:  # limitar para não pesar
        linha = {'nome': usuario.username, 'dias': []}
        for i in range(7):
            count = Presenca.objects.filter(
                usuario=usuario,
                chamada__data__gte=data_limite_30,
                chamada__data__week_day=i+2  # no Django, segunda=2, domingo=1
            ).count()
            linha['dias'].append(count)
        calor_data.append(linha)
    
    # Previsão para amanhã (média dos últimos 7 dias no mesmo dia da semana)
    amanha = hoje + timedelta(days=1)
    dia_semana_amanha = amanha.weekday()  # 0=segunda, 6=domingo
    presencas_media = []
    for i in range(1, 8):
        dia = amanha - timedelta(days=i*7)  # mesmo dia da semana, semanas anteriores
        chamada = Chamada.objects.filter(data=dia).first()
        if chamada:
            presencas_media.append(chamada.presencas.count())
    previsao = int(sum(presencas_media) / len(presencas_media)) if presencas_media else 0
    
    # Timeline de atividades (últimas 5 chamadas criadas)
    atividades = []
    for chamada in Chamada.objects.order_by('-criado_em')[:5]:
        atividades.append({
            'tipo': 'chamada',
            'descricao': f"Chamada de {chamada.data.strftime('%d/%m')}: {chamada.presencas.count()} presenças",
            'data': chamada.criado_em
        })
    
    context = {
        'usuarios_totais': usuarios_totais,
        'usuarios_ativos': usuarios_ativos,
        'usuarios_pendentes': usuarios_pendentes,
        'total_presentes_hoje': total_presentes_hoje,
        'chamadas_pendentes_aprovacao': chamadas_pendentes_aprovacao,
        'frequencia_media': round(frequencia_media, 1),
        'datas': json.dumps(datas),
        'presencas_dia': json.dumps(presencas_dia),
        'setores': setores,
        'top_funcionarios': top_funcionarios,
        'chamadas_pendentes': chamadas_pendentes,
        'calor_data': calor_data,
        'dias_semana': dias_semana,
        'previsao': previsao,
        'atividades': atividades,
    }
    return render(request, 'encarregado/dashboard.html', context)


@login_required
def dashboard(request):
    role = request.user.role
    if role == 'encarregado':
        return dashboard_encarregado(request)

    elif role == 'gerente':
        chamadas_pendentes = Chamada.objects.filter(status='pendente')
        return render(request, 'gerente/dashboard.html', {'chamadas': chamadas_pendentes})
    elif role == 'gestor':
        return render(request, 'gestor/dashboard.html')
    else:  # usuario
        return render(request, 'usuario/perfil.html')
