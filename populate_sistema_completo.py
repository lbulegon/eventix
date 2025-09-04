#!/usr/bin/env python
"""
Script para popular o sistema completo com dados de exemplo
Inclui: empresa contratante, evento, local, setores, equipamentos, pessoas e vagas
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import (
    EmpresaContratante, Empresa, TipoEmpresa, LocalEvento, Evento, 
    SetorEvento, Equipamento, CategoriaEquipamento, EquipamentoSetor,
    Freelance, User, TipoFuncao, Funcao, Vaga
)

def criar_empresa_contratante():
    """Cria a empresa contratante principal"""
    print("🏢 Criando empresa contratante...")
    
    empresa, created = EmpresaContratante.objects.get_or_create(
        cnpj='12.345.678/0001-90',
        defaults={
            'nome': 'Eventos Premium LTDA',
            'razao_social': 'Eventos Premium Produções e Serviços LTDA',
            'nome_fantasia': 'Eventos Premium',
            'email': 'contato@eventospremium.com',
            'telefone': '(11) 99999-9999',
            'cep': '01234-567',
            'logradouro': 'Rua das Flores',
            'numero': '123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'uf': 'SP',
            'data_vencimento': date.today() + timedelta(days=365),
            'plano_contratado': 'Premium',
            'valor_mensal': 1999.99,
            'ativo': True
        }
    )
    
    if created:
        print(f"✅ Empresa '{empresa.nome_fantasia}' criada com sucesso!")
    else:
        print(f"ℹ️  Empresa '{empresa.nome_fantasia}' já existe.")
    
    return empresa

def criar_tipos_empresa():
    """Cria os tipos de empresa"""
    print("📋 Criando tipos de empresa...")
    
    tipos_data = [
        {'nome': 'Produtora', 'descricao': 'Empresas produtoras de eventos'},
        {'nome': 'Contratante de Mão de Obra', 'descricao': 'Empresas que contratam freelancers'},
        {'nome': 'Proprietária de Local', 'descricao': 'Empresas proprietárias de locais de eventos'},
        {'nome': 'Fornecedora', 'descricao': 'Empresas fornecedoras de serviços e equipamentos'},
    ]
    
    tipos_criados = []
    for tipo_data in tipos_data:
        tipo, created = TipoEmpresa.objects.get_or_create(
            nome=tipo_data['nome'],
            defaults=tipo_data
        )
        if created:
            print(f"✅ Tipo de empresa criado: {tipo.nome}")
        tipos_criados.append(tipo)
    
    return tipos_criados

def criar_empresas_parceiras(empresa_contratante, tipos_empresa):
    """Cria empresas parceiras"""
    print("🤝 Criando empresas parceiras...")
    
    empresas_data = [
        {
            'nome': 'Centro de Convenções São Paulo',
            'cnpj': '98.765.432/0001-10',
            'tipo_empresa': tipos_empresa[2],  # Proprietária de Local
            'telefone': '(11) 3333-4444',
            'email': 'contato@centroconvencoes.com'
        },
        {
            'nome': 'Som & Luz Produções',
            'cnpj': '11.222.333/0001-44',
            'tipo_empresa': tipos_empresa[0],  # Produtora
            'telefone': '(11) 5555-6666',
            'email': 'contato@someluz.com'
        },
        {
            'nome': 'Equipamentos Premium',
            'cnpj': '44.555.666/0001-77',
            'tipo_empresa': tipos_empresa[3],  # Fornecedora
            'telefone': '(11) 7777-8888',
            'email': 'contato@equipamentospremium.com'
        }
    ]
    
    empresas_criadas = []
    for empresa_data in empresas_data:
        empresa_data['empresa_contratante'] = empresa_contratante
        empresa, created = Empresa.objects.get_or_create(
            cnpj=empresa_data['cnpj'],
            empresa_contratante=empresa_contratante,
            defaults=empresa_data
        )
        if created:
            print(f"✅ Empresa parceira criada: {empresa.nome}")
        empresas_criadas.append(empresa)
    
    return empresas_criadas

def criar_local_evento(empresa_local):
    """Cria um local de evento"""
    print("🏟️ Criando local de evento...")
    
    local, created = LocalEvento.objects.get_or_create(
        nome='Centro de Convenções São Paulo - Auditório Principal',
        defaults={
            'endereco': 'Av. Paulista, 1000 - Bela Vista, São Paulo - SP',
            'capacidade': 500,
            'empresa_proprietaria': empresa_local,
            'ativo': True
        }
    )
    
    if created:
        print(f"✅ Local criado: {local.nome}")
    else:
        print(f"ℹ️  Local já existe: {local.nome}")
    
    return local

def criar_evento(empresa_contratante, local, empresa_produtora):
    """Cria um evento"""
    print("🎪 Criando evento...")
    
    evento, created = Evento.objects.get_or_create(
        nome='Festival de Música Eletrônica 2024',
        empresa_contratante=empresa_contratante,
        defaults={
            'data_inicio': date.today() + timedelta(days=30),
            'data_fim': date.today() + timedelta(days=30),
            'descricao': 'Festival de música eletrônica com DJs nacionais e internacionais, food trucks e muito mais!',
            'local': local,
            'empresa_produtora': empresa_produtora,
            'empresa_contratante_mao_obra': empresa_produtora,
            'ativo': True
        }
    )
    
    if created:
        print(f"✅ Evento criado: {evento.nome}")
    else:
        print(f"ℹ️  Evento já existe: {evento.nome}")
    
    return evento

def criar_setores(evento):
    """Cria setores para o evento"""
    print("🏗️ Criando setores...")
    
    setores_data = [
        {
            'nome': 'Palco Principal',
            'descricao': 'Palco principal onde acontecerão as apresentações dos DJs'
        },
        {
            'nome': 'Área VIP',
            'descricao': 'Área VIP com vista privilegiada e serviços exclusivos'
        },
        {
            'nome': 'Food Court',
            'descricao': 'Área com food trucks e praça de alimentação'
        },
        {
            'nome': 'Entrada e Recepção',
            'descricao': 'Área de entrada, credenciamento e recepção dos convidados'
        }
    ]
    
    setores_criados = []
    for setor_data in setores_data:
        setor_data['evento'] = evento
        setor, created = SetorEvento.objects.get_or_create(
            nome=setor_data['nome'],
            evento=evento,
            defaults=setor_data
        )
        if created:
            print(f"✅ Setor criado: {setor.nome}")
        setores_criados.append(setor)
    
    return setores_criados

def criar_categorias_equipamentos(empresa_contratante):
    """Cria categorias de equipamentos"""
    print("📦 Criando categorias de equipamentos...")
    
    categorias_data = [
        {'nome': 'Som', 'descricao': 'Equipamentos de áudio e sonorização'},
        {'nome': 'Iluminação', 'descricao': 'Equipamentos de iluminação cênica'},
        {'nome': 'Estrutura', 'descricao': 'Estruturas metálicas e palcos'},
        {'nome': 'Segurança', 'descricao': 'Equipamentos de segurança e monitoramento'},
    ]
    
    categorias_criadas = []
    for categoria_data in categorias_data:
        categoria_data['empresa_contratante'] = empresa_contratante
        categoria, created = CategoriaEquipamento.objects.get_or_create(
            nome=categoria_data['nome'],
            empresa_contratante=empresa_contratante,
            defaults=categoria_data
        )
        if created:
            print(f"✅ Categoria criada: {categoria.nome}")
        categorias_criadas.append(categoria)
    
    return categorias_criadas

def criar_equipamentos(empresa_contratante, empresa_fornecedora, categorias):
    """Cria equipamentos"""
    print("🔧 Criando equipamentos...")
    
    equipamentos_data = [
        # Som
        {'codigo_patrimonial': 'SOM001', 'categoria': categorias[0], 'marca': 'JBL', 'modelo': 'SRX835P', 'descricao': 'Caixa de som ativa 15"', 'estado_conservacao': 'excelente'},
        {'codigo_patrimonial': 'SOM002', 'categoria': categorias[0], 'marca': 'Yamaha', 'modelo': 'MG16XU', 'descricao': 'Mesa de som digital 16 canais', 'estado_conservacao': 'bom'},
        {'codigo_patrimonial': 'SOM003', 'categoria': categorias[0], 'marca': 'Shure', 'modelo': 'SM58', 'descricao': 'Microfone dinâmico', 'estado_conservacao': 'excelente'},
        
        # Iluminação
        {'codigo_patrimonial': 'ILU001', 'categoria': categorias[1], 'marca': 'Chauvet', 'modelo': 'Intimidator Spot 355', 'descricao': 'Moving head LED', 'estado_conservacao': 'bom'},
        {'codigo_patrimonial': 'ILU002', 'categoria': categorias[1], 'marca': 'American DJ', 'modelo': 'Mega Tripar Profile', 'descricao': 'Par LED RGB', 'estado_conservacao': 'excelente'},
        
        # Estrutura
        {'codigo_patrimonial': 'EST001', 'categoria': categorias[2], 'marca': 'Global Truss', 'modelo': 'GT-34', 'descricao': 'Truss de alumínio 34mm', 'estado_conservacao': 'bom'},
        {'codigo_patrimonial': 'EST002', 'categoria': categorias[2], 'marca': 'Prolyte', 'modelo': 'H30V', 'descricao': 'Palco modular 1x1m', 'estado_conservacao': 'excelente'},
        
        # Segurança
        {'codigo_patrimonial': 'SEG001', 'categoria': categorias[3], 'marca': 'Hikvision', 'modelo': 'DS-2CD2143G0-I', 'descricao': 'Câmera IP 4MP', 'estado_conservacao': 'bom'},
    ]
    
    equipamentos_criados = []
    for equip_data in equipamentos_data:
        equip_data['empresa_contratante'] = empresa_contratante
        equip_data['empresa_proprietaria'] = empresa_fornecedora
        equip, created = Equipamento.objects.get_or_create(
            codigo_patrimonial=equip_data['codigo_patrimonial'],
            empresa_contratante=empresa_contratante,
            defaults=equip_data
        )
        if created:
            print(f"✅ Equipamento criado: {equip.codigo_patrimonial} - {equip.marca} {equip.modelo}")
        equipamentos_criados.append(equip)
    
    return equipamentos_criados

def criar_equipamentos_setor(setores, equipamentos):
    """Associa equipamentos aos setores"""
    print("🔗 Associando equipamentos aos setores...")
    
    # Palco Principal - Som e Iluminação
    palco_principal = setores[0]
    equipamentos_palco = equipamentos[:5]  # Som e iluminação
    
    for equip in equipamentos_palco:
        equip_setor, created = EquipamentoSetor.objects.get_or_create(
            equipamento=equip,
            setor=palco_principal,
            defaults={'quantidade_necessaria': 2, 'observacoes': 'Equipamento para palco principal'}
        )
        if created:
            print(f"✅ Equipamento {equip.codigo_patrimonial} associado ao {palco_principal.nome}")
    
    # Área VIP - Estrutura
    area_vip = setores[1]
    equipamentos_vip = equipamentos[5:7]  # Estrutura
    
    for equip in equipamentos_vip:
        equip_setor, created = EquipamentoSetor.objects.get_or_create(
            equipamento=equip,
            setor=area_vip,
            defaults={'quantidade_necessaria': 1, 'observacoes': 'Estrutura para área VIP'}
        )
        if created:
            print(f"✅ Equipamento {equip.codigo_patrimonial} associado ao {area_vip.nome}")

def criar_freelancers():
    """Cria freelancers"""
    print("👥 Criando freelancers...")
    
    freelancers_data = [
        {
            'username': 'joao_som',
            'email': 'joao@som.com',
            'nome_completo': 'João Silva',
            'telefone': '(11) 99999-1111',
            'cpf': '123.456.789-01',
            'especialidade': 'Técnico de Som'
        },
        {
            'username': 'maria_ilum',
            'email': 'maria@ilum.com',
            'nome_completo': 'Maria Santos',
            'telefone': '(11) 99999-2222',
            'cpf': '987.654.321-02',
            'especialidade': 'Técnico de Iluminação'
        },
        {
            'username': 'pedro_seg',
            'email': 'pedro@seg.com',
            'nome_completo': 'Pedro Costa',
            'telefone': '(11) 99999-3333',
            'cpf': '456.789.123-03',
            'especialidade': 'Segurança'
        },
        {
            'username': 'ana_atend',
            'email': 'ana@atend.com',
            'nome_completo': 'Ana Oliveira',
            'telefone': '(11) 99999-4444',
            'cpf': '789.123.456-04',
            'especialidade': 'Atendimento'
        }
    ]
    
    freelancers_criados = []
    for freelancer_data in freelancers_data:
        # Criar usuário
        user, created = User.objects.get_or_create(
            username=freelancer_data['username'],
            defaults={
                'email': freelancer_data['email'],
                'tipo_usuario': 'freelancer',
                'ativo': True
            }
        )
        
        if created:
            user.set_password('123456')  # Senha padrão
            user.save()
        
        # Criar perfil de freelancer
        freelance, created = Freelance.objects.get_or_create(
            usuario=user,
            defaults={
                'nome_completo': freelancer_data['nome_completo'],
                'telefone': freelancer_data['telefone'],
                'cpf': freelancer_data['cpf'],
                'habilidades': freelancer_data['especialidade'],
                'cadastro_completo': True
            }
        )
        
        if created:
            print(f"✅ Freelancer criado: {freelance.nome_completo}")
        freelancers_criados.append(freelance)
    
    return freelancers_criados

def criar_vagas(setores, funcoes, freelancers):
    """Cria vagas para os setores"""
    print("💼 Criando vagas...")
    
    # Mapear funções por tipo
    funcoes_por_tipo = {}
    for funcao in funcoes:
        if funcao.tipo_funcao.nome not in funcoes_por_tipo:
            funcoes_por_tipo[funcao.tipo_funcao.nome] = []
        funcoes_por_tipo[funcao.tipo_funcao.nome].append(funcao)
    
    vagas_data = [
        # Palco Principal
        {
            'setor': setores[0],  # Palco Principal
            'titulo': 'Técnico de Som - Palco Principal',
            'descricao': 'Responsável pela operação e manutenção dos equipamentos de som no palco principal',
            'quantidade': 2,
            'remuneracao': 300.00
        },
        {
            'setor': setores[0],  # Palco Principal
            'titulo': 'Técnico de Iluminação - Palco Principal',
            'descricao': 'Responsável pela operação dos equipamentos de iluminação cênica',
            'quantidade': 1,
            'remuneracao': 350.00
        },
        # Área VIP
        {
            'setor': setores[1],  # Área VIP
            'titulo': 'Recepcionista - Área VIP',
            'descricao': 'Atendimento exclusivo aos convidados VIP',
            'quantidade': 2,
            'remuneracao': 200.00
        },
        # Entrada e Recepção
        {
            'setor': setores[3],  # Entrada e Recepção
            'titulo': 'Segurança - Entrada',
            'descricao': 'Controle de acesso e segurança na entrada do evento',
            'quantidade': 3,
            'remuneracao': 250.00
        }
    ]
    
    vagas_criadas = []
    for vaga_data in vagas_data:
        vaga, created = Vaga.objects.get_or_create(
            titulo=vaga_data['titulo'],
            setor=vaga_data['setor'],
            defaults=vaga_data
        )
        if created:
            print(f"✅ Vaga criada: {vaga.titulo}")
        vagas_criadas.append(vaga)
    
    return vagas_criadas

def main():
    """Função principal do script"""
    print("🚀 Iniciando população completa do sistema...")
    print("=" * 60)
    
    # 1. Criar empresa contratante
    empresa_contratante = criar_empresa_contratante()
    
    # 2. Criar tipos de empresa
    tipos_empresa = criar_tipos_empresa()
    
    # 3. Criar empresas parceiras
    empresas_parceiras = criar_empresas_parceiras(empresa_contratante, tipos_empresa)
    
    # 4. Criar local de evento
    local = criar_local_evento(empresas_parceiras[0])  # Centro de Convenções
    
    # 5. Criar evento
    evento = criar_evento(empresa_contratante, local, empresas_parceiras[1])  # Som & Luz
    
    # 6. Criar setores
    setores = criar_setores(evento)
    
    # 7. Criar categorias de equipamentos
    categorias = criar_categorias_equipamentos(empresa_contratante)
    
    # 8. Criar equipamentos
    equipamentos = criar_equipamentos(empresa_contratante, empresas_parceiras[2], categorias)  # Equipamentos Premium
    
    # 9. Associar equipamentos aos setores
    criar_equipamentos_setor(setores, equipamentos)
    
    # 10. Criar freelancers
    freelancers = criar_freelancers()
    
    # 11. Buscar funções existentes
    funcoes = list(Funcao.objects.all())
    
    # 12. Criar vagas
    vagas = criar_vagas(setores, funcoes, freelancers)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL:")
    print(f"• Empresa contratante: {empresa_contratante.nome_fantasia}")
    print(f"• Empresas parceiras: {len(empresas_parceiras)}")
    print(f"• Local: {local.nome}")
    print(f"• Evento: {evento.nome}")
    print(f"• Setores: {len(setores)}")
    print(f"• Equipamentos: {len(equipamentos)}")
    print(f"• Freelancers: {len(freelancers)}")
    print(f"• Vagas: {len(vagas)}")
    print("=" * 60)
    print("✅ Sistema populado com sucesso!")

if __name__ == '__main__':
    main()
