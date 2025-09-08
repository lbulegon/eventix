// mobile/eventix/lib/pages/debug_user_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/auth_service.dart';
import 'package:eventix/services/vagas_service.dart';
import 'package:eventix/services/funcoes_service.dart';
import 'package:eventix/utils/app_logger.dart';

class DebugUserPage extends StatefulWidget {
  const DebugUserPage({super.key});

  @override
  State<DebugUserPage> createState() => _DebugUserPageState();
}

class _DebugUserPageState extends State<DebugUserPage> {
  Map<String, dynamic>? _userData;
  List<Map<String, dynamic>> _vagas = [];
  List<Map<String, dynamic>> _funcoes = [];
  bool _carregando = false;
  String? _erro;

  @override
  void initState() {
    super.initState();
    _carregarDados();
  }

  Future<void> _carregarDados() async {
    setState(() {
      _carregando = true;
      _erro = null;
    });

    try {
      // Carregar dados do usuário
      _userData = AuthService.userData;

      // Tentar carregar vagas e funções
      final results = await Future.wait([
        VagasService.getVagas(),
        FuncoesService.getMinhasFuncoes(),
      ]);

      _vagas = results[0] as List<Map<String, dynamic>>;
      _funcoes = results[1] as List<Map<String, dynamic>>;

      setState(() {
        _carregando = false;
      });
    } catch (e) {
      setState(() {
        _erro = e.toString();
        _carregando = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Debug - Usuário'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _carregarDados,
          ),
        ],
      ),
      body: _carregando
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Status de Login
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Status de Login',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          _buildInfoRow(
                              'Logado', AuthService.isLoggedIn.toString()),
                          _buildInfoRow('Tem Token',
                              (AuthService.accessToken != null).toString()),
                          _buildInfoRow(
                              'Token (primeiros 20 chars)',
                              AuthService.accessToken?.substring(0, 20) ??
                                  'null'),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Dados do Usuário
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Dados do Usuário',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          if (_userData != null) ...[
                            _buildInfoRow(
                                'ID', _userData!['id']?.toString() ?? 'null'),
                            _buildInfoRow('Nome',
                                _userData!['nome']?.toString() ?? 'null'),
                            _buildInfoRow('Email',
                                _userData!['email']?.toString() ?? 'null'),
                            _buildInfoRow(
                                'Tipo Usuário',
                                _userData!['tipo_usuario']?.toString() ??
                                    'null'),
                            _buildInfoRow('É Freelancer',
                                AuthService.isFreelancer.toString()),
                            _buildInfoRow(
                                'É Empresa', AuthService.isEmpresa.toString()),
                          ] else
                            const Text('Nenhum dado de usuário encontrado'),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Teste de Vagas
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Teste de Vagas',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          _buildInfoRow(
                              'Vagas Encontradas', _vagas.length.toString()),
                          if (_erro != null) _buildInfoRow('Erro', _erro!),
                          if (_vagas.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            const Text('Primeira Vaga:'),
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.grey[100],
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                _vagas.first.toString(),
                                style: const TextStyle(fontSize: 12),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Funções
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Minhas Funções',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          _buildInfoRow('Total de Funções Cadastradas',
                              _funcoes.length.toString()),
                          if (_funcoes.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            const Text('Funções de Segurança:'),
                            ...(_funcoes.map((e) => Padding(
                                  padding:
                                      const EdgeInsets.only(left: 8, top: 4),
                                  child: Text(
                                    '• ${e['funcao']['nome']} (${e['nivel'] ?? 'iniciante'})',
                                    style: const TextStyle(fontSize: 12),
                                  ),
                                ))),
                          ] else
                            const Text(
                              'Nenhuma função de segurança cadastrada',
                              style: TextStyle(color: Colors.red),
                            ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Botões de Ação
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () async {
                            try {
                              final vagas = await VagasService.getVagas();
                              setState(() {
                                _vagas = vagas;
                                _erro = null;
                              });
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content:
                                      Text('Vagas carregadas: ${vagas.length}'),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            } catch (e) {
                              setState(() {
                                _erro = e.toString();
                              });
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Erro: $e'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          },
                          child: const Text('Testar Vagas'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () async {
                            try {
                              final vagas =
                                  await VagasService.getVagasRecomendadas();
                              setState(() {
                                _vagas = vagas;
                                _erro = null;
                              });
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(
                                      'Vagas recomendadas: ${vagas.length}'),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            } catch (e) {
                              setState(() {
                                _erro = e.toString();
                              });
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Erro: $e'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          },
                          child: const Text('Testar Recomendadas'),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 8),

                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () async {
                            try {
                              final funcoes =
                                  await FuncoesService.getMinhasFuncoes();
                              setState(() {
                                _funcoes = funcoes;
                                _erro = null;
                              });
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(
                                      'Funções de segurança carregadas: ${funcoes.length}'),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            } catch (e) {
                              setState(() {
                                _erro = e.toString();
                              });
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Erro: $e'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          },
                          child: const Text('Testar Funções'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            Navigator.pushNamed(context, '/funcoes');
                          },
                          child: const Text('Gerenciar Funções'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: value == 'null' || value == 'false'
                    ? Colors.red
                    : Colors.black,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
