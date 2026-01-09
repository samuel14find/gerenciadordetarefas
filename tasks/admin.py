from django.contrib import admin
from .models import CategoriaDeTarefa, Tarefa, Etapa, BaseConhecimento

# 1. Configuração para Categorias
@admin.register(CategoriaDeTarefa)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'criado_em') # Colunas que aparecem na lista
    search_fields = ('nome',) # Campo de busca

# 2. Configuração para Base de Conhecimento
@admin.register(BaseConhecimento)
class BaseConhecimentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario')
    search_fields = ('titulo', 'conteudo_markdown')

# 3. Configuração INLINE das Etapas
# Isso faz as etapas aparecerem DENTRO da tela da Tarefa
class EtapaInline(admin.TabularInline):
    model = Etapa
    extra = 0 # Não mostra linhas vazias extras por padrão

# 4. Configuração da Tarefa (Com as Etapas dentro)
@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    # Colunas na tabela de listagem
    list_display = ('titulo', 'categoria', 'status', 'is_foco_atual', 'data_conclusao')
    
    # Filtros laterais
    list_filter = ('status', 'is_foco_atual', 'categoria')
    
    # Barra de busca
    search_fields = ('titulo', 'descricao')
    
    # Permite editar o status clicando direto na lista (sem abrir a tarefa)
    list_editable = ('status', 'is_foco_atual')
    
    # Adiciona as etapas dentro da edição da tarefa
    inlines = [EtapaInline]
