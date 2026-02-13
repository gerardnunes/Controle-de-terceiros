from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Usuários (encarregado)
    path('usuarios/', views.usuario_list, name='usuario_list'),
    path('usuarios/novo/', views.usuario_create, name='usuario_create'),
    path('usuarios/aprovar/<int:pk>/', views.usuario_aprovar, name='usuario_aprovar'),
    path('', views.redirect_dashboard, name='redirect_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),


    # Locais (encarregado)
    path('locais/', views.local_list, name='local_list'),
    path('locais/novo/', views.local_create, name='local_create'),
    path('locais/<int:pk>/editar/', views.local_edit, name='local_edit'),
    path('locais/<int:pk>/deletar/', views.local_delete, name='local_delete'),

    # Chamadas (encarregado)
    path('chamadas/', views.chamada_list, name='chamada_list'),
    path('chamadas/nova/', views.chamada_create, name='chamada_create'),
    path('chamadas/<int:pk>/', views.chamada_detail, name='chamada_detail'),

    # Gerente
    path('gerente/chamada/<int:pk>/', views.gerente_chamada_detail, name='gerente_chamada_detail'),

    # Relatórios (gerente e gestor)
    path('relatorios/', views.relatorio, name='relatorio'),

    # Gestor
    path('gestor/usuarios/', views.gestor_usuario_list, name='gestor_usuario_list'),
    path('gestor/usuarios/<int:pk>/editar/', views.gestor_usuario_edit, name='gestor_usuario_edit'),
]









