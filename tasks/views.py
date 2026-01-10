from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Tarefa, CategoriaDeTarefa, Etapa # Importe seus models
from .forms import TarefaForm, EtapaFormSet, CategoriaForm, CSVUploadForm # Importe os forms criados acima
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone # Importante para lidar com datas
import json
import csv
import io


# Create your views here.

@login_required
def minhas_tarefas(request):
    """ View para a Lista de Tarefas """
    # FILTRO MÁGICO: usuario=request.user
    # Otimização: select_related para FK e prefetch_related para ManyToMany (etapas)
    tarefas = Tarefa.objects.filter(usuario=request.user, arquivada=False)\
                            .select_related('categoria')\
                            .prefetch_related('etapas')
    
    data = {
        'tarefas': tarefas
    }
    return render(request, "tarefas.html", data)
# CREATE (Criar Tarefa)
@login_required
def criar_tarefa(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        formset = EtapaFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            tarefa = form.save(commit=False)
            tarefa.usuario = request.user
            tarefa.save()
            
            formset.instance = tarefa
            formset.save()
            
            # Redireciona para sua rota 'lista/' cujo nome é 'minhas_tarefas'
            return redirect('minhas_tarefas') 
    else:
        form = TarefaForm()
        formset = EtapaFormSet()
    
    return render(request, 'tarefa_form.html', {
        'form': form, 
        'formset': formset,
        'titulo_pagina': 'Nova Tarefa'
    })
# UPDATE (Editar Tarefa)
@login_required
def editar_tarefa(request, pk):
    # Garante que só o dono pode editar
    tarefa = get_object_or_404(Tarefa, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa)
        formset = EtapaFormSet(request.POST, instance=tarefa)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('minhas_tarefas')
    else:
        form = TarefaForm(instance=tarefa)
        formset = EtapaFormSet(instance=tarefa)
    
    return render(request, 'tarefa_form.html', {
        'form': form, 
        'formset': formset,
        'titulo_pagina': f'Editar: {tarefa.titulo}'
    })
# DELETE (Excluir Tarefa)
@login_required
def deletar_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        tarefa.delete()
        return redirect('minhas_tarefas')
        
    return render(request, 'tarefa_confirm_delete.html', {'tarefa': tarefa})

def categoriaTarefa(request, categoria_id):
    categoria = get_object_or_404(CategoriaDeTarefa, id=categoria_id)
    
    # Segurança: Verificar se a categoria pertence ao usuário logado
    if categoria.usuario != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Você não tem permissão para visualizar esta categoria.")

    data = {
        "CategoriaTarefa": categoria,
        "tarefas": categoria.tarefas.all().prefetch_related('etapas')
    }
    
    return render(request, "categoria_de_tarefa.html", data)

@login_required
def todasCategoriasDeTarefas(request):
    todasCategoriasOrdenadaPorData = CategoriaDeTarefa.objects.filter(usuario=request.user).order_by('criado_em')
    
    paginator = Paginator(todasCategoriasOrdenadaPorData, 6) # 2 itens por página
    
    page_number = request.GET.get('page') # Pega o parâmetro da URL
    
    # get_page lida automaticamente com:
    # - Valores não inteiros (retorna a pág 1)
    # - Valores vazios (retorna a pág 1)
    # - Valores maiores que o máx de páginas (retorna a última pág)
    page_obj = paginator.get_page(page_number)
    
    data = {
        # Nota: Quando usamos get_page, o próprio objeto 'page_obj' 
        # já serve como a lista para o loop 'for'
        'todas': page_obj, 
        'page': page_obj,
    }
    
    return render(request, "todasCategoriasTarefa.html", data)

@login_required
def painel(request):
    # 1. Pegamos a data de hoje (sem as horas)
    hoje_data = timezone.now().date()
    
    # 2. Base: Pegamos todas as tarefas do usuário (não arquivadas)
    tarefas_base = Tarefa.objects.filter(usuario=request.user, arquivada=False).prefetch_related('etapas', 'categoria')
    
    # --- CÁLCULOS E LISTAS ---
    
    # Total Geral
    total = tarefas_base.count()
    
    # Para Hoje: Vencem hoje E não estão concluídas
    tarefas_hoje_list = tarefas_base.filter(
        data_conclusao=hoje_data
    ).exclude(
        status=Tarefa.StatusChoices.CONCLUIDA
    )
    
    # Foco Atual: Marcadas com focus_atual E não concluídas
    tarefas_foco_list = tarefas_base.filter(
        is_foco_atual=True
    ).exclude(
        status=Tarefa.StatusChoices.CONCLUIDA
    )
    
    # Atrasadas: Vencimento menor que hoje E não estão concluídas
    tarefas_atrasadas_list = tarefas_base.filter(
        data_conclusao__lt=hoje_data
    ).exclude(
        status=Tarefa.StatusChoices.CONCLUIDA
    )
    
    # Concluídas
    tarefas_concluidas_list = tarefas_base.filter(
        status=Tarefa.StatusChoices.CONCLUIDA
    )

    context = {
        'total': total,
        'hoje': tarefas_hoje_list.count(),
        'foco': tarefas_foco_list.count(),
        'atrasadas': tarefas_atrasadas_list.count(),
        'concluidas': tarefas_concluidas_list.count(),
        'tarefas_hoje_list': tarefas_hoje_list,
        'tarefas_foco_list': tarefas_foco_list,
        'tarefas_atrasadas_list': tarefas_atrasadas_list,
        'tarefas_concluidas_list': tarefas_concluidas_list,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def pagina_restrita(request):
    
    data = {
        'title': 'Página Restrita',
        'content': '<h1> Você está logado!</h1>',
    }
    
    return render(request, "geral.html", data)

@csrf_exempt 
def atualizar_etapa(request, etapa_id):
    if request.method == 'POST':
        etapa = Etapa.objects.get(id=etapa_id)
        
        # 1. Alterna o status da etapa (se estava True vira False, e vice-versa)
        etapa.concluida = not etapa.concluida
        etapa.save()
        
        # 2. Verifica a Tarefa Pai
        tarefa = etapa.tarefa
        todas_etapas = tarefa.etapas.all()
        
        # Lógica: Se tem etapas e TODAS estão concluídas -> Concluída
        # Caso contrário, se tem pelo menos uma feita -> Em Andamento
        # Se nenhuma feita -> Não Iniciado
        
        todas_concluidas = all(e.concluida for e in todas_etapas)
        alguma_concluida = any(e.concluida for e in todas_etapas)
        
        novo_status = tarefa.status # status atual
        
        if todas_etapas.exists():
            if todas_concluidas:
                novo_status = Tarefa.StatusChoices.CONCLUIDA
            elif alguma_concluida:
                novo_status = Tarefa.StatusChoices.EM_ANDAMENTO
            else:
                novo_status = Tarefa.StatusChoices.NAO_INICIADO
        
        # Salva apenas se mudou
        if tarefa.status != novo_status:
            tarefa.status = novo_status
            tarefa.save()
            
        return JsonResponse({
            'status': 'sucesso', 
            'etapa_concluida': etapa.concluida,
            'tarefa_status': tarefa.get_status_display(),
            'tarefa_status_code': tarefa.status,
            'tarefa_id': tarefa.id
        })
        
    return JsonResponse({'status': 'erro'}, status=400)

# CRUD Categorias

@login_required
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()
            return redirect('categoriastarefa')
    else:
        form = CategoriaForm()
    
    return render(request, 'categoria_form.html', {
        'form': form,
        'titulo_pagina': 'Nova Categoria'
    })

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(CategoriaDeTarefa, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('categoriastarefa')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'categoria_form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {categoria.nome}'
    })


@login_required
def deletar_categoria(request, pk):
    categoria = get_object_or_404(CategoriaDeTarefa, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        categoria.delete()
        return redirect('categoriastarefa')
        
    return render(request, 'categoria_confirm_delete.html', {'categoria': categoria})


@login_required
def importar_tarefas(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['arquivo_csv']
            
            if not csv_file.name.endswith('.csv'):
                from django.contrib import messages
                messages.error(request, 'O arquivo deve ser um CSV (.csv).')
                return render(request, 'importar_tarefas.html', {'form': form})

            try:
                decoded_file = csv_file.read().decode('utf-8')
            except UnicodeDecodeError:
                from django.contrib import messages
                messages.error(request, 'Erro de codificação no arquivo. Certifique-se que é um CSV UTF-8.')
                return render(request, 'importar_tarefas.html', {'form': form})
            
            lines = decoded_file.splitlines()
            if not lines:
                from django.contrib import messages
                messages.warning(request, 'O arquivo está vazio.')
                return redirect('importar_tarefas')

            # Detecção de delimitador mais robusta
            first_line = lines[0]
            if ';' in first_line:
                delimiter = ';'
            else:
                delimiter = ','

            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string, delimiter=delimiter)
            
            # Normalizar chaves do header para remover espaços ou BOM
            if reader.fieldnames:
                reader.fieldnames = [name.strip() for name in reader.fieldnames]

            from datetime import datetime
            
            tasks_created = 0

            def parse_date(date_str):
                if not date_str or not date_str.strip():
                    return None
                date_str = date_str.strip()
                formats = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d']
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                return None

            for row in reader:
                if 'titulo' not in row:
                    continue

                titulo_raw = row['titulo']
                if not titulo_raw:
                    continue
                
                titulo = titulo_raw.strip()
                descricao = row.get('descricao', '').strip()
                
                data_inicio = parse_date(row.get('data_inicio'))
                data_conclusao = parse_date(row.get('data_conclusao'))
                
                status_raw = row.get('status', 'nao_iniciado')
                if status_raw is None: status_raw = 'nao_iniciado'
                status = status_raw.strip()

                valid_statuses = [choice[0] for choice in Tarefa.StatusChoices.choices]
                if status not in valid_statuses:
                    status = 'nao_iniciado'

                categoria_nome = row.get('categoria')
                categoria = None
                if categoria_nome and categoria_nome.strip():
                    categoria, _ = CategoriaDeTarefa.objects.get_or_create(
                        nome=categoria_nome.strip(), 
                        usuario=request.user,
                        defaults={'cor': '#000000'}
                    )

                tarefa = Tarefa.objects.create(
                    usuario=request.user,
                    titulo=titulo,
                    descricao=descricao,
                    data_inicio=data_inicio,
                    data_conclusao=data_conclusao,
                    status=status,
                    categoria=categoria
                )
                
                # Importar Etapas
                etapas_str = row.get('etapas')
                if etapas_str and etapas_str.strip():
                    # Separador de etapas é o PIPE |
                    lista_etapas = etapas_str.split('|')
                    for i, descricao_etapa in enumerate(lista_etapas):
                        descricao_limpa = descricao_etapa.strip()
                        if descricao_limpa:
                            Etapa.objects.create(
                                tarefa=tarefa,
                                descricao=descricao_limpa,
                                ordem=i
                            )
                            # Removing info_ordem above as it was a placeholder thought, using 'ordem' as per model.

                tasks_created += 1
            
            from django.contrib import messages
            if tasks_created > 0:
                messages.success(request, f'{tasks_created} tarefas importadas com sucesso!')
            else:
                messages.warning(request, 'Nenhuma tarefa foi importada. Verifique o formato do arquivo (cabeçalhos).')

            return redirect('minhas_tarefas')
    else:
        form = CSVUploadForm()
    
    return render(request, 'importar_tarefas.html', {'form': form})


@login_required
def arquivar_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, usuario=request.user)
    if tarefa.status == Tarefa.StatusChoices.CONCLUIDA:
        tarefa.arquivada = True
        tarefa.save()
    return redirect('minhas_tarefas')

@login_required
def tarefas_arquivadas(request):
    tarefas = Tarefa.objects.filter(usuario=request.user, arquivada=True).order_by('-atualizada_em')
    return render(request, 'tarefas_arquivadas.html', {'tarefas': tarefas})

@login_required
def exportar_tarefas_arquivadas(request):
    tarefas = Tarefa.objects.filter(usuario=request.user, arquivada=True)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tarefas_arquivadas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Título', 'Descrição', 'Data de Conclusão', 'Categoria'])
    
    for tarefa in tarefas:
        writer.writerow([
            tarefa.titulo, 
            tarefa.descricao, 
            tarefa.atualizada_em.strftime('%d/%m/%Y %H:%M'), 
            tarefa.categoria.nome if tarefa.categoria else 'Sem Categoria'
        ])
        
    return response


