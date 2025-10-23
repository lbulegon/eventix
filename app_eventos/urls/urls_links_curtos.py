from django.urls import path
from app_eventos import views_links_curtos

app_name = 'links_curtos'

urlpatterns = [
    # URLs curtas para vagas
    path('v/<int:vaga_id>/', views_links_curtos.redirecionar_vaga, name='link_curto_vaga'),
    path('e/<int:evento_id>/', views_links_curtos.redirecionar_evento, name='link_curto_evento'),
    
    # URLs curtas para freelancers
    path('f/<int:freelancer_id>/', views_links_curtos.redirecionar_freelancer, name='link_curto_freelancer'),
    
    # Página de fallback para web
    path('vagas/<int:vaga_id>/', views_links_curtos.vaga_web, name='vaga_web'),
    path('eventos/<int:evento_id>/', views_links_curtos.evento_web, name='evento_web'),
]
