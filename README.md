# Eventix

Apague migrações antigas (se existirem e puder) dos apps recém-criados e o db.sqlite3 (ou use seu Postgres limpo).

python manage.py makemigrations app_eventos api_v01

python manage.py migrate

python manage.py createsuperuser (role pode ser “EMPREGADOR” para administrar)

Testes rápidos:

POST /auth/jwt/create/ (login)

POST /api/signup/freelancer/

POST /api/signup/empresa/

POST /api/eventos/criar/

POST /api/vagas/criar/

GET /api/eventos/<id>/vagas/

POST /api/vagas/candidatar/ (com Bearer de freelancer)

GET /api/candidaturas/minhas/

PATCH /api/candidaturas/<id>/status/ (com Bearer do empregador)

POST /api/alocacoes/criar/

- python -m venv .venv
- git pull origin main
Windows
- .venv\Scripts\activate  
Linux
- source .venv/bin/activate
- railway --version  
- pip freeze > requirements.txt
- pip install -r requirements.txt
- npm i -g @railway/cli
- railway login
- railway link -p 05528686-ab0c-4968-b1c3-f1f824b2bdd8
- railway up
- railway reload
- python manage.py collectstatic
- python manage.py makemigrations  
- python manage.py migrate
- python manage.py createsuperuser
- python manage.py escanear_portas --host 127.0.0.1 --inicio 31400 --fim 31409
- python manage.py extrair_pdf docs/exemplo.pdf
- python manage.py geravagas_fixas
- python manage.py show_urls | findstr motoboy
