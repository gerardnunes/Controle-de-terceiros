from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Local, Chamada, Presenca


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'role', 'plataforma', 'filial', 'aprovado')
    list_filter = ('role', 'aprovado', 'plataforma', 'filial')

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': (
                'role',
                'cpf',
                'telefone',
                'endereco',
                'aprovado',
                'aprovado_por',
                'aprovado_em',
                'pix',
                'plataforma',
                'filial',
            )
        }),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Local)
admin.site.register(Chamada)
admin.site.register(Presenca)