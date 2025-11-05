"""
Script para gerar ícones PWA a partir do logo Eventix
Requer: pip install Pillow
"""
from PIL import Image
import os
from pathlib import Path

# Configurações
BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "static" / "logo_eventix.png"
OUTPUT_DIR = BASE_DIR / "static" / "icons"

def gerar_icones():
    """Gera todos os ícones necessários para PWA"""
    
    # Verifica se o logo existe
    if not LOGO_PATH.exists():
        print(f"❌ Erro: Logo não encontrado em {LOGO_PATH}")
        print("   Certifique-se de que o arquivo logo_eventix.png existe em static/")
        return False
    
    # Cria o diretório de saída
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Diretório de saída: {OUTPUT_DIR}")
    
    # Abre a imagem original
    try:
        img = Image.open(LOGO_PATH)
        print(f"✅ Logo carregado: {img.size[0]}x{img.size[1]}px")
    except Exception as e:
        print(f"❌ Erro ao abrir logo: {e}")
        return False
    
    # Tamanhos necessários para ícones padrão
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    print("\n🎨 Gerando ícones padrão...")
    for size in sizes:
        try:
            # Redimensiona mantendo a proporção e qualidade
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Salva como PNG
            output_path = OUTPUT_DIR / f"icon-{size}x{size}.png"
            resized.save(output_path, "PNG", optimize=True)
            print(f"   ✅ {output_path.name}")
        except Exception as e:
            print(f"   ❌ Erro ao gerar {size}x{size}: {e}")
    
    print("\n🎨 Gerando ícones maskable (com padding)...")
    # Tamanhos maskable (com área segura de 80%)
    maskable_sizes = [192, 512]
    
    for size in maskable_sizes:
        try:
            # Cria uma nova imagem com fundo transparente
            maskable = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            
            # Calcula o tamanho da área segura (80% do tamanho total)
            safe_size = int(size * 0.8)
            offset = (size - safe_size) // 2
            
            # Redimensiona o logo para a área segura
            logo_resized = img.resize((safe_size, safe_size), Image.Resampling.LANCZOS)
            
            # Converte para RGBA se necessário
            if logo_resized.mode != 'RGBA':
                logo_resized = logo_resized.convert('RGBA')
            
            # Cola o logo no centro
            maskable.paste(logo_resized, (offset, offset), logo_resized)
            
            # Salva
            output_path = OUTPUT_DIR / f"icon-maskable-{size}x{size}.png"
            maskable.save(output_path, "PNG", optimize=True)
            print(f"   ✅ {output_path.name} (área segura: {safe_size}x{safe_size}px)")
        except Exception as e:
            print(f"   ❌ Erro ao gerar maskable {size}x{size}: {e}")
    
    print(f"\n✅ Ícones gerados com sucesso em {OUTPUT_DIR}")
    print(f"   Total de ícones: {len(sizes) + len(maskable_sizes)}")
    
    return True

if __name__ == "__main__":
    print("🚀 Gerador de Ícones PWA - Eventix\n")
    
    if gerar_icones():
        print("\n🎉 Pronto! Agora você pode testar o PWA.")
        print("\n📝 Próximos passos:")
        print("   1. Teste o manifest.json no navegador")
        print("   2. Verifique se os ícones estão aparecendo")
        print("   3. Teste a instalação do PWA")
    else:
        print("\n❌ Falha ao gerar ícones. Verifique os erros acima.")

