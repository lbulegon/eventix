// mobile/eventix/lib/pages/minhas_candidaturas_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/vagas_service.dart';
import 'package:eventix/utils/app_logger.dart';

class MinhasCandidaturasPage extends StatefulWidget {
  const MinhasCandidaturasPage({super.key});

  @override
  State<MinhasCandidaturasPage> createState() => _MinhasCandidaturasPageState();
}

class _MinhasCandidaturasPageState extends State<MinhasCandidaturasPage> {
  List<Map<String, dynamic>> _candidaturas = [];
  bool _carregando = false;
  String? _erro;

  @override
  void initState() {
    super.initState();
    _carregarCandidaturas();
  }

  Future<void> _carregarCandidaturas() async {
    setState(() {
      _carregando = true;
      _erro = null;
    });

    try {
      AppLogger.info('Loading user candidaturas', category: LogCategory.api);

      final candidaturas = await VagasService.getMinhasCandidaturas();

      setState(() {
        _candidaturas = candidaturas;
        _carregando = false;
      });

      AppLogger.info('Candidaturas loaded successfully', category: LogCategory.api, data: {
        'count': _candidaturas.length,
      });
    } catch (e) {
      setState(() {
        _erro = 'Erro ao carregar candidaturas';
        _carregando = false;
      });

      AppLogger.error('Failed to load candidaturas', category: LogCategory.api, error: e);
    }
  }

  Future<void> _cancelarCandidatura(int candidaturaId) async {
    try {
      AppLogger.info('Canceling candidatura', category: LogCategory.api, data: {'candidatura_id': candidaturaId});

      final result = await VagasService.cancelarCandidatura(candidaturaId);

      if (result['success'] == true) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message']),
              backgroundColor: Colors.green,
            ),
          );
        }

        // Recarregar candidaturas
        _carregarCandidaturas();
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
      AppLogger.error('Failed to cancel candidatura', category: LogCategory.api, error: e);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Erro ao cancelar candidatura. Tente novamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
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

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pendente':
        return Colors.orange;
      case 'aprovada':
        return Colors.green;
      case 'rejeitada':
        return Colors.red;
      case 'cancelada':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Minhas Candidaturas'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _carregarCandidaturas,
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
                        onPressed: _carregarCandidaturas,
                        child: const Text('Tentar Novamente'),
                      ),
                    ],
                  ),
                )
              : _candidaturas.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.assignment_outlined,
                            size: 64,
                            color: Color(0xFF6366F1),
                          ),
                          SizedBox(height: 16),
                          Text(
                            'Nenhuma candidatura encontrada',
                            style: TextStyle(fontSize: 18),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'Você ainda não se candidatou a nenhuma vaga',
                            style: TextStyle(color: Color(0xFF6B7280)),
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _carregarCandidaturas,
                      child: ListView.builder(
                        itemCount: _candidaturas.length,
                        itemBuilder: (context, index) {
                          final candidatura = _candidaturas[index];
                          return _buildCandidaturaCard(candidatura);
                        },
                      ),
                    ),
    );
  }

  Widget _buildCandidaturaCard(Map<String, dynamic> candidatura) {
    final vaga = candidatura['vaga'];
    final evento = vaga?['setor']?['evento'];
    final funcao = vaga?['funcao'];
    final status = candidatura['status'] ?? 'pendente';
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Cabeçalho com status
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    vaga?['titulo'] ?? 'Vaga sem título',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStatusColor(status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _getStatusColor(status)),
                  ),
                  child: Text(
                    _getStatusText(status),
                    style: TextStyle(
                      color: _getStatusColor(status),
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

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

            // Remuneração
            Row(
              children: [
                const Icon(Icons.attach_money, size: 16, color: Color(0xFF6B7280)),
                const SizedBox(width: 8),
                Text(
                  'R\$ ${vaga?['remuneracao']?.toStringAsFixed(2) ?? '0.00'}',
                  style: const TextStyle(
                    color: Color(0xFF6B7280),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),

            // Data da candidatura
            Row(
              children: [
                const Icon(Icons.access_time, size: 16, color: Color(0xFF6B7280)),
                const SizedBox(width: 8),
                Text(
                  'Candidatado em: ${candidatura['data_candidatura'] ?? 'Data não disponível'}',
                  style: const TextStyle(color: Color(0xFF6B7280)),
                ),
              ],
            ),

            // Observações
            if (candidatura['observacoes'] != null && candidatura['observacoes'].toString().isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                'Observações: ${candidatura['observacoes']}',
                style: const TextStyle(color: Color(0xFF6B7280)),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],

            const SizedBox(height: 16),

            // Botões de ação
            if (status == 'pendente') ...[
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => _cancelarCandidatura(candidatura['id']),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Cancelar Candidatura'),
                ),
              ),
            ] else if (status == 'aprovada') ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green),
                ),
                child: const Text(
                  'Parabéns! Sua candidatura foi aprovada.',
                  style: TextStyle(
                    color: Colors.green,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ] else if (status == 'rejeitada') ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red),
                ),
                child: const Text(
                  'Sua candidatura foi rejeitada.',
                  style: TextStyle(
                    color: Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}