// mobile/eventix/lib/pages/pre_cadastro_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/freelancers_service.dart';
import 'package:eventix/utils/app_logger.dart';
import 'package:eventix/services/analytics_service.dart';

class PreCadastroPage extends StatefulWidget {
  const PreCadastroPage({super.key});

  @override
  State<PreCadastroPage> createState() => _PreCadastroPageState();
}

class _PreCadastroPageState extends State<PreCadastroPage> {
  final _formKey = GlobalKey<FormState>();
  final _nomeController = TextEditingController();
  final _telefoneController = TextEditingController();
  final _cpfController = TextEditingController();
  final _emailController = TextEditingController();
  final _senhaController = TextEditingController();
  final _confirmarSenhaController = TextEditingController();
  final _dataNascimentoController = TextEditingController();

  bool _carregando = false;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  String? _sexo;
  String? _erro;
  String? _sucesso;

  final List<String> _sexoOptions = ['M', 'F'];

  @override
  void dispose() {
    _nomeController.dispose();
    _telefoneController.dispose();
    _cpfController.dispose();
    _emailController.dispose();
    _senhaController.dispose();
    _confirmarSenhaController.dispose();
    _dataNascimentoController.dispose();
    super.dispose();
  }

  Future<void> _fazerPreCadastro() async {
    print('🎯 [PRE_CADASTRO] Iniciando processo de pré-cadastro...');

    if (!_formKey.currentState!.validate()) {
      print('❌ [PRE_CADASTRO] Validação do formulário falhou');
      AppLogger.warning('Pre-cadastro form validation failed',
          category: LogCategory.auth);
      return;
    }

    print('✅ [PRE_CADASTRO] Validação do formulário passou');
    print('📝 [PRE_CADASTRO] Dados do formulário:');
    print('   - Nome: ${_nomeController.text.trim()}');
    print('   - Telefone: ${_telefoneController.text.trim()}');
    print('   - CPF: ${_cpfController.text.trim()}');
    print('   - Email: ${_emailController.text.trim()}');
    print('   - Data Nascimento: ${_dataNascimentoController.text.trim()}');
    print('   - Sexo: $_sexo');

    setState(() {
      _carregando = true;
      _erro = null;
      _sucesso = null;
    });

    print('🔄 [PRE_CADASTRO] Estado atualizado - carregando: true');

    AppLogger.info('Pre-cadastro attempt started',
        category: LogCategory.auth,
        data: {
          'email': _emailController.text.trim(),
          'nome': _nomeController.text.trim(),
        });

    try {
      print('🚀 [PRE_CADASTRO] Chamando FreelancersService.preCadastro...');
      final result = await FreelancersService.preCadastro(
        nomeCompleto: _nomeController.text.trim(),
        telefone: _telefoneController.text.trim(),
        cpf: _cpfController.text.trim(),
        email: _emailController.text.trim(),
        password: _senhaController.text,
        dataNascimento: _dataNascimentoController.text.trim().isNotEmpty
            ? _dataNascimentoController.text.trim()
            : null,
        sexo: _sexo,
      );

      print('📨 [PRE_CADASTRO] Resultado recebido do serviço: $result');
      print('🔍 [PRE_CADASTRO] Success: ${result['success']}');
      print('💬 [PRE_CADASTRO] Message: ${result['message']}');
      print('❌ [PRE_CADASTRO] Error: ${result['error']}');

      if (result['success'] == true) {
        print('🎉 [PRE_CADASTRO] Pré-cadastro realizado com sucesso!');
        AppLogger.info('Pre-cadastro successful',
            category: LogCategory.auth,
            data: {
              'email': _emailController.text.trim(),
            });

        await AnalyticsService.logSignUp();

        setState(() {
          _sucesso = result['message'];
        });

        // Limpar formulário
        _formKey.currentState!.reset();
        _nomeController.clear();
        _telefoneController.clear();
        _cpfController.clear();
        _emailController.clear();
        _senhaController.clear();
        _confirmarSenhaController.clear();
        _dataNascimentoController.clear();
        _sexo = null;

        // Mostrar sucesso e navegar para login após 2 segundos
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            Navigator.pop(context);
          }
        });
      } else {
        print('❌ [PRE_CADASTRO] Pré-cadastro falhou!');
        print('🔍 [PRE_CADASTRO] Erro: ${result['error']}');

        setState(() {
          _erro = result['error'] ?? 'Erro no pré-cadastro';
        });

        print('🔄 [PRE_CADASTRO] Estado atualizado com erro: $_erro');

        AppLogger.warning('Pre-cadastro failed',
            category: LogCategory.auth,
            data: {
              'email': _emailController.text.trim(),
              'error': _erro,
            });
      }
    } catch (e) {
      print('💥 [PRE_CADASTRO] EXCEÇÃO CAPTURADA!');
      print('🔍 [PRE_CADASTRO] Tipo da exceção: ${e.runtimeType}');
      print('📝 [PRE_CADASTRO] Mensagem da exceção: ${e.toString()}');

      setState(() {
        _erro = 'Erro de conexão. Tente novamente.';
      });

      print('🔄 [PRE_CADASTRO] Estado atualizado com erro de conexão');

      AppLogger.error('Pre-cadastro error',
          category: LogCategory.auth,
          error: e,
          data: {
            'email': _emailController.text.trim(),
          });
    } finally {
      if (mounted) {
        setState(() {
          _carregando = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Criar Conta'),
        backgroundColor: const Color(0xFF6366F1),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Logo/Ícone
              const Icon(
                Icons.person_add_outlined,
                size: 64,
                color: Color(0xFF6366F1),
              ),
              const SizedBox(height: 24),

              // Título
              const Text(
                'Criar Conta de Freelancer',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              const Text(
                'Preencha os dados abaixo para criar sua conta',
                style: TextStyle(
                  fontSize: 16,
                  color: Color(0xFF6B7280),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // Nome Completo
              TextFormField(
                controller: _nomeController,
                decoration: const InputDecoration(
                  labelText: 'Nome Completo *',
                  prefixIcon: Icon(Icons.person),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Nome é obrigatório';
                  }
                  if (value.trim().length < 2) {
                    return 'Nome deve ter pelo menos 2 caracteres';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Email
              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Email *',
                  prefixIcon: Icon(Icons.email),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Email é obrigatório';
                  }
                  if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$')
                      .hasMatch(value)) {
                    return 'Email inválido';
                  }
                  if (value == 'lbulegon@gmail.com') {
                    return 'Este email já está cadastrado. Use outro email ou faça login.';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Telefone
              TextFormField(
                controller: _telefoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Telefone *',
                  prefixIcon: Icon(Icons.phone),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Telefone é obrigatório';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // CPF
              TextFormField(
                controller: _cpfController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'CPF *',
                  prefixIcon: Icon(Icons.badge),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'CPF é obrigatório';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Data de Nascimento
              TextFormField(
                controller: _dataNascimentoController,
                decoration: const InputDecoration(
                  labelText: 'Data de Nascimento (YYYY-MM-DD)',
                  prefixIcon: Icon(Icons.calendar_today),
                  border: OutlineInputBorder(),
                ),
                onTap: () async {
                  final date = await showDatePicker(
                    context: context,
                    initialDate: DateTime.now()
                        .subtract(const Duration(days: 6570)), // 18 anos atrás
                    firstDate: DateTime(1900),
                    lastDate:
                        DateTime.now().subtract(const Duration(days: 6570)),
                  );
                  if (date != null) {
                    _dataNascimentoController.text =
                        date.toIso8601String().split('T')[0];
                  }
                },
              ),
              const SizedBox(height: 16),

              // Sexo
              DropdownButtonFormField<String>(
                value: _sexo,
                decoration: const InputDecoration(
                  labelText: 'Sexo',
                  prefixIcon: Icon(Icons.person_outline),
                  border: OutlineInputBorder(),
                ),
                items: _sexoOptions.map((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value == 'M' ? 'Masculino' : 'Feminino'),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _sexo = newValue;
                  });
                },
              ),
              const SizedBox(height: 16),

              // Senha
              TextFormField(
                controller: _senhaController,
                obscureText: _obscurePassword,
                decoration: InputDecoration(
                  labelText: 'Senha *',
                  prefixIcon: const Icon(Icons.lock),
                  border: const OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(_obscurePassword
                        ? Icons.visibility
                        : Icons.visibility_off),
                    onPressed: () {
                      setState(() {
                        _obscurePassword = !_obscurePassword;
                      });
                    },
                  ),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Senha é obrigatória';
                  }
                  if (value.length < 8) {
                    return 'Senha deve ter pelo menos 8 caracteres';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Confirmar Senha
              TextFormField(
                controller: _confirmarSenhaController,
                obscureText: _obscureConfirmPassword,
                decoration: InputDecoration(
                  labelText: 'Confirmar Senha *',
                  prefixIcon: const Icon(Icons.lock_outline),
                  border: const OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(_obscureConfirmPassword
                        ? Icons.visibility
                        : Icons.visibility_off),
                    onPressed: () {
                      setState(() {
                        _obscureConfirmPassword = !_obscureConfirmPassword;
                      });
                    },
                  ),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Confirmação de senha é obrigatória';
                  }
                  if (value != _senhaController.text) {
                    return 'Senhas não coincidem';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),

              // Mensagens de erro/sucesso
              if (_erro != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.withOpacity(0.3)),
                  ),
                  child: Column(
                    children: [
                      Text(
                        _erro!,
                        style: const TextStyle(color: Colors.red),
                        textAlign: TextAlign.center,
                      ),
                      if (_erro!.contains('conexão') ||
                          _erro!.contains('internet') ||
                          _erro!.contains('servidor'))
                        Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: ElevatedButton(
                            onPressed: _carregando ? null : _fazerPreCadastro,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red,
                              foregroundColor: Colors.white,
                            ),
                            child: const Text('Tentar Novamente'),
                          ),
                        ),
                    ],
                  ),
                ),

              if (_sucesso != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.withOpacity(0.3)),
                  ),
                  child: Text(
                    _sucesso!,
                    style: const TextStyle(color: Colors.green),
                    textAlign: TextAlign.center,
                  ),
                ),

              // Botão de Cadastro
              ElevatedButton(
                onPressed: _carregando ? null : _fazerPreCadastro,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6366F1),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: _carregando
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text(
                        'Criar Conta',
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
              const SizedBox(height: 16),

              // Link para Login
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: const Text('Já tem uma conta? Faça login'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
