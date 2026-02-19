from django.urls import path
from django.contrib.auth import views as auth_views

from .views.Vgerente import (
    exportar_quinzena_excel,
    exportar_relatorio_excel,
    gerente_chamada_detail,
    relatorio
)

# Encarregado
from .views.Vencarregado import (
    usuario_list,
    usuario_create,
    usuario_aprovar,
    local_list,
    local_create,
    local_edit,
    local_delete,
    chamada_list,
    chamada_create,
    chamada_detail,
    dashboard_encarregado,
    index,
    register,
    dashboard
)

# Gerente
from .views.Vgerente import (
    gerente_chamada_detail,
)

# Gestor
from .views.Vgestor import (
    gestor_usuario_list,
    gestor_usuario_edit,
)

# Views gerais (se existirem)


urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),

    # ======================
    # AUTENTICAÇÃO
    # ======================
    path('', index, name='index'),

    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    path('register/', register, name='register'),

    # ======================
    # ENCARREGADO
    # ======================
    path(
        'encarregado/dashboard/',
        dashboard_encarregado,
        name='dashboard-encarregado'
    ),

    # Usuários
    path('encarregado/usuarios/', usuario_list, name='usuario_list'),
    path('encarregado/usuarios/novo/', usuario_create, name='usuario_create'),
    path(
        'encarregado/usuarios/<int:pk>/aprovar/',
        usuario_aprovar,
        name='usuario_aprovar'
    ),

    # Locais
    path('encarregado/locais/', local_list, name='local_list'),
    path('encarregado/locais/novo/', local_create, name='local_create'),
    path(
        'encarregado/locais/<int:pk>/editar/',
        local_edit,
        name='local_edit'
    ),
    path(
        'encarregado/locais/<int:pk>/deletar/',
        local_delete,
        name='local_delete'
    ),

    # Chamadas
    path('encarregado/chamadas/', chamada_list, name='chamada_list'),
    path('encarregado/chamadas/nova/', chamada_create, name='chamada_create'),
    path(
        'encarregado/chamadas/<int:pk>/',
        chamada_detail,
        name='chamada_detail'
    ),

    # ======================
    # GERENTE
    # ======================
    path(
        'gerente/chamadas/<int:pk>/',
        gerente_chamada_detail,
        name='gerente_chamada_detail'
    ),

    # ======================
    # GESTOR
    # ======================
    path('gestor/usuarios/', gestor_usuario_list, name='gestor_usuario_list'),
    path(
        'gestor/usuarios/<int:pk>/editar/',
        gestor_usuario_edit,
        name='gestor_usuario_edit'
    ),
    # ======================
# RELATÓRIOS
# ======================
    path('relatorios/', relatorio, name='relatorio'),
    path('exportar-quinzena/', exportar_quinzena_excel, name='exportar_quinzena_excel'),

    # ... outras URLs
    path('relatorio/', relatorio, name='relatorio'),
    path('exportar-relatorio-excel/', exportar_relatorio_excel, name='exportar_relatorio_excel'),
]

