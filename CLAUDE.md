Django 프로젝트 시작 지침

1. conda 환경 생성 및 활성화

conda create -n django_study python=3.12
conda activate django_study

2. Django 설치

pip install django djangorestframework

3. 프로젝트 생성

django-admin startproject 프로젝트명
cd 프로젝트명

4. 앱 생성 (기능 단위로 분리)

python manage.py startapp 앱명

5. 서버 실행

python manage.py runserver
→ http://localhost:8000 확인

FastAPI와 대응 구조 참고

FastAPI (현 프로젝트) Django
apis/ views.py
schemas/ serializers.py (DRF)
models/ models.py
services/ 직접 구현
.env settings.py
나중에 새 프로젝트 팔 때 이 순서대로 따라하면 돼요.
