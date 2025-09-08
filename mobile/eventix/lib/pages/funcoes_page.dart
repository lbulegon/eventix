// mobile/eventix/lib/pages/funcoes_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/funcoes_service.dart';
import 'package:eventix/utils/app_logger.dart';

class FuncoesPage extends StatefulWidget {
  const FuncoesPage({super.key});

  @override
  State<FuncoesPage> createState() => _FuncoesPageState();
}

class _FuncoesPageState extends State<FuncoesPage> {
  List<Map<String, dynamic>> _funcoesDisponiveis = [];
  List<Map<String, dynamic>> _minhasFuncoes = [];

  bool _carregandoDisponiveis = false;
  bool _carregandoMinhas = false;

  String? _erroDisponiveis;
  String? _erroMinhas;

  @override
  void initState() {
    super.initState();
    _carregarFuncoes();
  }

  Future<void> _carregarFuncoes() async {
    await Future.wait([
      _carregarFuncoesDisponiveis(),
      _carregarMinhasFuncoes(),
    ]);
  }

  Future<void> _carregarFuncoesDisponiveis() async {
    setState(() {
      _carregandoDisponiveis = true;
      _erroDisponiveis = null;
    });

    try {
      AppLogger.info('Loading available funcoes', category: LogCategory.api);

      final funcoes = await FuncoesService.getFuncoes();

      // Filter only "Segurança" functions
      final segurancaFuncoes = funcoes.where((funcao) {
        final nome = funcao['nome']?.toString().toLowerCase() ?? '';
        return nome.contains('segurança') ||
            nome.contains('seguranca') ||
            nome.contains('security');
      }).toList();

      setState(() {
        _funcoesDisponiveis = segurancaFuncoes;
        _carregandoDisponiveis = false;
      });

      AppLogger.info('Security functions loaded successfully',
          category: LogCategory.api,
          data: {
            'total_functions': funcoes.length,
            'security_functions': segurancaFuncoes.length,
          });
    } catch (e) {
      setState(() {
        _erroDisponiveis = 'Erro ao carregar funções de segurança';
        _carregandoDisponiveis = false;
      });

      AppLogger.error('Failed to load security functions',
          category: LogCategory.api, error: e);
    }
  }

  Future<void> _carregarMinhasFuncoes() async {
    setState(() {
      _carregandoMinhas = true;
      _erroMinhas = null;
    });

    try {
      AppLogger.info('Loading user funcoes', category: LogCategory.api);

      final funcoes = await FuncoesService.getMinhasFuncoes();

      setState(() {
        _minhasFuncoes = funcoes;
        _carregandoMinhas = false;
      });

      AppLogger.info('User funcoes loaded successfully',
          category: LogCategory.api,
          data: {
            'count': _minhasFuncoes.length,
          });
    } catch (e) {
      setState(() {
        _erroMinhas = 'Erro ao carregar suas funções';
        _carregandoMinhas = false;
      });

      AppLogger.error('Failed to load user funcoes',
          category: LogCategory.api, error: e);
    }
  }

