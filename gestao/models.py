from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('gestor', 'Gestor'),
        ('gerente', 'Gerente'),
        ('encarregado', 'Encarregado'),
        ('usuario', 'Usuário'),
        ('administrador', 'Administrador'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='usuario')
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.TextField(blank=True)
    aprovado = models.BooleanField(default=False)  # apenas para usuários
    aprovado_por = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='aprovados')
    aprovado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Local(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class Chamada(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    )
    data = models.DateField()
    encarregado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chamadas_criadas')
    criado_em = models.DateTimeField(auto_now_add=True)
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chamadas_aprovadas')
    aprovado_em = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')

    class Meta:
        unique_together = ['data', 'encarregado']  # um encarregado só pode ter uma chamada por dia

    def __str__(self):
        return f"Chamada {self.data} - {self.encarregado}"

class Presenca(models.Model):
    chamada = models.ForeignKey(Chamada, on_delete=models.CASCADE, related_name='presencas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presencas')
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    hora_chegada = models.TimeField(null=True, blank=True)
    hora_saida = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ['chamada', 'usuario']  # um usuário só pode estar uma vez por chamada

    def __str__(self):
        return f"{self.usuario} em {self.chamada.data}"