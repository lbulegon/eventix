// mobile/eventix/lib/pages/vagas_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/vagas_service.dart';
import 'package:eventix/utils/app_logger.dart';

class VagasPage extends StatefulWidget {
  const VagasPage({super.key});

  @override
  State<VagasPage> createState() => _VagasPageState();
}

class _VagasPageState extends State<VagasPage> {
  List<Map<String, dynamic>> _vagas = [];
  bool _carregando = false;
  String? _erro;
  String? _searchQuery;
  int _currentPage = 1;
  bool _hasMore = true;

  @override
  void initState() {
    super.initState();
    _carregarVagas();
  }

  Future<void> _carregarVagas({bool refresh = false}) async {
    if (refresh) {
      setState(() {
        _currentPage = 1;
        _hasMore = true;
        _vagas.clear();
      });
    }

    if (!_hasMore && !refresh) return;

    setState(() {
      _carregando = true;
      _erro = null;
    });

    try {
      AppLogger.info('Loading vagas', category: LogCategory.api, data: {
        'page': _currentPage,
        'search': _searchQuery,
      });

      final novasVagas = await VagasService.getVagas(
        search: _searchQuery,
        page: _currentPage,
      );

      setState(() {
        if (refresh) {
          _vagas = novasVagas;
        } else {
          _vagas.addAll(novasVagas);
        }

        _hasMore = novasVagas.length >= 10; // Assumindo paginação de 10
        if (_hasMore) _currentPage++;
        _carregando = false;
      });

      AppLogger.info('Vagas loaded successfully',
          category: LogCategory.api,
          data: {
            'count': _vagas.length,
          });
    } catch (e) {
      setState(() {
        _erro = 'Erro ao carregar vagas';
        _carregando = false;
      });

      AppLogger.error('Failed to load vagas',
          category: LogCategory.api, error: e);
    }
  }

  Future<void> _candidatarVaga(int vagaId) async {
    try {
      AppLogger.info('Candidating to vaga',
          category: LogCategory.api, data: {'vaga_id': vagaId});

      final result = await VagasService.candidatarVaga(vagaId);

      if (result['success'] == true) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message']),
              backgroundColor: Colors.green,
            ),
          );
        }

        // Recarregar vagas para atualizar status
        _carregarVagas(refresh: true);
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
      AppLogger.error('Failed to candidate to vaga',
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

  void _mostrarFiltros() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Filtros',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            // Aqui você pode adicionar filtros específicos
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _carregarVagas(refresh: true);
              },
              child: const Text('Aplicar Filtros'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Vagas Disponíveis'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _mostrarFiltros,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _carregarVagas(refresh: true),
          ),
        ],
      ),
      body: Column(
        children: [
          // Barra de busca
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Buscar vagas...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery != null && _searchQuery!.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          setState(() {
                            _searchQuery = null;
                          });
                          _carregarVagas(refresh: true);
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              onSubmitted: (value) {
                setState(() {
                  _searchQuery = value.trim().isEmpty ? null : value.trim();
                });
                _carregarVagas(refresh: true);
              },
            ),
          ),

          // Lista de vagas
          Expanded(
            child: _carregando && _vagas.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : _erro != null && _vagas.isEmpty
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
                              onPressed: () => _carregarVagas(refresh: true),
                              child: const Text('Tentar Novamente'),
                            ),
                          ],
                        ),
                      )
                    : _vagas.isEmpty
                        ? const Center(
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
                                  'Nenhuma vaga disponível',
                                  style: TextStyle(fontSize: 16),
                                ),
                              ],
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: () => _carregarVagas(refresh: true),
                            child: ListView.builder(
                              itemCount: _vagas.length + (_hasMore ? 1 : 0),
                              itemBuilder: (context, index) {
                                if (index == _vagas.length) {
                                  // Loading indicator para próxima página
                                  return const Padding(
                                    padding: EdgeInsets.all(16),
                                    child: Center(
                                      child: CircularProgressIndicator(),
                                    ),
                                  );
                                }

                                final vaga = _vagas[index];
                                return _buildVagaCard(vaga);
                              },
                            ),
                          ),
          ),
        ],
      ),
    );
  }

  Widget _buildVagaCard(Map<String, dynamic> vaga) {
    final evento = vaga['setor']?['evento'];
    final funcao = vaga['funcao'];

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Título da vaga
            Text(
              vaga['titulo'] ?? 'Vaga sem título',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1F2937),
              ),
            ),
            const SizedBox(height: 8),

            // Evento - usando evento_nome que vem diretamente da vaga
            if (vaga['evento_nome'] != null) ...[
              Row(
                children: [
                  const Icon(Icons.event, size: 16, color: Color(0xFF6B7280)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      vaga['evento_nome'],
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
                  'R\$ ${vaga['remuneracao']?.toString() ?? '0.00'}',
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
                onPressed: () => _candidatarVaga(vaga['id']),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6366F1),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text('Candidatar-se'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
