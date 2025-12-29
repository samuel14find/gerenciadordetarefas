from django.urls import path

from tasks import views

urlpatterns=[
    path('painel/', views.painel, name='painel'),
    path('lista/', views.minhas_tarefas, name='minhas_tarefas'),
    path('categoriatarefa/todas/', views.todasCategoriasDeTarefas,name="categoriastarefa"),
    path('categoriatarefa/todas/<int:categoria_id>/', views.categoriaTarefa, name="categoriatarefa"),
    #path('', views.minhas_tarefas, name='minhas_tarefas'),
    path('pagina_restrita/', views.pagina_restrita, name='pagina_restrita'),
    # Create
    path('nova/', views.criar_tarefa, name='criar_tarefa'),
    # Update (Precisa do ID)
    path('editar/<int:pk>/', views.editar_tarefa, name='editar_tarefa'),
    # Delete (Precisa do ID)
    path('deletar/<int:pk>/', views.deletar_tarefa, name='deletar_tarefa'),
    
    path('api/etapa/<int:etapa_id>/toggle/', views.atualizar_etapa, name='atualizar_etapa'),
    
    # Categorias CRUD
    path('categoriatarefa/nova/', views.criar_categoria, name='criar_categoria'),
    path('categoriatarefa/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categoriatarefa/deletar/<int:pk>/', views.deletar_categoria, name='deletar_categoria'),
    
    # Importar
    path('importar/', views.importar_tarefas, name='importar_tarefas'),
    
    # Arquivamento
    path('arquivar/<int:pk>/', views.arquivar_tarefa, name='arquivar_tarefa'),
    path('arquivadas/', views.tarefas_arquivadas, name='tarefas_arquivadas'),
    path('arquivadas/exportar/', views.exportar_tarefas_arquivadas, name='exportar_tarefas_arquivadas'),
]

