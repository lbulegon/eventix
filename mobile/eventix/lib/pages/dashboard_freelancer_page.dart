// mobile/eventix/lib/pages/dashboard_freelancer_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/vagas_service.dart';
import 'package:eventix/services/notificacoes_service.dart';
import 'package:eventix/utils/app_logger.dart';

class DashboardFreelancerPage extends StatefulWidget {
  const DashboardFreelancerPage({super.key});

  @override
  State<DashboardFreelancerPage> createState() =>
      _DashboardFreelancerPageState();
}

class _DashboardFreelancerPageState extends State<DashboardFreelancerPage> {
  Map<String, dynamic>? _estatisticas;
  List<Map<String, dynamic>> _candidaturas = [];
  List<Map<String, dynamic>> _vagasRecomendadas = [];
  int _contadorNotificacoes = 0;

  bool _carregando = true;
  String? _erro;

  @override
  void initState() {
    super.initState();
    _carregarDashboard();
  }

  Future<void> _carregarDashboard() async {
    setState(() {
      _carregando = true;
      _erro = null;
    });

    try {
      AppLogger.info('Loading freelancer dashboard', category: LogCategory.api);

      // Carregar dados em paralelo
      final results = await Future.wait([
        VagasService.getEstatisticasFreelancer(),
        VagasService.getMinhasCandidaturas(),
        VagasService.getVagasRecomendadas(),
        NotificacoesService.getContadorNaoLidas(),
      ]);

      setState(() {
        _estatisticas = results[0] as Map<String, dynamic>?;
        _candidaturas = results[1] as List<Map<String, dynamic>>;
        _vagasRecomendadas = results[2] as List<Map<String, dynamic>>;
        _contadorNotificacoes = results[3] as int;
        _carregando = false;
      });

      AppLogger.info('Freelancer dashboard loaded successfully',
          category: LogCategory.api,
          data: {
            'estatisticas': _estatisticas != null,
            'candidaturas_count': _candidaturas.length,
            'vagas_recomendadas_count': _vagasRecomendadas.length,
            'notificacoes_count': _contadorNotificacoes,
          });
    } catch (e) {
      setState(() {
        _erro = 'Erro ao carregar dashboard';
        _carregando = false;
      });

      AppLogger.error('Failed to load freelancer dashboard',
          category: LogCategory.api, error: e);
    }
  }

