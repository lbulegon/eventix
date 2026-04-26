// mobile/eventix/lib/services/freelancers_service.dart
import 'package:dio/dio.dart';
import '../utils/app_config.dart';
import '../utils/app_logger.dart';
import 'auth_service.dart';

class FreelancersService {
  static final Dio _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    sendTimeout: const Duration(seconds: 30),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  /// Inicializa o serviço
  static void initialize() {
    print('🔧 [FREELANCERS_SERVICE] Inicializando serviço...');
    print('🌐 [FREELANCERS_SERVICE] Configurações do Dio:');
    print('   - Connect Timeout: 30s');
    print('   - Receive Timeout: 30s');
    print('   - Send Timeout: 30s');

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        print('🚀 [DIO_INTERCEPTOR] Fazendo requisição para: ${options.uri}');
        print('📋 [DIO_INTERCEPTOR] Método: ${options.method}');
        print('📦 [DIO_INTERCEPTOR] Headers: ${options.headers}');
        print('📄 [DIO_INTERCEPTOR] Dados: ${options.data}');

        if (AuthService.accessToken != null) {
          options.headers['Authorization'] =
              'Bearer ${AuthService.accessToken}';
          print('🔑 [DIO_INTERCEPTOR] Token adicionado aos headers');
        } else {
          print('⚠️ [DIO_INTERCEPTOR] Nenhum token de acesso encontrado');
        }
        handler.next(options);
      },
      onResponse: (response, handler) {
        print('✅ [DIO_INTERCEPTOR] Resposta recebida: ${response.statusCode}');
        print('📊 [DIO_INTERCEPTOR] Headers da resposta: ${response.headers}');
        print('📄 [DIO_INTERCEPTOR] Dados da resposta: ${response.data}');
        handler.next(response);
      },
      onError: (error, handler) {
        print('❌ [DIO_INTERCEPTOR] Erro na requisição: ${error.message}');
        print('🔍 [DIO_INTERCEPTOR] Tipo do erro: ${error.type}');
        print(
            '📊 [DIO_INTERCEPTOR] Status Code: ${error.response?.statusCode}');
        print('📄 [DIO_INTERCEPTOR] Dados do erro: ${error.response?.data}');
        handler.next(error);
      },
    ));

    print('✅ [FREELANCERS_SERVICE] Serviço inicializado com sucesso!');
  }

  /// Faz pré-cadastro de freelancer
  static Future<Map<String, dynamic>> preCadastro({
    required String nomeCompleto,
    required String telefone,
    required String cpf,
    required String email,
    required String password,
    String? dataNascimento,
    String? sexo,
    String? habilidades,
  }) async {
    try {
      print('🚀 [FREELANCERS_SERVICE] Iniciando pré-cadastro...');
      print('📧 [FREELANCERS_SERVICE] Email: $email');
      print('👤 [FREELANCERS_SERVICE] Nome: $nomeCompleto');
      print('📱 [FREELANCERS_SERVICE] Telefone: $telefone');
      print('🆔 [FREELANCERS_SERVICE] CPF: $cpf');

      AppLogger.info('Freelancer pre-cadastro started',
          category: LogCategory.api,
          data: {
            'nome_completo': nomeCompleto,
            'email': email,
            'cpf': cpf,
          });

      print('🌐 [FREELANCERS_SERVICE] URL da API: ${AppConfig.preCadastro}');
      print('📦 [FREELANCERS_SERVICE] Preparando dados para envio...');

      final requestData = {
        'nome_completo': nomeCompleto, // Servidor espera nome_completo
        'telefone': telefone,
        'cpf': cpf,
        'email': email,
        'password': password,
        'tipo_usuario': 'freelancer', // Definir como freelancer
        if (dataNascimento != null && dataNascimento.isNotEmpty)
          'data_nascimento': dataNascimento,
        if (sexo != null && sexo.isNotEmpty) 'sexo': sexo,
      };

      print('📋 [FREELANCERS_SERVICE] Dados preparados: $requestData');
      print('🔄 [FREELANCERS_SERVICE] Enviando requisição POST...');

      final response = await _dio.post(
        AppConfig.preCadastro,
        data: requestData,
      );

      print('✅ [FREELANCERS_SERVICE] Resposta recebida!');
      print('📊 [FREELANCERS_SERVICE] Status Code: ${response.statusCode}');
      print('📄 [FREELANCERS_SERVICE] Dados da resposta: ${response.data}');

      if (response.statusCode == 201) {
        print('🎉 [FREELANCERS_SERVICE] Pré-cadastro realizado com sucesso!');
        AppLogger.info('Freelancer pre-cadastro successful',
            category: LogCategory.api,
            data: {
              'freelancer_id': response.data['freelancer_id'],
            });

        return {
          'success': true,
          'message': 'Pré-cadastro realizado com sucesso!',
          'data': response.data,
        };
      } else {
        print(
            '⚠️ [FREELANCERS_SERVICE] Status code inesperado: ${response.statusCode}');
        return {
          'success': false,
          'error': 'Status code inesperado: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('❌ [FREELANCERS_SERVICE] ERRO CAPTURADO!');
      print('🔍 [FREELANCERS_SERVICE] Tipo do erro: ${e.runtimeType}');
      print('📝 [FREELANCERS_SERVICE] Mensagem do erro: ${e.toString()}');

      AppLogger.error('Freelancer pre-cadastro failed',
          category: LogCategory.api, error: e, data: {'email': email});

      if (e is DioException) {
        print('🌐 [FREELANCERS_SERVICE] Erro é do tipo DioException');
        final response = e.response;
        final statusCode = response?.statusCode;

        print('🔴 [FREELANCERS_SERVICE] Status Code: $statusCode');
        print('🔴 [FREELANCERS_SERVICE] Dados da resposta: ${response?.data}');
        print(
            '🔴 [FREELANCERS_SERVICE] Headers da resposta: ${response?.headers}');
        print('🔴 [FREELANCERS_SERVICE] Tipo do erro Dio: ${e.type}');
        print('🔴 [FREELANCERS_SERVICE] Mensagem do erro Dio: ${e.message}');

        if (statusCode == 400) {
          final data = response?.data;
          if (data is Map<String, dynamic>) {
            final errors = <String>[];
            data.forEach((key, value) {
              if (value is List) {
                errors.addAll(value.map((e) => e.toString()));
              } else {
                errors.add(value.toString());
              }
            });

            return {
              'success': false,
              'error': errors.join(', '),
            };
          }
        } else if (statusCode == 409) {
          return {
            'success': false,
            'error': 'Email ou CPF já cadastrado',
          };
        } else if (statusCode == 500) {
          // Verifica se é erro de email duplicado
          final responseData = response?.data;
          print(
              '🔍 [FREELANCERS_SERVICE] Resposta do servidor (500): $responseData');

          if (responseData != null) {
            final responseString = responseData.toString().toLowerCase();
            if (responseString
                .contains('duplicate key value violates unique constraint')) {
              if (responseString.contains('username') ||
                  responseString.contains('email')) {
                return {
                  'success': false,
                  'error':
                      'Este email já está cadastrado. Tente fazer login ou use outro email.',
                };
              } else if (responseString.contains('cpf')) {
                return {
                  'success': false,
                  'error': 'Este CPF já está cadastrado.',
                };
              }
            }
          }
          return {
            'success': false,
            'error': 'Erro interno do servidor. Tente novamente mais tarde.',
          };
        } else if (statusCode == null) {
          // Erro de conexão (sem resposta do servidor)
          return {
            'success': false,
            'error': 'Sem conexão com a internet. Verifique sua conexão.',
          };
        } else {
          return {
            'success': false,
            'error': 'Erro do servidor (código $statusCode). Tente novamente.',
          };
        }
      }

      // Erro não relacionado ao Dio
      print('🔴 Erro não relacionado ao Dio: $e');
      return {
        'success': false,
        'error': 'Erro inesperado. Verifique sua conexão e tente novamente.',
      };
    }

    return {
      'success': false,
      'error': 'Erro desconhecido',
    };
  }

  /// Estado do onboarding (nível 2) + prompt sugerido (texto de apoio / IA).
  static Future<Map<String, dynamic>?> getOnboardingNivel2() async {
    try {
      final response = await _dio.get(AppConfig.freelancerOnboardingNivel2);
      if (response.statusCode == 200 && response.data is Map<String, dynamic>) {
        return Map<String, dynamic>.from(response.data);
      }
    } catch (e) {
      AppLogger.error('Failed to fetch onboarding nivel 2',
          category: LogCategory.api, error: e);
    }
    return null;
  }

  /// Atualiza apenas os campos do nível 2 (dados pessoais e endereço, sem bancário).
  static Future<Map<String, dynamic>> patchOnboardingNivel2(
      Map<String, dynamic> campos) async {
    try {
      final response = await _dio.patch(
        AppConfig.freelancerOnboardingNivel2,
        data: campos,
      );
      if (response.statusCode == 200 && response.data is Map) {
        return {
          'success': true,
          'data': response.data,
        };
      }
    } catch (e) {
      AppLogger.error('Failed to patch onboarding nivel 2',
          category: LogCategory.api, error: e);
      if (e is DioException) {
        return {
          'success': false,
          'error': e.response?.data?.toString() ?? e.message,
        };
      }
    }
    return {'success': false, 'error': 'Erro desconhecido'};
  }

  /// Obtém perfil do freelancer
  static Future<Map<String, dynamic>?> getPerfilFreelancer() async {
    try {
      AppLogger.info('Fetching freelancer profile', category: LogCategory.api);

      final response = await _dio.get(AppConfig.freelancerProfile);

      if (response.statusCode == 200) {
        final data = response.data;

        AppLogger.info('Freelancer profile fetched successfully',
            category: LogCategory.api,
            data: {
              'freelancer_id': data['id'],
            });

        return data;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch freelancer profile',
          category: LogCategory.api, error: e);
    }

    return null;
  }

  /// Atualiza perfil do freelancer
  static Future<Map<String, dynamic>> atualizarPerfilFreelancer({
    String? nomeCompleto,
    String? telefone,
    String? documento,
    String? habilidades,
    String? cpf,
    String? rg,
    String? dataNascimento,
    String? sexo,
    String? estadoCivil,
    String? cep,
    String? logradouro,
    String? numero,
    String? complemento,
    String? bairro,
    String? cidade,
    String? uf,
    String? banco,
    String? agencia,
    String? conta,
    String? tipoConta,
    String? chavePix,
    String? observacoes,
  }) async {
    try {
      AppLogger.info('Updating freelancer profile', category: LogCategory.api);

      final data = <String, dynamic>{};
      if (nomeCompleto != null) data['nome_completo'] = nomeCompleto;
      if (telefone != null) data['telefone'] = telefone;
      if (documento != null) data['documento'] = documento;
      if (habilidades != null) data['habilidades'] = habilidades;
      if (cpf != null) data['cpf'] = cpf;
      if (rg != null) data['rg'] = rg;
      if (dataNascimento != null) data['data_nascimento'] = dataNascimento;
      if (sexo != null) data['sexo'] = sexo;
      if (estadoCivil != null) data['estado_civil'] = estadoCivil;
      if (cep != null) data['cep'] = cep;
      if (logradouro != null) data['logradouro'] = logradouro;
      if (numero != null) data['numero'] = numero;
      if (complemento != null) data['complemento'] = complemento;
      if (bairro != null) data['bairro'] = bairro;
      if (cidade != null) data['cidade'] = cidade;
      if (uf != null) data['uf'] = uf;
      if (banco != null) data['banco'] = banco;
      if (agencia != null) data['agencia'] = agencia;
      if (conta != null) data['conta'] = conta;
      if (tipoConta != null) data['tipo_conta'] = tipoConta;
      if (chavePix != null) data['chave_pix'] = chavePix;
      if (observacoes != null) data['observacoes'] = observacoes;

      final response = await _dio.put(
        AppConfig.freelancerProfile,
        data: data,
      );

      if (response.statusCode == 200) {
        AppLogger.info('Freelancer profile updated successfully',
            category: LogCategory.api);

        return {
          'success': true,
          'message': 'Perfil atualizado com sucesso!',
          'data': response.data,
        };
      }
    } catch (e) {
      AppLogger.error('Failed to update freelancer profile',
          category: LogCategory.api, error: e);

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 400) {
          final data = response?.data;
          if (data is Map<String, dynamic>) {
            final errors = <String>[];
            data.forEach((key, value) {
              if (value is List) {
                errors.addAll(value.map((e) => e.toString()));
              } else {
                errors.add(value.toString());
              }
            });

            return {
              'success': false,
              'error': errors.join(', '),
            };
          }
        } else if (response?.statusCode == 403) {
          return {
            'success': false,
            'error': 'Você não tem permissão para editar este perfil',
          };
        }
      }

      return {
        'success': false,
        'error': 'Erro de conexão. Tente novamente.',
      };
    }

    return {
      'success': false,
      'error': 'Erro desconhecido',
    };
  }

  /// Lista todos os freelancers (apenas para empresas/admin)
  static Future<List<Map<String, dynamic>>> getFreelancers() async {
    try {
      AppLogger.info('Fetching all freelancers', category: LogCategory.api);

      final response = await _dio.get(AppConfig.freelancerProfile);

      if (response.statusCode == 200) {
        final data = response.data;
        final freelancers =
            List<Map<String, dynamic>>.from(data['results'] ?? []);

        AppLogger.info('Freelancers fetched successfully',
            category: LogCategory.api,
            data: {
              'count': freelancers.length,
            });

        return freelancers;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch freelancers',
          category: LogCategory.api, error: e);
    }

    return [];
  }
}
