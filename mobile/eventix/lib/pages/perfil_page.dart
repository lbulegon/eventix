// mobile/eventix/lib/pages/perfil_page.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:eventix/providers/user_provider.dart';
import 'package:eventix/services/freelancers_service.dart';
import 'package:eventix/utils/app_logger.dart';

class PerfilPage extends StatefulWidget {
  const PerfilPage({super.key});

  @override
  State<PerfilPage> createState() => _PerfilPageState();
}

class _PerfilPageState extends State<PerfilPage> {
  Map<String, dynamic>? _perfilFreelancer;
  bool _carregando = false;
  String? _erro;

  @override
  void initState() {
    super.initState();
    _carregarPerfil();
  }

  Future<void> _carregarPerfil() async {
    setState(() {
      _carregando = true;
      _erro = null;
    });

    try {
      AppLogger.info('Loading freelancer profile', category: LogCategory.api);

      final perfil = await FreelancersService.getPerfilFreelancer();

      setState(() {
        _perfilFreelancer = perfil;
        _carregando = false;
      });

      AppLogger.info('Freelancer profile loaded successfully',
          category: LogCategory.api);
    } catch (e) {
      setState(() {
        _erro = 'Erro ao carregar perfil';
        _carregando = false;
      });

      AppLogger.error('Failed to load freelancer profile',
          category: LogCategory.api, error: e);
    }
  }

  void _editarPerfil() {
    Navigator.pushNamed(context, '/editar-perfil');
  }

  @override
  Widget build(BuildContext context) {
    final userProvider = context.watch<UserProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Perfil'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: _editarPerfil,
          ),
        ],
      ),
      body: _carregando
          ? const Center(child: CircularProgressIndicator())
          : _erro != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 64,
                        color: Colors.red,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        _erro!,
                        style: const TextStyle(fontSize: 16),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _carregarPerfil,
                        child: const Text('Tentar Novamente'),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      // Avatar e informações básicas
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 10,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            // Avatar
                            CircleAvatar(
                              radius: 50,
                              backgroundColor: const Color(0xFF6366F1),
                              child: Text(
                                userProvider.nome
                                        ?.substring(0, 1)
                                        .toUpperCase() ??
                                    'U',
                                style: const TextStyle(
                                  fontSize: 32,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),

                            // Nome
                            Text(
                              userProvider.nome ?? 'Nome não disponível',
                              style: const TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1F2937),
                              ),
                            ),
                            const SizedBox(height: 8),

                            // Email
                            Text(
                              userProvider.email ?? 'Email não disponível',
                              style: const TextStyle(
                                fontSize: 16,
                                color: Color(0xFF6B7280),
                              ),
                            ),
                            const SizedBox(height: 4),

                            // Tipo de usuário
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFF6366F1).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                userProvider.tipoUsuario ??
                                    'Tipo não disponível',
                                style: const TextStyle(
                                  color: Color(0xFF6366F1),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Informações do Freelancer
                      if (_perfilFreelancer != null) ...[
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.1),
                                blurRadius: 10,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Informações do Freelancer',
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF1F2937),
                                ),
                              ),
                              const SizedBox(height: 16),

                              // CPF
                              if (_perfilFreelancer!['cpf'] != null) ...[
                                _buildInfoRow('CPF', _perfilFreelancer!['cpf']),
                                const SizedBox(height: 12),
                              ],

                              // Telefone
                              if (_perfilFreelancer!['telefone'] != null) ...[
                                _buildInfoRow(
                                    'Telefone', _perfilFreelancer!['telefone']),
                                const SizedBox(height: 12),
                              ],

                              // Data de Nascimento
                              if (_perfilFreelancer!['data_nascimento'] !=
                                  null) ...[
                                _buildInfoRow('Data de Nascimento',
                                    _perfilFreelancer!['data_nascimento']),
                                const SizedBox(height: 12),
                              ],

                              // Sexo
                              if (_perfilFreelancer!['sexo'] != null) ...[
                                _buildInfoRow(
                                    'Sexo',
                                    _perfilFreelancer!['sexo'] == 'M'
                                        ? 'Masculino'
                                        : 'Feminino'),
                                const SizedBox(height: 12),
                              ],

                              // Habilidades
                              if (_perfilFreelancer!['habilidades'] != null &&
                                  _perfilFreelancer!['habilidades']
                                      .toString()
                                      .isNotEmpty) ...[
                                _buildInfoRow('Habilidades',
                                    _perfilFreelancer!['habilidades']),
                                const SizedBox(height: 12),
                              ],

                              // Endereço
                              if (_perfilFreelancer!['cidade'] != null ||
                                  _perfilFreelancer!['uf'] != null) ...[
                                _buildInfoRow(
                                    'Localização',
                                    '${_perfilFreelancer!['cidade'] ?? ''}, ${_perfilFreelancer!['uf'] ?? ''}'
                                        .replaceAll(', ', '')
                                        .replaceAll(',', '')),
                                const SizedBox(height: 12),
                              ],

                              // Dados Bancários
                              if (_perfilFreelancer!['banco'] != null ||
                                  _perfilFreelancer!['chave_pix'] != null) ...[
                                const Text(
                                  'Dados Bancários',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF1F2937),
                                  ),
                                ),
                                const SizedBox(height: 8),
                                if (_perfilFreelancer!['banco'] != null) ...[
                                  _buildInfoRow(
                                      'Banco', _perfilFreelancer!['banco']),
                                  const SizedBox(height: 8),
                                ],
                                if (_perfilFreelancer!['chave_pix'] !=
                                    null) ...[
                                  _buildInfoRow('Chave PIX',
                                      _perfilFreelancer!['chave_pix']),
                                  const SizedBox(height: 8),
                                ],
                              ],
                            ],
                          ),
                        ),
                        const SizedBox(height: 24),
                      ],

                      // Botão de Editar Perfil
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: _editarPerfil,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF6366F1),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: const Text(
                            'Editar Perfil',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 120,
          child: Text(
            '$label:',
            style: const TextStyle(
              fontWeight: FontWeight.w500,
              color: Color(0xFF6B7280),
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              color: Color(0xFF1F2937),
            ),
          ),
        ),
      ],
    );
  }
}
