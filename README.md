# API Credit Safety Lab

Laboratorio educativo de seguridad para revisar una falla de autorización en un sistema de créditos.

## Contenido

- App Flask original: app.py, templates/index.html y test_app.py.
- Demo pública: https://vxiex11.github.io/api-credit-safety-lab/ en docs/index.html.

> La demo de GitHub Pages es una simulación estática del flujo: no ejecuta Flask, no mantiene sesiones en un servidor y no debe usarse con datos reales. El backend original contiene credenciales y una vulnerabilidad intencional, únicamente para pruebas locales controladas.

## Ejecutar el backend localmente

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python app.py

Después abre http://localhost:5000. No expongas este backend a Internet sin corregir la autorización, retirar las credenciales de ejemplo y configurar secretos seguros.
