from rest_framework import serializers
from app_eventos.models import User, Empresa, EmpresaUser, FreelanceProfile

class SignupFreelancerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "cpf", "phone"]

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            cpf=validated_data.get("cpf"),
            phone=validated_data.get("phone"),
            role="FREELANCER",
        )
        user.set_password(validated_data["password"])
        user.save()
        FreelanceProfile.objects.get_or_create(user=user)
        return user


class SignupEmpresaSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    empresa_descricao = serializers.CharField()
    empresa_cnpj = serializers.CharField()
    empresa_email = serializers.EmailField()

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role="EMPREGADOR",
        )
        user.set_password(validated_data["password"])
        user.save()

        empresa = Empresa.objects.create(
            descricao=validated_data["empresa_descricao"],
            cnpj=validated_data["empresa_cnpj"],
            email=validated_data["empresa_email"],
            status="A",
        )
        EmpresaUser.objects.create(empresa=empresa, user=user, papel="OWNER")
        return user
