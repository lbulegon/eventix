// mobile/eventix/lib/services/freelancers_service.dart
import 'package:dio/dio.dart';
import '../utils/app_config.dart';
import '../utils/app_logger.dart';
import 'auth_service.dart';

class FreelancersService {
  static final Dio _dio = Dio();

  /// Inicializa o serviço
  static void initialize() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (AuthService.accessToken != null) {
          options.headers['Authorization'] =
              'Bearer ${AuthService.accessToken}';
        }
        handler.next(options);
      },
    ));
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
      AppLogger.info('Freelancer pre-cadastro started',
          category: LogCategory.api,
          data: {
            'nome_completo': nomeCompleto,
            'email': email,
            'cpf': cpf,
          });

      final response = await _dio.post(
        AppConfig.preCadastro,
        data: {
          'nome_completo': nomeCompleto,
          'telefone': telefone,
          'cpf': cpf,
          'email': email,
          'password': password,
          if (dataNascimento != null) 'data_nascimento': dataNascimento,
          if (sexo != null) 'sexo': sexo,
          if (habilidades != null) 'habilidades': habilidades,
        },
      );

      if (response.statusCode == 201) {
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
      }
    } catch (e) {
      AppLogger.error('Freelancer pre-cadastro failed',
          category: LogCategory.api, error: e, data: {'email': email});

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
        } else if (response?.statusCode == 409) {
          return {
            'success': false,
            'error': 'Email ou CPF já cadastrado',
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
