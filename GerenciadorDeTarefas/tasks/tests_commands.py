from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from tasks.models import Tarefa
from django.contrib.auth import get_user_model

User = get_user_model()

class TarefasCommandTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            nome='Admin User',
            password='password123'
        )
        self.hoje = timezone.now().date()
        
        # 1. Tarefa muito atrasada (mais de 15 dias)
        self.tarefa_muito_atrasada = Tarefa.objects.create(
            titulo='Tarefa Muito Atrasada',
            descricao='Esta tarefa está bem atrasada',
            data_conclusao=self.hoje - timedelta(days=20),
            status=Tarefa.StatusChoices.NAO_INICIADO,
            usuario=self.user
        )
        
        # 2. Tarefa pouco atrasada (menos de 15 dias)
        self.tarefa_pouco_atrasada = Tarefa.objects.create(
            titulo='Tarefa Pouco Atrasada',
            descricao='Esta tarefa está pouco atrasada',
            data_conclusao=self.hoje - timedelta(days=5),
            status=Tarefa.StatusChoices.EM_ANDAMENTO,
            usuario=self.user
        )
        
        # 3. Tarefa concluída (mesmo que com data antiga, não deve aparecer no filtro de atrasadas)
        self.tarefa_concluida = Tarefa.objects.create(
            titulo='Tarefa Concluída Antiga',
            data_conclusao=self.hoje - timedelta(days=30),
            status=Tarefa.StatusChoices.CONCLUIDA,
            usuario=self.user
        )

    def test_tarefas_listagem_geral(self):
        """Testa se a listagem geral exibe todas as tarefas."""
        out = StringIO()
        call_command('tarefas', stdout=out)
        output = out.getvalue()
        
        self.assertIn('=== LISTAGEM GERAL DE TAREFAS ===', output)
        self.assertIn('Tarefa Muito Atrasada', output)
        self.assertIn('Tarefa Pouco Atrasada', output)
        self.assertIn('Tarefa Concluída Antiga', output)

    def test_tarefas_listagem_atrasadas(self):
        """Testa se o filtro --atrasadas funciona corretamente."""
        out = StringIO()
        call_command('tarefas', '--atrasadas', stdout=out)
        output = out.getvalue()
        
        self.assertIn('=== TAREFAS COM MAIS DE 15 DIAS DE ATRASO ===', output)
        self.assertIn('Tarefa Muito Atrasada', output)
        
        # Não deve conter a tarefa pouco atrasada
        self.assertNotIn('Tarefa Pouco Atrasada', output)
        
        # Não deve conter a tarefa concluída 
        self.assertNotIn('Tarefa Concluída Antiga', output)
        
        # Deve mostrar a duração do atraso
        self.assertIn('Duração do Atraso: 20 dias', output)

    def test_tarefas_no_results(self):
        """Testa a mensagem quando não há tarefas que correspondam ao filtro."""
        # Limpa as tarefas
        Tarefa.objects.all().delete()
        
        out = StringIO()
        call_command('tarefas', '--atrasadas', stdout=out)
        output = out.getvalue()
        
        self.assertIn('Nenhuma tarefa encontrada para os critérios selecionados.', output)
