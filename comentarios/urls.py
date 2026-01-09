from django.urls import path

from comentarios import views

urlpatterns = [
path('enviar_comentario/', views.comentario, name='comentarios'),
path('comentarios_aceito/', views.comentario_aceito, name='comentario_aceito'),
]
