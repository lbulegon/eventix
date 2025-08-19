# Eventix Mobile - Guia de Desenvolvimento

## 📱 Visão Geral

O aplicativo móvel Eventix é desenvolvido em React Native com TypeScript, oferecendo uma experiência nativa para Android e iOS. O app se conecta com a API Django backend através de endpoints RESTful.

## 🏗️ Arquitetura

### Estrutura de Pastas
```
mobile/
├── src/
│   ├── contexts/           # Contextos React (Auth, API)
│   ├── services/           # Serviços (API, Storage)
│   ├── screens/            # Telas do aplicativo
│   │   ├── auth/          # Telas de autenticação
│   │   ├── freelancer/    # Telas específicas do freelancer
│   │   ├── empresa/       # Telas específicas da empresa
│   │   └── admin/         # Telas administrativas
│   └── components/        # Componentes reutilizáveis
├── App.tsx                # Componente principal
└── package.json          # Dependências
```

### Fluxo de Navegação
```
Login/Register → Dashboard específico por tipo de usuário
├── Freelancer: Dashboard → Vagas → Candidaturas → Perfil
├── Empresa: Dashboard → Eventos → Vagas → Perfil
└── Admin: Dashboard → Perfil
```

## 🔐 Sistema de Autenticação

### Contexto de Autenticação
O `AuthContext` gerencia:
- Estado do usuário logado
- Tokens JWT (access e refresh)
- Persistência com AsyncStorage
- Renovação automática de tokens

### Fluxo de Login
1. Usuário insere credenciais
2. API retorna tokens JWT
3. Tokens são salvos no AsyncStorage
4. Usuário é redirecionado para dashboard específico

### Tipos de Usuário
- **Freelancer**: Vinculado automaticamente à Eventix
- **Empresa**: Vinculado à empresa contratante
- **Admin**: Acesso total ao sistema

## 🎨 Design System

### Cores
- **Primária**: #667eea (Azul)
- **Secundária**: #764ba2 (Roxo)
- **Sucesso**: #4CAF50 (Verde)
- **Aviso**: #FF9800 (Laranja)
- **Erro**: #F44336 (Vermelho)

### Componentes
- **Cards**: Bordas arredondadas e sombras
- **Botões**: Gradientes e estados de loading
- **Inputs**: Ícones e validações visuais
- **Navegação**: Abas coloridas por tipo de usuário

## 📱 Telas Implementadas

### 🔐 Autenticação
- **LoginScreen**: Tela de login com design moderno
- **RegisterScreen**: Registro com validações por tipo de usuário

### 👨‍💼 Freelancer
- **FreelancerDashboard**: Dashboard com estatísticas e ações rápidas
- **VagasScreen**: Lista de vagas disponíveis (placeholder)
- **CandidaturasScreen**: Histórico de candidaturas (placeholder)

### 🏢 Empresa
- **EmpresaDashboard**: Dashboard da empresa (placeholder)
- **EventosScreen**: Gerenciamento de eventos (placeholder)
- **VagasEmpresaScreen**: Gerenciamento de vagas (placeholder)

### 👨‍💻 Admin
- **AdminDashboard**: Dashboard administrativo (placeholder)

### 👤 Perfil
- **ProfileScreen**: Perfil do usuário com opção de logout

## 🔧 Configuração da API

### URL da API
O app está configurado para conectar com a API Django em `http://127.0.0.1:8000/api`.

Para alterar a URL da API, edite o arquivo `src/services/api.ts`:

```typescript
export const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // Altere aqui
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Endpoints Utilizados
- `POST /auth/login/` - Login
- `POST /auth/registro/` - Registro
- `GET /auth/empresas/` - Listar empresas
- `GET /auth/perfil/` - Perfil do usuário
- `POST /auth/refresh/` - Renovar token

## 🚀 Como Executar

### Pré-requisitos
- Node.js 16+
- React Native CLI
- Android Studio (para Android)
- Xcode (para iOS - apenas macOS)

### Instalação
```bash
cd mobile
npm install
```

### Android
```bash
npx react-native run-android
```

### iOS
```bash
cd ios && pod install && cd ..
npx react-native run-ios
```

## 🐛 Debugging

### Logs
```bash
# Android
npx react-native log-android

# iOS
npx react-native log-ios
```

### DevTools
- **React Native Debugger**: Para debugging avançado
- **Flipper**: Para inspeção de rede e logs

## 📊 Funcionalidades Futuras

### 🔄 Próximas Implementações
- [ ] Lista de vagas com filtros
- [ ] Sistema de candidaturas
- [ ] Chat entre freelancers e empresas
- [ ] Notificações push
- [ ] Upload de documentos
- [ ] Sistema de avaliações
- [ ] Pagamentos integrados

### 🎯 Melhorias Planejadas
- [ ] Offline mode
- [ ] Cache de dados
- [ ] Animações avançadas
- [ ] Tema escuro
- [ ] Internacionalização
- [ ] Testes automatizados

## 🧪 Testes

### Executar Testes
```bash
npm test
```

### Cobertura de Testes
```bash
npm test -- --coverage
```

## 📱 Build e Deploy

### Android
```bash
cd android
./gradlew assembleRelease
```

### iOS
```bash
cd ios
xcodebuild -workspace EventixMobile.xcworkspace -scheme EventixMobile -configuration Release
```

## 🔧 Configurações de Desenvolvimento

### ESLint
```bash
npm run lint
```

### Prettier
```bash
npx prettier --write src/
```

### TypeScript
```bash
npx tsc --noEmit
```

## 📚 Recursos Úteis

### Documentação
- [React Native](https://reactnative.dev/)
- [React Navigation](https://reactnavigation.org/)
- [React Native Paper](https://callstack.github.io/react-native-paper/)
- [Axios](https://axios-http.com/)

### Ferramentas
- [React Native Debugger](https://github.com/jhen0409/react-native-debugger)
- [Flipper](https://fbflipper.com/)
- [Reactotron](https://github.com/infinitered/reactotron)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para suporte técnico:
- Email: suporte@eventix.com
- Discord: [Link do servidor]
- Documentação: [Link da documentação]

---

**Eventix Mobile** - Conectando talentos e oportunidades! 🎉

