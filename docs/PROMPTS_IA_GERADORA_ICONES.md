# 🎨 Prompts para IA Geradora de Imagens - Ícones PWA Eventix

Este documento contém prompts completos e otimizados para usar em IAs geradoras de imagens (DALL-E, Midjourney, Stable Diffusion, Leonardo.ai, etc.) para criar ou ajustar os ícones do Eventix para PWA.

---

## 📋 Informações do Projeto

- **Nome:** Eventix
- **Tagline:** "Organização é o espetáculo"
- **Tema:** Gestão de eventos, produção, organização
- **Cores principais:** Azul (#0d6efd), Branco
- **Estilo:** Moderno, profissional, minimalista

---

## 🎯 Prompt Base (Versão Completa)

### **Para criar/ajustar o logo principal:**

```
Crie um ícone de aplicativo PWA moderno e profissional para "Eventix", uma plataforma de gestão de eventos.

ESPECIFICAÇÕES:
- Tema: Eventos, organização, bilhetes, calendário
- Elemento principal: Inclua um ícone de bilhete (🎟️) ou calendário de forma estilizada
- Estilo: Minimalista, flat design, moderno, profissional
- Cores: Azul primário (#0d6efd) como cor principal, fundo branco ou transparente
- Tipografia: Se incluir texto, use fonte moderna e legível (pode ser apenas "E" ou "EX" estilizado)
- Formato: Quadrado, proporção 1:1
- Estilo visual: Similar a ícones de apps modernos como Google Calendar, Eventbrite, mas com identidade única
- Contraste: Alto contraste para legibilidade em diferentes fundos
- Detalhes: Evite elementos muito pequenos ou complexos que se percam em tamanhos pequenos

CONTEXTO:
- É para um Progressive Web App (PWA)
- Precisa funcionar bem em tamanhos de 72x72px até 512x512px
- Deve ser reconhecível mesmo em tamanho pequeno
- Usado em dispositivos móveis e desktop

RESTRIÇÕES:
- Não use gradientes complexos (mantenha simples)
- Evite muitos detalhes ou elementos pequenos
- Mantenha o design limpo e minimalista
- Certifique-se de que funciona bem sobre fundo claro e escuro
```

---

## 🎨 Prompts Específicos por Tipo de Ícone

### **1. Ícone Padrão (Purpose: "any")**

```
PROMPT COMPLETO:

Crie um ícone de aplicativo quadrado para "Eventix" - plataforma de gestão de eventos.

REQUISITOS VISUAIS:
- Tamanho: 512x512 pixels (proporção 1:1)
- Estilo: Flat design moderno, minimalista
- Elemento central: Bilhete de evento estilizado (🎟️) ou calendário com marca de check
- Cor principal: Azul vibrante (#0d6efd ou similar)
- Fundo: Branco sólido ou transparente
- Texto opcional: Letra "E" estilizada ou "EX" como elemento decorativo (não texto legível pequeno)
- Bordas: Cantos ligeiramente arredondados (10-15% de radius)
- Sombras: Nenhuma ou muito suave
- Contraste: Alto contraste entre elementos e fundo

ESTILO DE REFERÊNCIA:
- Similar a ícones de apps como: Google Calendar, Eventbrite, Asana
- Design profissional e confiável
- Moderno mas atemporal

CONTEXTO TÉCNICO:
- Será usado em tamanhos de 72px até 512px
- Precisa ser legível em todos os tamanhos
- Deve funcionar bem sobre fundos claros e escuros
- Para Progressive Web App (PWA)

GARANTIR:
- Design simples e reconhecível
- Sem elementos muito pequenos
- Cores vibrantes e contrastantes
- Funciona bem em escala pequena
```

---

### **2. Ícone Maskable (Purpose: "maskable")**

```
PROMPT COMPLETO:

Crie um ícone maskable para PWA Android do "Eventix" - plataforma de gestão de eventos.

REQUISITOS ESPECÍFICOS MASKABLE:
- Tamanho: 512x512 pixels
- Área segura: O conteúdo importante deve estar centralizado em uma área de 410x410 pixels (80% do tamanho total)
- Margem: 51 pixels de padding em todos os lados (10% do tamanho)
- Elemento central: Bilhete de evento estilizado ou calendário, centralizado
- Fundo: Pode estender até as bordas, mas o conteúdo principal deve estar na área central
- Cores: Azul (#0d6efd) como cor principal, com bom contraste

ESTILO VISUAL:
- Design que funcione bem quando cortado em diferentes formas (círculo, quadrado com cantos arredondados, etc.)
- Elemento central bem definido e reconhecível
- Fundo pode ter gradiente suave ou cor sólida
- Evite elementos importantes nas bordas (últimos 10%)

CONTEXTO:
- Android usa este ícone para criar ícones adaptativos
- O sistema pode cortar/mascarar o ícone em diferentes formas
- O conteúdo central permanece sempre visível

GARANTIR:
- Conteúdo principal ocupando 60-70% do centro
- Margens de segurança respeitadas
- Design que funcione quando cortado
- Alto contraste
```

---

## 🔄 Prompt para Ajustar Logo Existente

### **Se você já tem um logo e quer ajustá-lo:**

```
Ajuste e otimize este logo existente do Eventix para uso como ícone de Progressive Web App (PWA).

LOGO ORIGINAL:
[Faça upload do logo_eventix.png ou descreva o logo atual]

AJUSTES NECESSÁRIOS:
- Formato: Quadrado perfeito (1:1)
- Tamanho: 512x512 pixels
- Fundo: Branco sólido ou transparente
- Otimização: Simplifique elementos se necessário para funcionar bem em tamanhos pequenos
- Contraste: Aumente o contraste se necessário
- Espaçamento: Adicione padding adequado (10-15% das bordas) se o logo atual vai até as bordas
- Cores: Mantenha as cores originais mas garanta que sejam vibrantes
- Detalhes: Remova elementos muito pequenos que não aparecerão em 72x72px

VERSÕES NECESSÁRIAS:
1. Versão padrão (conteúdo pode ir até as bordas)
2. Versão maskable (conteúdo importante centralizado com 10% de margem)

CONTEXTO:
- Será usado em dispositivos móveis e desktop
- Precisa ser reconhecível de 72px até 512px
- Para instalação como PWA
```

---

## 📐 Prompt para Versões Específicas de Tamanho

### **Para gerar cada tamanho individualmente:**

```
Gere uma versão específica de 192x192 pixels do ícone Eventix para PWA.

ESPECIFICAÇÕES TÉCNICAS:
- Tamanho exato: 192x192 pixels
- Resolução: Alta qualidade, nítida, sem pixelização
- Formato: PNG com transparência
- Elemento: Bilhete de evento estilizado ou calendário
- Cor: Azul (#0d6efd) como cor principal
- Fundo: Transparente ou branco sólido
- Estilo: Minimalista, flat design, sem gradientes complexos

OTIMIZAÇÃO PARA TAMANHO:
- Design simplificado mas reconhecível
- Elementos principais bem definidos
- Alto contraste
- Sem detalhes muito pequenos

CONTEXTO:
- Usado em dispositivos Android
- Tamanho mínimo obrigatório para PWA
- Deve ser legível e atraente
```

---

## 🎨 Prompt para Estilo Específico

### **Se quiser um estilo mais específico:**

```
Crie um ícone PWA para "Eventix" seguindo este estilo específico:

ESTILO VISUAL:
- Design: Material Design 3.0 ou iOS Human Interface Guidelines
- Tipo: Flat design com leve profundidade (sombra sutil)
- Cores: Azul primário (#0d6efd), branco, acentos em verde (#198754)
- Elementos: Bilhete de evento estilizado com ícone de calendário integrado
- Tipografia: Se incluir letra, use fonte sans-serif moderna (Inter ou Poppins)

ELEMENTOS VISUAIS:
- Ícone principal: Bilhete de evento com bordas arredondadas
- Elemento secundário: Marca de check ou estrela sutil
- Fundo: Branco com leve sombra ou gradiente suave azul claro
- Bordas: Cantos arredondados (20px radius)

CONTEXTO:
- Plataforma de gestão de eventos
- Público: Profissionais de eventos, produtores, freelancers
- Tom: Profissional, confiável, moderno
- Diferencial: Organização e eficiência

QUALIDADE:
- Alta resolução
- Vetorizável (se possível)
- Escalável
- Profissional
```

---

## 🛠️ Dicas de Uso em Diferentes IAs

### **DALL-E (ChatGPT)**
- Use o prompt completo
- Adicione: "PNG, transparent background, high resolution, 512x512 pixels"
- Pode pedir variações: "Crie 4 variações com diferentes estilos"

### **Midjourney**
- Use: `/imagine prompt: [seu prompt] --ar 1:1 --v 6`
- Adicione: `--style raw` para estilo mais limpo
- Use `--q 2` para maior qualidade

### **Leonardo.ai / Stable Diffusion**
- Use o prompt completo
- Configure: Aspect Ratio 1:1, Resolution 512x512
- Use negative prompt: "text, complex details, blurry, low quality"

### **Adobe Firefly**
- Use o prompt completo
- Selecione: "Square" aspect ratio
- Use "Remove Background" para versão transparente

---

## 📝 Checklist do Prompt Ideal

Antes de enviar, certifique-se de que seu prompt inclui:

- [ ] Tamanho específico (ex: 512x512px)
- [ ] Estilo visual desejado (flat, moderno, minimalista)
- [ ] Elementos principais (bilhete, calendário, etc.)
- [ ] Cores principais (#0d6efd, branco)
- [ ] Contexto de uso (PWA, mobile, desktop)
- [ ] Requisitos técnicos (transparente, alto contraste)
- [ ] Restrições (sem elementos pequenos, sem gradientes complexos)

---

## 🔄 Processo Recomendado

1. **Primeira tentativa:** Use o "Prompt Base (Versão Completa)"
2. **Ajuste:** Se não ficar bom, especifique o que mudar
3. **Refine:** Peça ajustes específicos (cores, tamanho de elementos, espaçamento)
4. **Gere variações:** Crie 3-5 versões e escolha a melhor
5. **Otimize:** Use ferramentas de edição para ajustes finais se necessário

---

## 💡 Exemplo de Conversa com IA

```
Você: [Use o Prompt Base Completo]

IA: [Gera primeira versão]

Você: "Ajuste o ícone: o bilhete está muito grande, reduza para 70% do tamanho. 
      Adicione mais espaçamento nas bordas. Mantenha o azul mas torne-o um pouco mais vibrante. 
      O fundo deve ser branco sólido, não transparente."

IA: [Gera versão ajustada]

Você: "Perfeito! Agora crie uma versão maskable deste mesmo design, 
      onde o bilhete está centralizado em uma área de 410x410 pixels 
      com 51 pixels de padding em todas as bordas."
```

---

## 🎯 Resumo: Prompt Mais Simples e Direto

Se preferir algo mais direto:

```
Crie um ícone de aplicativo 512x512 pixels para "Eventix" - plataforma de gestão de eventos. 
Estilo: Minimalista, flat design, azul (#0d6efd) como cor principal, fundo branco. 
Elemento central: Bilhete de evento estilizado. 
Alto contraste, sem elementos pequenos, funciona bem em tamanhos de 72px até 512px. 
Para Progressive Web App (PWA), moderno e profissional.
```

---

**Última atualização:** Janeiro 2025

