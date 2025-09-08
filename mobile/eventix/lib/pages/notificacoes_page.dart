// mobile/eventix/lib/pages/notificacoes_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/notificacoes_service.dart';
import 'package:eventix/utils/app_logger.dart';

class NotificacoesPage extends StatefulWidget {
  const NotificacoesPage({super.key});

  @override
  State<NotificacoesPage> createState() => _NotificacoesPageState();
}

class _NotificacoesPageState extends State<NotificacoesPage> {
  List<Map<String, dynamic>> _notificacoes = [];
  bool _carregando = false;
  String? _erro;
  int _contadorNaoLidas = 0;

  @override
  void initState() {
    super.initState();
    _carregarNotificacoes();
    _carregarContadorNaoLidas();
  }

  Future<void> _carregarNotificacoes() async {
    setState(() {
      _carregando = true;
      _erro = null;
    });

    try {
      AppLogger.info('Loading notifications', category: LogCategory.api);

      final notificacoes = await NotificacoesService.getNotificacoes();

      setState(() {
        _notificacoes = notificacoes;
        _carregando = false;
      });

      AppLogger.info('Notifications loaded successfully',
          category: LogCategory.api,
          data: {
            'count': _notificacoes.length,
          });
    } catch (e) {
      setState(() {
        _erro = 'Erro ao carregar notificações';
        _carregando = false;
      });

      AppLogger.error('Failed to load notifications',
          category: LogCategory.api, error: e);
    }
  }

  Future<void> _carregarContadorNaoLidas() async {
    try {
      final count = await NotificacoesService.getContadorNaoLidas();
      setState(() {
        _contadorNaoLidas = count;
      });
    } catch (e) {
      AppLogger.error('Failed to load unread count',
          category: LogCategory.api, error: e);
    }
  }

  Future<void> _marcarComoLida(int notificacaoId) async {
    try {
      final result = await NotificacoesService.marcarComoLida(notificacaoId);

      if (result['success'] == true) {
        // Atualizar a notificação local
        setState(() {
          final index =
              _notificacoes.indexWhere((n) => n['id'] == notificacaoId);
          if (index != -1) {
            _notificacoes[index]['lida'] = true;
          }
          _contadorNaoLidas =
              (_contadorNaoLidas - 1).clamp(0, double.infinity).toInt();
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message']),
              backgroundColor: Colors.green,
            ),
          );
        }
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
      AppLogger.error('Failed to mark notification as read',
          category: LogCategory.api, error: e);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content:
                Text('Erro ao marcar notificação como lida. Tente novamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _marcarTodasComoLidas() async {
    try {
      final result = await NotificacoesService.marcarTodasComoLidas();

      if (result['success'] == true) {
        setState(() {
          for (var notificacao in _notificacoes) {
            notificacao['lida'] = true;
          }
          _contadorNaoLidas = 0;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message']),
              backgroundColor: Colors.green,
            ),
          );
        }
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
      AppLogger.error('Failed to mark all notifications as read',
          category: LogCategory.api, error: e);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
                'Erro ao marcar todas as notificações como lidas. Tente novamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _deletarNotificacao(int notificacaoId) async {
    try {
      final result =
          await NotificacoesService.deletarNotificacao(notificacaoId);

      if (result['success'] == true) {
        setState(() {
          _notificacoes.removeWhere((n) => n['id'] == notificacaoId);
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message']),
              backgroundColor: Colors.green,
            ),
          );
        }
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
      AppLogger.error('Failed to delete notification',
          category: LogCategory.api, error: e);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Erro ao deletar notificação. Tente novamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  String _getTipoIcon(String tipo) {
    switch (tipo.toLowerCase()) {
      case 'candidatura_aprovada':
        return '✅';
      case 'candidatura_rejeitada':
        return '❌';
      case 'nova_vaga':
        return '🆕';
      case 'vaga_urgente':
        return '🚨';
      case 'evento_proximo':
        return '📅';
      default:
        return '📢';
    }
  }

  Color _getTipoColor(String tipo) {
    switch (tipo.toLowerCase()) {
      case 'candidatura_aprovada':
        return Colors.green;
      case 'candidatura_rejeitada':
        return Colors.red;
      case 'nova_vaga':
        return Colors.blue;
      case 'vaga_urgente':
        return Colors.orange;
      case 'evento_proximo':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notificações'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
        actions: [
          if (_contadorNaoLidas > 0)
            IconButton(
              icon: const Icon(Icons.done_all),
              onPressed: _marcarTodasComoLidas,
              tooltip: 'Marcar todas como lidas',
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              _carregarNotificacoes();
              _carregarContadorNaoLidas();
            },
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
                        onPressed: () {
                          _carregarNotificacoes();
                          _carregarContadorNaoLidas();
                        },
                        child: const Text('Tentar Novamente'),
                      ),
                    ],
                  ),
                )
              : _notificacoes.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.notifications_none,
                            size: 64,
                            color: Color(0xFF6366F1),
                          ),
                          SizedBox(height: 16),
                          Text(
                            'Nenhuma notificação',
                            style: TextStyle(fontSize: 18),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'Você receberá notificações sobre suas candidaturas e novas vagas',
                            style: TextStyle(color: Color(0xFF6B7280)),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: () async {
                        await _carregarNotificacoes();
                        await _carregarContadorNaoLidas();
                      },
                      child: ListView.builder(
                        itemCount: _notificacoes.length,
                        itemBuilder: (context, index) {
                          final notificacao = _notificacoes[index];
                          return _buildNotificacaoCard(notificacao);
                        },
                      ),
                    ),
    );
  }

  Widget _buildNotificacaoCard(Map<String, dynamic> notificacao) {
    final tipo = notificacao['tipo'] ?? 'geral';
    final lida = notificacao['lida'] ?? false;
    final data = notificacao['data_criacao'] ?? '';

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      color: lida ? null : const Color(0xFF6366F1).withOpacity(0.05),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getTipoColor(tipo).withOpacity(0.1),
          child: Text(
            _getTipoIcon(tipo),
            style: const TextStyle(fontSize: 20),
          ),
        ),
        title: Text(
          notificacao['titulo'] ?? 'Notificação',
          style: TextStyle(
            fontWeight: lida ? FontWeight.normal : FontWeight.bold,
            color: lida ? const Color(0xFF6B7280) : const Color(0xFF1F2937),
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (notificacao['mensagem'] != null)
              Text(
                notificacao['mensagem'],
                style: TextStyle(
                  color:
                      lida ? const Color(0xFF9CA3AF) : const Color(0xFF6B7280),
                ),
              ),
            const SizedBox(height: 4),
            Text(
              data,
              style: const TextStyle(
                fontSize: 12,
                color: Color(0xFF9CA3AF),
              ),
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (!lida)
              IconButton(
                icon: const Icon(Icons.mark_email_read, size: 20),
                onPressed: () => _marcarComoLida(notificacao['id']),
                tooltip: 'Marcar como lida',
              ),
            IconButton(
              icon: const Icon(Icons.delete, size: 20),
              onPressed: () => _deletarNotificacao(notificacao['id']),
              tooltip: 'Deletar',
            ),
          ],
        ),
        onTap: !lida ? () => _marcarComoLida(notificacao['id']) : null,
      ),
    );
  }
}
