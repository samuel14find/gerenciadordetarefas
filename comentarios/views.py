from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings 
from comentarios.forms import FormularioComentario

def comentario(request):
    if request.method == 'POST':
        form = FormularioComentario(request.POST)
        if form.is_valid():
            nome = form.cleaned_data["nome"]
            comentario_texto = form.cleaned_data["comentario"]
            
            mensagem = f"Recebido comentário de {nome}\n\n{comentario_texto}"
            
            # Disparo do e-mail
            try:
                send_mail(
                    subject=f"Novo Comentário: {nome}",
                    message=mensagem,
                    from_email=settings.EMAIL_HOST_USER, 
                    recipient_list=['samuel.bicalho@ifmg.edu.br'],
                    fail_silently=False,
                )
            except Exception as e:
                # Opcional: registrar o erro ou avisar o usuário
                print(f"Erro ao enviar e-mail: {e}")
                
            return redirect("comentario_aceito")
    else:
        form = FormularioComentario()

    data = {
        "form": form,
    }

    return render(request, "comentario.html", data)

def comentario_aceito(request):
    data = {
        "title": "Sucesso",
        "icon": "ph-fill ph-check-circle",
        "body_class": "page-status",
        "content": """
            <h1>Comentário Enviado!</h1>
            <p>Sua mensagem foi recebida com sucesso. Agradecemos por compartilhar sua opinião conosco!</p>
        """,
        "back_url": reverse("home") # Redireciona para a home ou use reverse("comentarios")
    }
    return render(request, "geral.html", data)
