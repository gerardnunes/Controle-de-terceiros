# --- Gerente: Aprovação de Chamadas ---
from datetime import timezone
from itertools import count
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from flask_login import login_required

from gestao.decorators import role_required
from gestao.forms import RelatorioForm
from gestao.models import Chamada, User


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
                dias=count('presencas', distinct=True)
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
