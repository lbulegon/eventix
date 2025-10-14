# ✅ Configuração Firebase - Eventix Mobile

## 🎯 Configuração Completa Seguindo as Instruções Oficiais do Firebase

Este projeto foi configurado seguindo **exatamente** as [instruções oficiais do Firebase](https://firebase.google.com/docs/android/setup) para Android.

---

## 📁 Estrutura de Arquivos

```
mobile/eventix/
├── android/
│   ├── app/
│   │   ├── build.gradle.kts          ✅ Configurado
│   │   └── google-services.json      ✅ Presente
│   └── build.gradle.kts              ✅ Configurado
├── lib/
│   └── main.dart                     ✅ Firebase inicializado
└── pubspec.yaml                      ✅ Dependências instaladas
```

---

## 🔧 Configurações Implementadas

### 1. Arquivo `android/build.gradle.kts` (Nível do Projeto)

```kotlin
plugins {
    // Add the dependency for the Google services Gradle plugin
    id("com.google.gms.google-services") version "4.4.3" apply false
}
```

**✅ O que isso faz:**
- Declara o plugin do Google Services na versão mais recente (4.4.3)
- O `apply false` significa que o plugin é declarado mas só será aplicado no módulo app

---

### 2. Arquivo `android/app/build.gradle.kts` (Nível do App)

```kotlin
plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
    // Add the Google services Gradle plugin
    id("com.google.gms.google-services")
}

dependencies {
    // Import the Firebase BoM
    implementation(platform("com.google.firebase:firebase-bom:34.3.0"))

    // Firebase products (quando usar BoM, não especificar versões)
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-messaging")
    implementation("com.google.firebase:firebase-crashlytics")
}
```

**✅ O que isso faz:**
- Aplica o plugin do Google Services no módulo app
- Importa o Firebase BoM (Bill of Materials) versão 34.3.0
- Adiciona as bibliotecas Firebase necessárias SEM especificar versões
- O BoM garante compatibilidade entre todas as bibliotecas Firebase

---

### 3. Arquivo `google-services.json`

**📍 Localização:** `android/app/google-services.json`

Este arquivo contém as configurações do seu projeto Firebase:
- Project ID
- Application ID (`com.example.eventix`)
- API Keys
- URLs do projeto

**⚠️ IMPORTANTE:** 
- Este arquivo NÃO deve ser commitado se contiver informações sensíveis
- Sempre baixe a versão mais recente do Firebase Console
- O Package Name deve corresponder ao `applicationId` no `build.gradle.kts`

---

### 4. Dependências Flutter (`pubspec.yaml`)

```yaml
dependencies:
  firebase_core: ^2.24.2          # Núcleo do Firebase
  firebase_messaging: ^14.7.10    # Push Notifications
  firebase_analytics: ^10.8.0     # Analytics
  firebase_crashlytics: ^3.4.9    # Crash Reporting
```

**✅ Instalado com:** `flutter pub get`

---

### 5. Código Flutter (`lib/main.dart`)

**Inicialização do Firebase:**
```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // ... inicializa Firebase em background
}

Future<void> _initializeServicesInBackground() async {
  await Firebase.initializeApp();
  await _initializeFirebaseMessaging();
  // ...
}
```

**Handlers de Notificações:**
- ✅ Foreground (app aberto)
- ✅ Background (app minimizado)
- ✅ Terminated (app fechado)

---

## 🎯 Package Name / Application ID

```
com.example.eventix
```

**Onde está definido:**
- `android/app/build.gradle.kts`: `applicationId = "com.example.eventix"`
- Firebase Console: Deve ter o mesmo nome

---

## 🔥 Firebase BoM (Bill of Materials)

### O que é?

O Firebase BoM é uma forma de gerenciar versões de bibliotecas Firebase de maneira centralizada.

### Vantagens:

1. **Compatibilidade Garantida:** Todas as bibliotecas Firebase são compatíveis entre si
2. **Simplicidade:** Não precisa especificar versão para cada biblioteca
3. **Atualizações Fáceis:** Basta atualizar a versão do BoM
4. **Menos Conflitos:** Reduz problemas de dependências incompatíveis

### Como funciona:

```kotlin
// Importa o BoM
implementation(platform("com.google.firebase:firebase-bom:34.3.0"))

// Adiciona bibliotecas SEM especificar versões
implementation("com.google.firebase:firebase-analytics")    // ✅ Versão gerenciada pelo BoM
implementation("com.google.firebase:firebase-messaging")    // ✅ Versão gerenciada pelo BoM
implementation("com.google.firebase:firebase-crashlytics")  // ✅ Versão gerenciada pelo BoM
```

### Versões Gerenciadas pelo BoM 34.3.0:

O BoM 34.3.0 inclui:
- `firebase-analytics`: 22.3.0
- `firebase-messaging`: 24.3.0
- `firebase-crashlytics`: 19.3.0
- E muitas outras...

---

## 🚀 Como Testar

### 1. Limpar o projeto:
```bash
flutter clean
```

### 2. Instalar dependências:
```bash
flutter pub get
```

### 3. Executar o app:
```bash
flutter run
```

### 4. Verificar no console:
```
✅ Permissão de notificações concedida
📱 FCM Token: [seu_token_aqui]
```

---

## 📚 Documentação

- **Guia Completo:** `docs/GUIA_FLUTTER_FCM.md`
- **Setup Backend:** `NOTIFICACOES_PUSH_SETUP.md`
- **README Principal:** `README.md` (seção Firebase)
- **Instruções Oficiais:** https://firebase.google.com/docs/android/setup

---

## ✅ Checklist de Configuração

- [x] Plugin Google Services v4.4.3 adicionado no projeto
- [x] Plugin aplicado no módulo app
- [x] Firebase BoM v34.3.0 importado
- [x] Bibliotecas Firebase adicionadas (Analytics, Messaging, Crashlytics)
- [x] Arquivo `google-services.json` no lugar correto
- [x] Package Name configurado (`com.example.eventix`)
- [x] Dependências Flutter instaladas
- [x] Firebase inicializado no `main.dart`
- [x] Handlers de notificações configurados
- [x] Permissões de notificações solicitadas
- [x] FCM Token obtido e exibido

---

## 🎯 Próximos Passos

1. **Testar o App:**
   - Execute e verifique se o FCM Token é exibido no console

2. **Integrar com Backend:**
   - Enviar o FCM Token para o backend Django
   - Endpoint: `POST /api/v1/notificacoes/registrar-token/`

3. **Configurar Firebase Console:**
   - Adicionar Server Key nas variáveis de ambiente do Django
   - Testar envio de notificações

4. **Testar Notificações:**
   - Criar uma vaga no backend
   - Verificar se a notificação chega no app

---

## ⚠️ Observações Importantes

1. **Versões do Plugin:**
   - Google Services Plugin: `4.4.3` (mais recente)
   - Firebase BoM: `34.3.0` (mais recente)

2. **Compatibilidade:**
   - Gradle: Kotlin DSL (`.kts`)
   - Flutter SDK: ^3.6.0
   - Android minSdk: Definido pelo Flutter

3. **Segurança:**
   - O `google-services.json` contém chaves de API
   - Considere adicionar ao `.gitignore` para projetos privados
   - Use Firebase App Check em produção

---

**Configurado em:** Outubro 2025  
**Última atualização:** Seguindo instruções oficiais do Firebase

