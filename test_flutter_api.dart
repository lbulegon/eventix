// Teste de conexão com a API do Flutter
import 'dart:convert';
import 'package:dio/dio.dart';

void main() async {
  print('=== TESTANDO CONEXÃO COM API DO FLUTTER ===');
  
  final dio = Dio();
  
  try {
    // Teste 1: Verificar se a API está online
    print('1. Testando conexão com a API...');
    final response = await dio.get('https://eventix-development.up.railway.app/api/v1/funcoes/');
    
    print('✅ API está online!');
    print('Status: ${response.statusCode}');
    print('Headers: ${response.headers}');
    
    // Teste 2: Verificar dados das funções
    if (response.data != null) {
      print('\n2. Dados das funções:');
      final data = response.data;
      if (data is List) {
        print('Total de funções: ${data.length}');
        for (var funcao in data) {
          print('  - ${funcao['nome']}: ${funcao['descricao']}');
        }
      } else {
        print('Formato de dados: ${data.runtimeType}');
        print('Dados: $data');
      }
    }
    
    // Teste 3: Testar endpoint de vagas
    print('\n3. Testando endpoint de vagas...');
    final vagasResponse = await dio.get('https://eventix-development.up.railway.app/api/v1/vagas/');
    print('✅ Endpoint de vagas funcionando!');
    print('Status: ${vagasResponse.statusCode}');
    
    if (vagasResponse.data != null) {
      final vagasData = vagasResponse.data;
      if (vagasData is List) {
        print('Total de vagas: ${vagasData.length}');
        for (var vaga in vagasData.take(3)) {
          print('  - ${vaga['titulo']}: R\$ ${vaga['remuneracao']}');
        }
      }
    }
    
    print('\n🎉 Todos os testes passaram! A API está funcionando corretamente.');
    
  } catch (e) {
    print('❌ Erro na conexão com a API: $e');
    if (e is DioException) {
      print('Status: ${e.response?.statusCode}');
      print('Mensagem: ${e.response?.data}');
    }
  }
}
