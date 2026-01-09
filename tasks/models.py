from django.db import models
from django.conf import settings 

# 1. Model CategoriaDeTarefa (Já existia, mantido)
class CategoriaDeTarefa(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome da Categoria')
    cor = models.CharField(max_length=7, default='#000000', verbose_name='Cor (Código HEX)')
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='categorias_criadas',
        verbose_name='Usuário Criador'
    )
    criado_em = models.DateTimeField(verbose_name='Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria de Tarefa'
        verbose_name_plural = 'Categorias de Tarefas'
        unique_together = ('nome', 'usuario',) 

    def __str__(self):
        return f"{self.nome} (por {self.usuario.nome})"


# 2. Model BaseConhecimento (Criado antes de Tarefa para poder ser referenciado)
class BaseConhecimento(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Título do Conhecimento')
    conteudo_markdown = models.TextField(verbose_name='Conteúdo (Markdown)')
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conhecimentos',
        verbose_name='Autor'
    )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Base de Conhecimento'
        verbose_name_plural = 'Bases de Conhecimento'


# 3. Model Tarefa
class Tarefa(models.Model):
    # Definição do ENUM para o status
    class StatusChoices(models.TextChoices):
        NAO_INICIADO = 'nao_iniciado', 'Não Iniciado'
        EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
        CONCLUIDA = 'concluida', 'Concluída'

    titulo = models.CharField(max_length=255, verbose_name='Título da Tarefa')
    descricao = models.TextField(verbose_name='Descrição', blank=True, null=True)
    
    data_inicio = models.DateField(verbose_name='Data de Início', null=True, blank=True)
    data_conclusao = models.DateField(verbose_name='Data de Conclusão', null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NAO_INICIADO,
        verbose_name='Status'
    )
    
    is_foco_atual = models.BooleanField(default=False, verbose_name='Foco Atual?')
    arquivada = models.BooleanField(default=False, verbose_name='Arquivada?')
    
    # Chaves Estrangeiras (FK)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tarefas',
        verbose_name='Usuário Responsável'
    )
    
    categoria = models.ForeignKey(
        CategoriaDeTarefa,
        on_delete=models.SET_NULL, # Se deletar a categoria, a tarefa fica sem categoria (NULL)
        null=True,
        blank=True,
        related_name='tarefas',
        verbose_name='Categoria'
        )

    # Relação Muitos-para-Muitos (Substitui a necessidade de criar Model de junção manual)
    conhecimentos = models.ManyToManyField(
        BaseConhecimento,
        blank=True, # Uma tarefa pode não ter nenhum conhecimento atrelado
        related_name='tarefas_associadas',
        verbose_name='Conhecimentos Relacionados'
    )

    # Timestamps
    criada_em = models.DateTimeField(auto_now_add=True, verbose_name='Criada em')
    atualizada_em = models.DateTimeField(auto_now=True, verbose_name='Última atualização')
    
    def get_progresso(self):
        total_etapas = self.etapas.count()
        if total_etapas == 0:
            return {
                'total': 0, 
                'feitas': 0, 
                'porcentagem': 0
            }
        etapas_feitas = self.etapas.filter(concluida=True).count()
        porcentagem = int((etapas_feitas / total_etapas) * 100)
        
        return {
            'total': total_etapas,
            'feitas': etapas_feitas,
            'porcentagem': porcentagem
        }

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['-criada_em'] # Padrão: mostra as mais novas primeiro


# 4. Model Etapa
class Etapa(models.Model):
    descricao = models.CharField(max_length=255, verbose_name='Descrição da Etapa')
    concluida = models.BooleanField(default=False, verbose_name='Concluída?')
    ordem = models.PositiveIntegerField(default=0, verbose_name='Ordem de Execução')
    
    tarefa = models.ForeignKey(
        Tarefa,
        on_delete=models.CASCADE, # Se deletar a Tarefa, deleta as etapas
        related_name='etapas', # Permite acessar via: tarefa.etapas.all()
        verbose_name='Tarefa Associada'
    )

    def __str__(self):
        return f"{self.ordem} - {self.descricao}"

    class Meta:
        verbose_name = 'Etapa'
        verbose_name_plural = 'Etapas'
        ordering = ['ordem'] # Garante que sempre venha ordenado 1, 2, 3...