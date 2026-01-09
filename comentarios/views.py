from django.core.mail import send_mail
from django.shortcuts import render, redirect
from comentarios.forms import FormularioComentario

def comentario(request):
    # Lógica de processamento do formulário
    if request.method == 'POST':
        form = FormularioComentario(request.POST)
        if form.is_valid():
            nome = form.cleaned_data["nome"]
            comentario = form.cleaned_data["comentario"]
            
            # CORREÇÃO 1: Nome da variável padronizado
            mensagem = f"""\
            Received comment from {nome}\n\n
            {comentario}
            """
            
            # CORREÇÃO 1: Usando 'mensagem' corretamente aqui
            send_mail(
                "Received comment", 
                mensagem, 
                "admin@example.com", 
                ["admin@example.com"],
                fail_silently=False
            )
            return redirect("comentario_aceito")
    else:
        # Se for GET, cria o formulário vazio
        form = FormularioComentario()

    # CORREÇÃO 2: O dicionário context (data) agora é definido
    # fora do if/else, garantindo que ele exista tanto no GET quanto no POST (em caso de erro de validação)
    data = {
        "form": form,
    }

    return render(request, "comentario.html", data)

def comentario_aceito(request):
    data = {
        "content": """
            <h1> Comentário Aceito </h1>
            <p> Obrigado por enviar um comentário para o meu <i>Gerenciador de Tarefas</i> </p>
        """
    }
    return render(request, "geral.html", data)



# Create your views here.
