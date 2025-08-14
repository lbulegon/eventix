from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Empresa, EmpresaUser, Evento, Setor, Funcao, Vaga,
    Candidatura, AlocacaoFinal, FreelanceProfile
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Mantém os fieldsets padrão e adiciona um bloco "Perfil"
    # IMPORTANTE: não repita 'email' aqui, pois já está em "Informações pessoais"
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil", {"fields": ("role", "cpf", "phone")}),
    )

    # Na tela de criação de usuário, podemos incluir os novos campos
    # (UserAdmin.add_fieldsets padrão tem username, password1, password2)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "role", "cpf", "phone"),
        }),
    )

    list_display = ("username", "email", "role", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")

# Registros dos demais modelos
for m in [Empresa, EmpresaUser, Evento, Setor, Funcao, Vaga, Candidatura, AlocacaoFinal, FreelanceProfile]:
    admin.site.register(m)
