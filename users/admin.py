from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuarios

# Precisamos criar uma classe customizada herdando de UserAdmin
# para lidar com o fato de usarmos 'email' em vez de 'username'
@admin.register(Usuarios)
class UsuarioAdmin(BaseUserAdmin):
    # A ordem das colunas na listagem
    list_display = ('email', 'nome', 'is_admin', 'is_staff')
    
    # Filtros laterais
    list_filter = ('is_admin',)
    
    # Campos de busca
    search_fields = ('email', 'nome')
    
    # Configuração de ordenação
    ordering = ('email',)
    
    # Como não temos 'username', definimos como ordenar e filtrar
    filter_horizontal = ()
    
    # O fieldsets define como o formulário de edição aparece
    # Tivemos que redefinir porque o padrão espera um campo 'username' que não temos
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    # Configuração para a tela de "Adicionar Usuário"
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password', 'confirm_password'),
        }),
    )