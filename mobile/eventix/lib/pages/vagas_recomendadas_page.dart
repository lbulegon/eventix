// mobile/eventix/lib/pages/vagas_recomendadas_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/vagas_service.dart';
import 'package:eventix/utils/app_logger.dart';

class VagasRecomendadasPage extends StatefulWidget {
  const VagasRecomendadasPage({super.key});

  @override
  State<VagasRecomendadasPage> createState() => _VagasRecomendadasPageState();
}

class _VagasRecomendadasPageState extends State<VagasRecomendadasPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<Map<String, dynamic>> _vagasRecomendadas = [];
  List<Map<String, dynamic>> _vagasTrending = [];
  List<Map<String, dynamic>> _vagasUrgentes = [];

  bool _carregandoRecomendadas = false;
  bool _carregandoTrending = false;
  bool _carregandoUrgentes = false;

  String? _erroRecomendadas;
  String? _erroTrending;
  String? _erroUrgentes;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _carregarTodasAsVagas();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _carregarTodasAsVagas() async {
    await Future.wait([
      _carregarVagasRecomendadas(),
      _carregarVagasTrending(),
      _carregarVagasUrgentes(),
    ]);
  }

  Future<void> _carregarVagasRecomendadas() async {
    setState(() {
      _carregandoRecomendadas = true;
      _erroRecomendadas = null;
    });

    try {
      AppLogger.info('Loading recommended vagas', category: LogCategory.api);

      final vagas = await VagasService.getVagasRecomendadas();

      setState(() {
        _vagasRecomendadas = vagas;
        _carregandoRecomendadas = false;
      });

      AppLogger.info('Recommended vagas loaded successfully',
          category: LogCategory.api,
          data: {
            'count': _vagasRecomendadas.length,
          });
    } catch (e) {
      setState(() {
        _erroRecomendadas = 'Erro ao carregar vagas recomendadas';
        _carregandoRecomendadas = false;
      });

      AppLogger.error('Failed to load recommended vagas',
          category: LogCategory.api, error: e);
    }
  }

  Future<void> _carregarVagasTrending() async {
    setState(() {
      _carregandoTrending = true;
      _erroTrending = null;
    });

    try {
      AppLogger.info('Loading trending vagas', category: LogCategory.api);

      final vagas = await VagasService.getVagasTrending();

      setState(() {
        _vagasTrending = vagas;
        _carregandoTrending = false;
      });

      AppLogger.info('Trending vagas loaded successfully',
          category: LogCategory.api,
          data: {
            'count': _vagasTrending.length,
          });
    } catch (e) {
      setState(() {
        _erroTrending = 'Erro ao carregar vagas em alta';
        _carregandoTrending = false;
      });

      AppLogger.error('Failed to load trending vagas',
          category: LogCategory.api, error: e);
    }
  }

  Future<void> _carregarVagasUrgentes() async {
    setState(() {
      _carregandoUrgentes = true;
      _erroUrgentes = null;
    });

    try {
      AppLogger.info('Loading urgent vagas', category: LogCategory.api);

      final vagas = await VagasService.getVagasUrgentes();

      setState(() {
        _vagasUrgentes = vagas;
        _carregandoUrgentes = false;
      });

      AppLogger.info('Urgent vagas loaded successfully',
          category: LogCategory.api,
          data: {
            'count': _vagasUrgentes.length,
          });
    } catch (e) {
      setState(() {
        _erroUrgentes = 'Erro ao carregar vagas urgentes';
        _carregandoUrgentes = false;
      });

      AppLogger.error('Failed to load urgent vagas',
          category: LogCategory.api, error: e);
    }
  }

  Future<void> _candidatarVagaComCarta(int vagaId) async {
    final cartaController = TextEditingController();

    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Carta de Apresentação'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Escreva uma carta de apresentação para esta vaga:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: cartaController,
              maxLines: 5,
              decoration: const InputDecoration(
                hintText:
                    'Conte um pouco sobre você e por que você é ideal para esta vaga...',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              if (cartaController.text.trim().isNotEmpty) {
                Navigator.pop(context, true);
              }
            },
            child: const Text('Candidatar-se'),
          ),
        ],
      ),
    );

    if (result == true && cartaController.text.trim().isNotEmpty) {
      try {
        AppLogger.info('Candidating to vaga with cover letter',
            category: LogCategory.api, data: {'vaga_id': vagaId});

        final result = await VagasService.candidatarVagaComCarta(
          vagaId,
          cartaController.text.trim(),
        );

        if (result['success'] == true) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(result['message']),
                backgroundColor: Colors.green,
              ),
            );
          }

          // Recarregar vagas
          _carregarTodasAsVagas();
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
        AppLogger.error('Failed to candidate to vaga with cover letter',
            category: LogCategory.api, error: e);

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Erro ao se candidatar. Tente novamente.'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Vagas para Você'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(
              icon: Icon(Icons.recommend),
              text: 'Recomendadas',
            ),
            Tab(
              icon: Icon(Icons.trending_up),
              text: 'Em Alta',
            ),
            Tab(
              icon: Icon(Icons.priority_high),
              text: 'Urgentes',
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _carregarTodasAsVagas,
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildVagasList(
            vagas: _vagasRecomendadas,
            carregando: _carregandoRecomendadas,
            erro: _erroRecomendadas,
            onRefresh: _carregarVagasRecomendadas,
            emptyMessage: 'Nenhuma vaga recomendada encontrada',
            emptySubtitle:
                'Complete seu perfil para receber recomendações personalizadas',
          ),
          _buildVagasList(
            vagas: _vagasTrending,
            carregando: _carregandoTrending,
            erro: _erroTrending,
            onRefresh: _carregarVagasTrending,
            emptyMessage: 'Nenhuma vaga em alta no momento',
            emptySubtitle: 'As vagas mais populares aparecerão aqui',
          ),
          _buildVagasList(
            vagas: _vagasUrgentes,
            carregando: _carregandoUrgentes,
            erro: _erroUrgentes,
            onRefresh: _carregarVagasUrgentes,
            emptyMessage: 'Nenhuma vaga urgente no momento',
            emptySubtitle: 'Vagas com prazo próximo aparecerão aqui',
            isUrgent: true,
          ),
        ],
      ),
    );
  }

  Widget _buildVagasList({
    required List<Map<String, dynamic>> vagas,
    required bool carregando,
    required String? erro,
    required Future<void> Function() onRefresh,
    required String emptyMessage,
    required String emptySubtitle,
    bool isUrgent = false,
  }) {
    if (carregando) {
      return const Center(child: CircularProgressIndicator());
    }

    if (erro != null) {
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
              erro,
              style: const TextStyle(fontSize: 16),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: onRefresh,
              child: const Text('Tentar Novamente'),
            ),
          ],
        ),
      );
    }

    if (vagas.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              isUrgent ? Icons.priority_high : Icons.work_outline,
              size: 64,
              color: const Color(0xFF6366F1),
            ),
            const SizedBox(height: 16),
            Text(
              emptyMessage,
              style: const TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 8),
            Text(
              emptySubtitle,
              style: const TextStyle(color: Color(0xFF6B7280)),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: ListView.builder(
        itemCount: vagas.length,
        itemBuilder: (context, index) {
          final vaga = vagas[index];
          return _buildVagaCard(vaga, isUrgent: isUrgent);
        },
      ),
    );
  }

  Widget _buildVagaCard(Map<String, dynamic> vaga, {bool isUrgent = false}) {
    final evento = vaga['setor']?['evento'];
    final funcao = vaga['funcao'];

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Cabeçalho com badge
            Row(
              children: [
                Expanded(
                  child: Text(
                    vaga['titulo'] ?? 'Vaga sem título',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                ),
                if (isUrgent)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.red),
                    ),
                    child: const Text(
                      'URGENTE',
                      style: TextStyle(
                        color: Colors.red,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),

            // Evento
            if (evento != null) ...[
              Row(
                children: [
                  const Icon(Icons.event, size: 16, color: Color(0xFF6B7280)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      evento['nome'] ?? 'Evento sem nome',
                      style: const TextStyle(color: Color(0xFF6B7280)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
            ],

            // Função
            if (funcao != null) ...[
              Row(
                children: [
                  const Icon(Icons.work, size: 16, color: Color(0xFF6B7280)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      funcao['nome'] ?? 'Função não especificada',
                      style: const TextStyle(color: Color(0xFF6B7280)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
            ],

            // Quantidade
            Row(
              children: [
                const Icon(Icons.people, size: 16, color: Color(0xFF6B7280)),
                const SizedBox(width: 8),
                Text(
                  '${vaga['quantidade'] ?? 0} vaga(s)',
                  style: const TextStyle(color: Color(0xFF6B7280)),
                ),
              ],
            ),
            const SizedBox(height: 4),

            // Remuneração
            Row(
              children: [
                const Icon(Icons.attach_money,
                    size: 16, color: Color(0xFF6B7280)),
                const SizedBox(width: 8),
                Text(
                  'R\$ ${_formatarValor(vaga['remuneracao'])}',
                  style: const TextStyle(
                    color: Color(0xFF6B7280),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),

            // Descrição
            if (vaga['descricao'] != null &&
                vaga['descricao'].toString().isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                vaga['descricao'],
                style: const TextStyle(color: Color(0xFF6B7280)),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],

            const SizedBox(height: 16),

            // Botão de candidatura
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => _candidatarVagaComCarta(vaga['id']),
                style: ElevatedButton.styleFrom(
                  backgroundColor:
                      isUrgent ? Colors.red : const Color(0xFF6366F1),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: Text(
                    isUrgent ? 'Candidatar-se (Urgente)' : 'Candidatar-se'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
