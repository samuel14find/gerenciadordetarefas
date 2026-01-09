from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

# Classe obrigatória para gerenciar a criação de usuários e superusuários
class UsuarioManager(BaseUserManager):
    """Gerenciador para o modelo Usuarios, onde o e-mail é o identificador único."""
    def create_user(self, email, nome, password=None):
        if not email:
            raise ValueError('O e-mail deve ser informado para o login.')

        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome)
        
        # 'set_password' trata a geração da senha_hash automaticamente
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None):
        user = self.create_user(email, nome, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Modelo customizado de Usuário
class Usuarios(AbstractBaseUser, PermissionsMixin):
    # Campos solicitados
    nome = models.CharField(max_length=255)
    email = models.EmailField(
        verbose_name='e-mail', 
        max_length=255, 
        unique=True # Requisito de unicidade
    )
    # 'senha_hash' é representado pelo campo 'password' herdado de AbstractBaseUser
    criado_em = models.DateTimeField(
        verbose_name='Criado em', 
        auto_now_add=True # Preenche automaticamente na criação
    ) 

    # Campos de controle padrão (necessários para AbstractBaseUser/PermissionsMixin)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UsuarioManager() # Define o gerenciador customizado

    # Define o campo que será usado como identificador de login
    USERNAME_FIELD = 'email' 
    
    # Define os campos que serão solicitados ao criar um usuário via 'createsuperuser'
    REQUIRED_FIELDS = ['nome'] 

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuarios'