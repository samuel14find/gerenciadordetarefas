from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse # Importação necessária para retornar JSON

# Create your views here.

def creditos(request):
    conteudo = "Desenvolvido por Samuel Salvador Bicalho Pereira"
    
    return HttpResponse(conteudo, content_type="text/plain")

def sobre(request):
    conteudo = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                margin: 0;
                padding: 0;
                background-color: #f7f7f7;
            }}
            
        </style>
    </head>
    <body>
        <h1>Sobre Mim</h1>
        <p> Sistema para gerenciar minhas tarefas<p>
    </body>
    </html>
    """
    
    return HttpResponse(conteudo, content_type="text/html")
 
def versao_info(request):
    # Definimos os dados que queremos retornar em um dicionário Python
    dados_versao = {
        "nome_site": "Gerenciador de Tarefas",
        "versao": "1.0.3-beta", # Número da versão
        "data_lancamento": "2025-11-03",
        "status": "Em desenvolvimento"
    }
    
    # Retornamos o dicionário usando JsonResponse.
    # O JsonResponse serializa automaticamente o dicionário para uma string JSON
    # e define o Content-Type como "application/json".
    return JsonResponse(dados_versao)
    
def blog(request):
    data = {
        'blog':[
            "Esse é o blog para notícias e textos gerais",
            "O gerenciador de tarefas tem sua primeira página web"
        ],
    }
    
    return render(request,'blog2.html',data)
    
def landing_page(request):
    return render(request,'index.html')

def painelControleUsuarioLogado(request):
    return render(request,'dashboard.html')
    
    
