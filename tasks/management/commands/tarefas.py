from django.core.management.base import BaseCommand
from tasks.models import Tarefa
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Lista tarefas registradas com detalhes e filtro de atraso superior a 15 dias.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--atrasadas',
            action='store_true',
            help='Exibe apenas tarefas que estão em atraso há mais de 15 dias',
        )

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        limite_atraso = hoje - timedelta(days=15)
        
        if options['atrasadas']:
            # Filtro: Status diferente de CONCLUIDA e data_conclusao < (hoje - 15 dias)
            tarefas = Tarefa.objects.exclude(
                status=Tarefa.StatusChoices.CONCLUIDA
            ).filter(
                data_conclusao__lt=limite_atraso
            ).order_by('data_conclusao')
            
            self.stdout.write(self.style.WARNING('\n=== TAREFAS COM MAIS DE 15 DIAS DE ATRASO ===\n'))
        else:
            tarefas = Tarefa.objects.all().order_by('-data_conclusao')
            self.stdout.write(self.style.MIGRATE_HEADING('\n=== LISTAGEM GERAL DE TAREFAS ===\n'))

        if not tarefas.exists():
            self.stdout.write(self.style.NOTICE("Nenhuma tarefa encontrada para os critérios selecionados."))
            return

        for tarefa in tarefas:
            self.stdout.write(self.style.SUCCESS(f"Título: {tarefa.titulo}"))
            self.stdout.write(f"Descrição: {tarefa.descricao or 'Sem descrição'}")
            self.stdout.write(f"Data de Conclusão Prevista: {tarefa.data_conclusao}")
            self.stdout.write(f"Status: {tarefa.get_status_display()}")
            
            # Cálculo de dias de atraso para exibição visual
            if tarefa.data_conclusao and tarefa.status != Tarefa.StatusChoices.CONCLUIDA:
                dias_atraso = (hoje - tarefa.data_conclusao).days
                if dias_atraso > 0:
                    color_style = self.style.ERROR if dias_atraso > 15 else self.style.WARNING
                    self.stdout.write(color_style(f"Duração do Atraso: {dias_atraso} dias"))
            
            self.stdout.write("-" * 50)