  String _formatarValor(dynamic valor) {
    if (valor == null) return '0.00';
    
    // Se já é uma string, tenta converter para double
    if (valor is String) {
      try {
        final doubleValor = double.parse(valor);
        return doubleValor.toStringAsFixed(2);
      } catch (e) {
        return valor; // Retorna a string original se não conseguir converter
      }
    }
    
    // Se é um número, usa toStringAsFixed
    if (valor is num) {
      return valor.toStringAsFixed(2);
    }
    
    return '0.00';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications),
                onPressed: () {
                  Navigator.pushNamed(context, '/notificacoes');
                },
              ),
              if (_contadorNotificacoes > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 16,
                      minHeight: 16,
                    ),
                    child: Text(
                      '$_contadorNotificacoes',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _carregarDashboard,
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
                        onPressed: _carregarDashboard,
                        child: const Text('Tentar Novamente'),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _carregarDashboard,
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Estatísticas
                        if (_estatisticas != null) _buildEstatisticasCard(),
                        const SizedBox(height: 16),

                        // Candidaturas recentes
                        _buildCandidaturasCard(),
                        const SizedBox(height: 16),

                        // Vagas recomendadas
                        _buildVagasRecomendadasCard(),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildEstatisticasCard() {
    final stats = _estatisticas!;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Suas Estatísticas',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1F2937),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Candidaturas',
                    '${stats['total_candidaturas'] ?? 0}',
                    Icons.assignment,
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Aprovadas',
                    '${stats['candidaturas_aprovadas'] ?? 0}',
                    Icons.check_circle,
                    Colors.green,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Pendentes',
                    '${stats['candidaturas_pendentes'] ?? 0}',
                    Icons.pending,
                    Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Taxa de Aprovação',
                    '${((stats['taxa_aprovacao'] ?? 0) * 100).toStringAsFixed(1)}%',
                    Icons.trending_up,
                    Colors.purple,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Avaliação Média',
                    '${stats['avaliacao_media'] ?? 0}',
                    Icons.star,
                    Colors.amber,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(
      String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            icon,
            color: color,
            size: 24,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Color(0xFF6B7280),
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildCandidaturasCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Candidaturas Recentes',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F2937),
                  ),
                ),
                TextButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/minhas_candidaturas');
                  },
                  child: const Text('Ver Todas'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_candidaturas.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Column(
                    children: [
                      Icon(
                        Icons.assignment_outlined,
                        size: 48,
                        color: Color(0xFF9CA3AF),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Nenhuma candidatura ainda',
                        style: TextStyle(color: Color(0xFF6B7280)),
                      ),
                    ],
                  ),
                ),
              )
            else
              ...(_candidaturas
                  .take(3)
                  .map((candidatura) => _buildCandidaturaItem(candidatura))),
          ],
        ),
      ),
    );
  }

  Widget _buildCandidaturaItem(Map<String, dynamic> candidatura) {
    final vaga = candidatura['vaga'];
    final status = candidatura['status'] ?? 'pendente';

    Color statusColor;
    switch (status) {
      case 'aprovada':
        statusColor = Colors.green;
        break;
      case 'rejeitada':
        statusColor = Colors.red;
        break;
      case 'pendente':
        statusColor = Colors.orange;
        break;
      default:
        statusColor = Colors.grey;
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 40,
            decoration: BoxDecoration(
              color: statusColor,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  vaga?['titulo'] ?? 'Vaga sem título',
                  style: const TextStyle(
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF1F2937),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _getStatusText(status),
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVagasRecomendadasCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Vagas Recomendadas',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F2937),
                  ),
                ),
                TextButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/vagas_recomendadas');
                  },
                  child: const Text('Ver Todas'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_vagasRecomendadas.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Column(
                    children: [
                      Icon(
                        Icons.work_outline,
                        size: 48,
                        color: Color(0xFF9CA3AF),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Nenhuma vaga recomendada',
                        style: TextStyle(color: Color(0xFF6B7280)),
                      ),
                    ],
                  ),
                ),
              )
            else
              ...(_vagasRecomendadas
                  .take(3)
                  .map((vaga) => _buildVagaItem(vaga))),
          ],
        ),
      ),
    );
  }

  Widget _buildVagaItem(Map<String, dynamic> vaga) {
    final evento = vaga['setor']?['evento'];
    final funcao = vaga['funcao'];

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFF6366F1),
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  vaga['titulo'] ?? 'Vaga sem título',
                  style: const TextStyle(
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF1F2937),
                  ),
                ),
                const SizedBox(height: 4),
                if (evento != null)
                  Text(
                    evento['nome'] ?? 'Evento sem nome',
                    style: const TextStyle(
                      color: Color(0xFF6B7280),
                      fontSize: 12,
                    ),
                  ),
                if (funcao != null)
                  Text(
                    funcao['nome'] ?? 'Função não especificada',
                    style: const TextStyle(
                      color: Color(0xFF6B7280),
                      fontSize: 12,
                    ),
                  ),
                Text(
                  'R\$ ${_formatarValor(vaga['remuneracao'])}',
                  style: const TextStyle(
                    color: Color(0xFF10B981),
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _getStatusText(String status) {
    switch (status) {
      case 'pendente':
        return 'Pendente';
      case 'aprovada':
        return 'Aprovada';
      case 'rejeitada':
        return 'Rejeitada';
      case 'cancelada':
        return 'Cancelada';
      default:
        return 'Desconhecido';
    }
  }
}
