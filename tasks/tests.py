from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from tasks.models import Tarefa, CategoriaDeTarefa, Etapa
from django.urls import reverse

User = get_user_model()

class TarefaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', nome='Test User', password='password')
        self.tarefa = Tarefa.objects.create(
            titulo='Test Task',
            usuario=self.user
        )

    def test_tarefa_creation(self):
        self.assertEqual(self.tarefa.titulo, 'Test Task')
        self.assertEqual(self.tarefa.usuario, self.user)
        self.assertEqual(self.tarefa.status, 'nao_iniciado')

    def test_get_progresso_empty(self):
        progresso = self.tarefa.get_progresso()
        self.assertEqual(progresso['total'], 0)
        self.assertEqual(progresso['feitas'], 0)
        self.assertEqual(progresso['porcentagem'], 0)

    def test_get_progresso_with_etapas(self):
        Etapa.objects.create(descricao='Step 1', tarefa=self.tarefa, concluida=True)
        Etapa.objects.create(descricao='Step 2', tarefa=self.tarefa, concluida=False)
        
        progresso = self.tarefa.get_progresso()
        self.assertEqual(progresso['total'], 2)
        self.assertEqual(progresso['feitas'], 1)
        self.assertEqual(progresso['porcentagem'], 50)

class CategoriaViewTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(email='user_a@example.com', nome='User A', password='password')
        self.user_b = User.objects.create_user(email='user_b@example.com', nome='User B', password='password')
        
        self.categoria_a = CategoriaDeTarefa.objects.create(nome='Cat A', usuario=self.user_a)
        self.categoria_b = CategoriaDeTarefa.objects.create(nome='Cat B', usuario=self.user_b)
        
        self.client = Client()

    def test_todas_categorias_view_security(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('categoriastarefa'))
        
        # Deve ver apenas a categoria A
        self.assertContains(response, 'Cat A')
        self.assertNotContains(response, 'Cat B')

    def test_categoria_detail_view_security_allowed(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('categoriatarefa', args=[self.categoria_a.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cat A')

    def test_categoria_detail_view_security_denied(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('categoriatarefa', args=[self.categoria_b.id]))
        self.assertEqual(response.status_code, 403)
 

