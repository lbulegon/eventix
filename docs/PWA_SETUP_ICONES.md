# 📱 Setup de Ícones PWA - Eventix

## ✅ Manifest.json Criado

O arquivo `manifest.json` foi criado com sucesso em `static/manifest.json` e está referenciado no `base.html`.

## 📋 Ícones Necessários

Para completar a implementação do PWA, você precisa gerar os seguintes ícones a partir do logo Eventix (`static/logo_eventix.png`):

### 📁 Estrutura de Diretórios

Crie a pasta `static/icons/` e adicione os seguintes arquivos:

```
static/
└── icons/
    ├── icon-72x72.png
    ├── icon-96x96.png
    ├── icon-128x128.png
    ├── icon-144x144.png
    ├── icon-152x152.png
    ├── icon-192x192.png
    ├── icon-384x384.png
    ├── icon-512x512.png
    ├── icon-maskable-192x192.png
    └── icon-maskable-512x512.png
```

### 🎨 Especificações dos Ícones

#### **Ícones Padrão (purpose: "any")**
- **72x72px** - Para dispositivos Android antigos
- **96x96px** - Para shortcuts e notificações
- **128x128px** - Para Chrome/Edge
- **144x144px** - Para Windows tiles
- **152x152px** - Para iOS/iPad
- **192x192px** - **OBRIGATÓRIO** - Tamanho mínimo para Android
- **384x384px** - Para splash screens
- **512x512px** - **OBRIGATÓRIO** - Tamanho mínimo para Android

#### **Ícones Maskable (purpose: "maskable")**
- **192x192px** - Ícone com padding de 10% (área segura de 172x172px)
- **512x512px** - Ícone com padding de 10% (área segura de 460x460px)

**Nota:** Ícones maskable são usados pelo Android para criar ícones adaptativos. O conteúdo importante deve estar dentro de uma área central (80% do tamanho total).

---

## 🛠️ Como Gerar os Ícones

### **Opção 1: Ferramentas Online (Recomendado)**

1. **PWA Asset Generator** (Mais fácil)
   - Acesse: https://github.com/elegantapp/pwa-asset-generator
   - Ou use: https://www.pwabuilder.com/imageGenerator
   - Faça upload do `logo_eventix.png`
   - Gere todos os tamanhos automaticamente

2. **Real Favicon Generator**
   - Acesse: https://realfavicongenerator.net/
   - Faça upload do logo
   - Configure para PWA
   - Baixe todos os ícones gerados

### **Opção 2: Script Python (Automático)**

Crie um script para redimensionar automaticamente:

```python
from PIL import Image
import os

# Caminho do logo original
logo_path = "static/logo_eventix.png"
output_dir = "static/icons"
os.makedirs(output_dir, exist_ok=True)

# Tamanhos necessários
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

# Abre a imagem
img = Image.open(logo_path)

# Gera ícones padrão
for size in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(f"{output_dir}/icon-{size}x{size}.png")

# Gera ícones maskable (com padding de 10%)
for size in [192, 512]:
    # Cria uma nova imagem com fundo transparente
    maskable = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Calcula o tamanho da área segura (80% do tamanho total)
    safe_size = int(size * 0.8)
    offset = (size - safe_size) // 2
    
    # Redimensiona o logo para a área segura
    logo_resized = img.resize((safe_size, safe_size), Image.Resampling.LANCZOS)
    
    # Cola o logo no centro
    maskable.paste(logo_resized, (offset, offset), logo_resized if logo_resized.mode == 'RGBA' else None)
    
    maskable.save(f"{output_dir}/icon-maskable-{size}x{size}.png")

print("✅ Ícones gerados com sucesso!")
```

### **Opção 3: ImageMagick (Linha de Comando)**

```bash
# Criar diretório
mkdir -p static/icons

# Ícones padrão
for size in 72 96 128 144 152 192 384 512; do
  convert static/logo_eventix.png -resize ${size}x${size} static/icons/icon-${size}x${size}.png
done

# Ícones maskable (com padding)
convert static/logo_eventix.png -resize 153x153 -gravity center -extent 192x192 -background transparent static/icons/icon-maskable-192x192.png
convert static/logo_eventix.png -resize 409x409 -gravity center -extent 512x512 -background transparent static/icons/icon-maskable-512x512.png
```

---

## ✅ Checklist de Implementação

- [x] Manifest.json criado
- [x] Referência ao manifest no base.html
- [x] Meta tags PWA adicionadas
- [ ] Ícones gerados e colocados em `static/icons/`
- [ ] Testar instalação no Chrome/Edge
- [ ] Testar instalação no Android
- [ ] Testar instalação no iOS Safari

---

## 🧪 Como Testar

### **Chrome/Edge (Desktop)**
1. Abra o DevTools (F12)
2. Vá para a aba "Application"
3. Verifique se o manifest aparece em "Manifest"
4. Verifique se todos os ícones estão carregando
5. Teste o botão "Install" na barra de endereços

### **Android (Chrome)**
1. Abra o site no Chrome
2. Toque no menu (três pontos)
3. Verifique se aparece "Adicionar à tela inicial"
4. Instale e teste

### **iOS Safari**
1. Abra o site no Safari
2. Toque no botão de compartilhar
3. Selecione "Adicionar à Tela de Início"
4. Teste o ícone e a experiência

---

## 📝 Notas Importantes

1. **Ícones Maskable:** Essenciais para Android moderno. O conteúdo importante deve estar na área central (80% do tamanho).

2. **Formato PNG:** Todos os ícones devem ser PNG com transparência (quando aplicável).

3. **Apple Touch Icon:** O `icon-192x192.png` será usado como fallback para iOS.

4. **Atualização:** Após adicionar os ícones, limpe o cache do navegador e teste novamente.

---

## 🔗 Referências

- [Web App Manifest - MDN](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [PWA Checklist - Google](https://web.dev/pwa-checklist/)
- [Maskable Icons - Android](https://web.dev/maskable-icon/)

---

**Próximo passo:** Gerar os ícones e adicionar ao diretório `static/icons/` 🎨