  Future<void> _adicionarFuncao(int funcaoId) async {
    try {
      final result = await FuncoesService.adicionarFuncao(funcaoId);

      if (result['success'] == true) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message']),
              backgroundColor: Colors.green,
            ),
          );
        }

        // Recarregar funções
        _carregarMinhasFuncoes();
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error']),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      AppLogger.error('Failed to add funcao',
          category: LogCategory.api, error: e);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Erro ao adicionar função. Tente novamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _removerFuncao(int freelancerFuncaoId) async {
    try {
      final result = await FuncoesService.removerFuncao(freelancerFuncaoId);

      if (result['success'] == true) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message']),
              backgroundColor: Colors.green,
            ),
          );
        }

        // Recarregar funções
        _carregarMinhasFuncoes();
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error']),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      AppLogger.error('Failed to remove funcao',
          category: LogCategory.api, error: e);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Erro ao remover função. Tente novamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _atualizarNivel(int freelancerFuncaoId, String nivel) async {
    try {
      final result =
          await FuncoesService.atualizarNivelFuncao(freelancerFuncaoId, nivel);

      if (result['success'] == true) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message']),
              backgroundColor: Colors.green,
            ),
          );
        }

        // Recarregar funções
        _carregarMinhasFuncoes();
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error']),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      AppLogger.error('Failed to update funcao level',
          category: LogCategory.api, error: e);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Erro ao atualizar nível. Tente novamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Minhas Funções'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _carregarFuncoes,
          ),
        ],
      ),
      body: DefaultTabController(
        length: 2,
        child: Column(
          children: [
            const TabBar(
              labelColor: Color(0xFF6366F1),
              unselectedLabelColor: Color(0xFF6B7280),
              tabs: [
                Tab(
                  icon: Icon(Icons.add_circle_outline),
                  text: 'Buscar Funções',
                ),
                Tab(
                  icon: Icon(Icons.person),
                  text: 'Minhas Funções',
                ),
              ],
            ),
            Expanded(
              child: TabBarView(
                children: [
                  // Tab: Funções Disponíveis
                  _buildFuncoesDisponiveis(),
                  // Tab: Minhas Funções
                  _buildMinhasFuncoes(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFuncoesDisponiveis() {
    if (_carregandoDisponiveis) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_erroDisponiveis != null) {
      return Center(
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
              _erroDisponiveis!,
              style: const TextStyle(fontSize: 16),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _carregarFuncoesDisponiveis,
              child: const Text('Tentar Novamente'),
            ),
          ],
        ),
      );
    }

    if (_funcoesDisponiveis.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.work_outline,
              size: 64,
              color: Color(0xFF6366F1),
            ),
            SizedBox(height: 16),
            Text(
              'Nenhuma função de segurança disponível',
              style: TextStyle(fontSize: 18),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _carregarFuncoesDisponiveis,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _funcoesDisponiveis.length,
        itemBuilder: (context, index) {
          final funcao = _funcoesDisponiveis[index];
          final jaPossui =
              _minhasFuncoes.any((e) => e['funcao']['id'] == funcao['id']);

          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: const Color(0xFF6366F1).withOpacity(0.1),
                child: const Icon(
                  Icons.work,
                  color: Color(0xFF6366F1),
                ),
              ),
              title: Text(
                funcao['nome'] ?? 'Função sem nome',
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
              subtitle: funcao['descricao'] != null
                  ? Text(funcao['descricao'])
                  : null,
              trailing: jaPossui
                  ? const Chip(
                      label: Text('Já possui'),
                      backgroundColor: Colors.green,
                      labelStyle: TextStyle(color: Colors.white),
                    )
                  : ElevatedButton(
                      onPressed: () => _adicionarFuncao(funcao['id']),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF6366F1),
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Adicionar'),
                    ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildMinhasFuncoes() {
    if (_carregandoMinhas) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_erroMinhas != null) {
      return Center(
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
              _erroMinhas!,
              style: const TextStyle(fontSize: 16),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _carregarMinhasFuncoes,
              child: const Text('Tentar Novamente'),
            ),
          ],
        ),
      );
    }

    if (_minhasFuncoes.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.person_outline,
              size: 64,
              color: Color(0xFF6366F1),
            ),
            SizedBox(height: 16),
            Text(
              'Nenhuma função de segurança cadastrada',
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 8),
            Text(
              'Adicione funções de segurança para receber oportunidades recomendadas',
              style: TextStyle(color: Color(0xFF6B7280)),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _carregarMinhasFuncoes,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _minhasFuncoes.length,
        itemBuilder: (context, index) {
          final funcao = _minhasFuncoes[index];
          final funcaoData = funcao['funcao'];
          final nivel = funcao['nivel'] ?? 'iniciante';

          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: _getNivelColor(nivel).withOpacity(0.1),
                child: Icon(
                  _getNivelIcon(nivel),
                  color: _getNivelColor(nivel),
                ),
              ),
              title: Text(
                funcaoData['nome'] ?? 'Função sem nome',
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (funcaoData['descricao'] != null)
                    Text(funcaoData['descricao']),
                  const SizedBox(height: 4),
                  Chip(
                    label: Text(_getNivelText(nivel)),
                    backgroundColor: _getNivelColor(nivel).withOpacity(0.1),
                    labelStyle: TextStyle(color: _getNivelColor(nivel)),
                  ),
                ],
              ),
              trailing: PopupMenuButton<String>(
                onSelected: (value) {
                  if (value == 'remover') {
                    _removerFuncao(funcao['id']);
                  } else {
                    _atualizarNivel(funcao['id'], value);
                  }
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'iniciante',
                    child: Text('Iniciante'),
                  ),
                  const PopupMenuItem(
                    value: 'intermediario',
                    child: Text('Intermediário'),
                  ),
                  const PopupMenuItem(
                    value: 'avancado',
                    child: Text('Avançado'),
                  ),
                  const PopupMenuItem(
                    value: 'expert',
                    child: Text('Expert'),
                  ),
                  const PopupMenuDivider(),
                  const PopupMenuItem(
                    value: 'remover',
                    child: Text('Remover', style: TextStyle(color: Colors.red)),
                  ),
                ],
                child: const Icon(Icons.more_vert),
              ),
            ),
          );
        },
      ),
    );
  }

  Color _getNivelColor(String nivel) {
    switch (nivel.toLowerCase()) {
      case 'iniciante':
        return Colors.blue;
      case 'intermediario':
        return Colors.orange;
      case 'avancado':
        return Colors.green;
      case 'expert':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  IconData _getNivelIcon(String nivel) {
    switch (nivel.toLowerCase()) {
      case 'iniciante':
        return Icons.star_border;
      case 'intermediario':
        return Icons.star_half;
      case 'avancado':
        return Icons.star;
      case 'expert':
        return Icons.workspace_premium;
      default:
        return Icons.star_border;
    }
  }

  String _getNivelText(String nivel) {
    switch (nivel.toLowerCase()) {
      case 'iniciante':
        return 'Iniciante';
      case 'intermediario':
        return 'Intermediário';
      case 'avancado':
        return 'Avançado';
      case 'expert':
        return 'Expert';
      default:
        return 'Iniciante';
    }
  }
}
