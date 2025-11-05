"""
Views para PWA - Service Worker e Manifest
"""
from django.http import HttpResponse
from django.conf import settings
from pathlib import Path


def service_worker(request):
    """
    Serve o Service Worker na raiz do domínio (/service-worker.js)
    Necessário para PWA funcionar corretamente
    """
    sw_path = Path(settings.BASE_DIR) / 'static' / 'service-worker.js'
    
    if not sw_path.exists():
        # Tenta no staticfiles também
        sw_path = Path(settings.STATIC_ROOT) / 'service-worker.js'
    
    if sw_path.exists():
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = HttpResponse(content, content_type='application/javascript')
        # Headers importantes para Service Worker
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    return HttpResponse('// Service Worker não encontrado', status=404, content_type='application/javascript')


def manifest_json(request):
    """
    Serve o manifest.json com o Content-Type correto
    """
    manifest_path = Path(settings.BASE_DIR) / 'static' / 'manifest.json'
    
    if not manifest_path.exists():
        manifest_path = Path(settings.STATIC_ROOT) / 'manifest.json'
    
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = HttpResponse(content, content_type='application/manifest+json')
        response['Cache-Control'] = 'public, max-age=3600'
        return response
    
    return HttpResponse('{}', status=404, content_type='application/manifest+json')

