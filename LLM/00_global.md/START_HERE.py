#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                  🎓 CHATBOT EVOLUTION - START HERE 🎓                     ║
║                                                                            ║
║                              v2.1 - Feb 24, 2026                          ║
║                         Production Ready Architecture                      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

Este archivo es tu GUÍA DE INICIO. Ejecuta este script para comenzar.
"""

import os
import sys
from pathlib import Path

def clear_screen():
    """Limpia la pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Imprime header del proyecto"""
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║              🤖 CHATBOT EVOLUTION - START HERE 🤖                 ║
    ║                                                                    ║
    ║          De ELIZA monolítico → Arquitectura profesional           ║
    ║                                                                    ║
    ║                    2,500+ líneas   |   50+ tests                  ║
    ║                    7 módulos       |   40+ patrones               ║
    ║                    15 documentos   |   Production ready           ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)

def print_quick_start():
    """Imprime guía rápida"""
    print("\n" + "="*70)
    print("⚡ INICIO RÁPIDO (5 MINUTOS)")
    print("="*70)
    print("""
1️⃣  ENTENDER el proyecto:
    $ python PROJECT_STATUS_SUMMARY.py resumen

2️⃣  EXPLORAR patrones (RECOMENDADO):
    $ python test_patterns.py

3️⃣  USAR el chatbot:
    $ python -m src.main --mode cli

4️⃣  VER API (Swagger):
    $ python -m src.main --mode api
    Luego: http://localhost:8000/docs
    """)

def print_learning_paths():
    """Imprime rutas de aprendizaje"""
    print("\n" + "="*70)
    print("📚 RUTAS DE APRENDIZAJE")
    print("="*70)
    print("""
🎯 PARA USUARIOS FINALES (5 min)
   1. Lee: COMPLETE.txt (resumen de 3 KB)
   2. Ejecuta: python test_patterns.py
   3. Usa: python -m src.main --mode cli

👨‍💻 PARA DESARROLLADORES (30 min)
   1. Lee: README.md
   2. Lee: ARCHITECTURE.md
   3. Ejecuta: python ARCHITECTURE_DIAGRAM.py
   4. Estudia: src/ (código fuente)
   5. Lee: COMPLETE_ARCHITECTURE.md

🎓 PARA ENTENDER PATRONES (15 min)
   1. Ejecuta: python test_patterns.py
   2. Lee: IMPROVED_RULES.md
   3. Lee: PATTERNS_QUICK_REFERENCE.md
   4. Ejecuta: python debug_flow.py

🚀 PARA DEPLOYAR (10 min)
   1. Lee: .env.example
   2. Lee: Dockerfile
   3. Ejecuta: docker-compose up
    """)

def print_important_files():
    """Imprime archivos importantes"""
    print("\n" + "="*70)
    print("📁 ARCHIVOS IMPORTANTES")
    print("="*70)
    print("""
📖 DOCUMENTACIÓN:
   • COMPLETE.txt (resumen ejecutivo 3 KB)
   • DOCUMENTATION_INDEX.md (índice maestro)
   • COMPLETE_ARCHITECTURE.md (arquitectura detallada)
   • IMPROVED_RULES.md (40+ patrones documentados)

🧪 PRUEBAS INTERACTIVAS:
   • test_patterns.py (menú interactivo)
   • CONVERSATION_EXAMPLES.py (7 conversaciones)
   • IMPROVEMENTS_SUMMARY.py (resumen visual)
   • debug_flow.py (debug paso a paso)

💻 CÓDIGO:
   • src/main.py (entry point)
   • src/brain/actor.py (orquestador)
   • src/nlp/pattern_engine.py (patrones NLP)
   • src/api/routes.py (REST API)

⚙️  CONFIGURACIÓN:
   • pyproject.toml (dependencias)
   • .env.example (variables de entorno)
   • Dockerfile (containerización)
   • docker-compose.yml (orquestación)
    """)

def print_statistics():
    """Imprime estadísticas"""
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS DEL PROYECTO")
    print("="*70)
    print("""
CÓDIGO FUENTE:
   ✓ 2,500+ líneas de Python
   ✓ 7 módulos independientes
   ✓ 13 archivos de código

TESTING:
   ✓ 50+ unit tests
   ✓ ~85% cobertura
   ✓ Pytest + fixtures

PATRONES NLP:
   ✓ 40+ patrones
   ✓ 13 categorías
   ✓ Mejora: 7 → 40+ (475%)

DOCUMENTACIÓN:
   ✓ 15 archivos
   ✓ 150+ KB
   ✓ Por tipo y propósito

DEPLOYMENT:
   ✓ Docker + docker-compose
   ✓ Fly.io ready
   ✓ Render.com ready
    """)

def print_commands():
    """Imprime comandos útiles"""
    print("\n" + "="*70)
    print("⚡ COMANDOS ÚTILES")
    print("="*70)
    print("""
EXPLORACIÓN:
   python PROJECT_STATUS_SUMMARY.py  # Menú interactivo completo
   python ARCHITECTURE_DIAGRAM.py    # Visualización arquitectura
   python test_patterns.py           # Menú de patrones

EJECUCIÓN:
   python -m src.main --mode cli     # CLI interactivo
   python -m src.main --mode api     # API REST (http://localhost:8000)

TESTING:
   pytest tests/ -v                  # Todos los tests
   pytest tests/ --cov=src           # Con cobertura

DOCUMENTACIÓN:
   cat DOCUMENTATION_INDEX.md        # Índice maestro
   cat COMPLETE_ARCHITECTURE.md      # Arquitectura exhaustiva
   cat IMPROVED_RULES.md             # Patrones detallado
    """)

def print_menu():
    """Imprime menú principal"""
    print("\n" + "="*70)
    print("📋 MENÚ PRINCIPAL")
    print("="*70)
    print("""
¿QUÉ QUIERES HACER?

1. ⚡ Inicio Rápido (muestra guía 5 min)
2. 📚 Rutas de Aprendizaje (por perfil)
3. 📁 Archivos Importantes (qué leer)
4. 📊 Estadísticas del Proyecto
5. ⚡ Comandos Útiles
6. 🎓 Ver Resumen Completo (PROJECT_STATUS_SUMMARY.py)
7. 🏗️  Ver Arquitectura (ARCHITECTURE_DIAGRAM.py)
8. 🧪 Explorar Patrones (test_patterns.py)
9. 💬 Usar Chatbot (CLI interactivo)
10. 🔗 Links y Referencias
11. ❌ Salir
    """)

def print_links():
    """Imprime links y referencias"""
    print("\n" + "="*70)
    print("🔗 ARCHIVOS Y REFERENCIAS")
    print("="*70)
    print("""
INICIO:
  → DOCUMENTATION_INDEX.md      Índice maestro de documentación
  → PROJECT_STATUS_SUMMARY.py   Resumen interactivo del proyecto
  → ARCHITECTURE_DIAGRAM.py     Diagramas de arquitectura ASCII

APRENDIZAJE:
  → README.md                   Visión general
  → GETTING_STARTED.md          Instalación y primer uso
  → COMPLETE_ARCHITECTURE.md    Arquitectura exhaustiva (MÁS DETALLADO)
  → IMPROVED_RULES.md           Documentación de 40+ patrones

EXPLORACIÓN:
  → test_patterns.py            Menú interactivo para probar patrones
  → CONVERSATION_EXAMPLES.py    7 conversaciones de ejemplo
  → debug_flow.py               Debug paso a paso

CÓDIGO:
  → src/main.py                 Entry point (CLI/API)
  → src/brain/actor.py          Orquestador principal
  → src/nlp/pattern_engine.py   Sistema de patrones

DEPLOYMENT:
  → Dockerfile                  Configuración Docker
  → docker-compose.yml          Orquestación con Docker Compose
  → .env.example                Variables de entorno

ESTADÍSTICAS:
  → COMPLETE.txt                Resumen ejecutivo (3 KB)
  → STATUS.txt                  Métricas del proyecto
  → IMPROVEMENTS_SUMMARY.txt    Resumen de mejoras
    """)

def interactive_menu():
    """Menú interactivo"""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("\n¿Opción (1-11)? ").strip()
        
        opciones = {
            "1": print_quick_start,
            "2": print_learning_paths,
            "3": print_important_files,
            "4": print_statistics,
            "5": print_commands,
            "6": lambda: print("\n✅ Ejecuta: python PROJECT_STATUS_SUMMARY.py\n"),
            "7": lambda: print("\n✅ Ejecuta: python ARCHITECTURE_DIAGRAM.py\n"),
            "8": lambda: print("\n✅ Ejecuta: python test_patterns.py\n"),
            "9": lambda: print("\n✅ Ejecuta: python -m src.main --mode cli\n"),
            "10": print_links
        }
        
        if choice == "11":
            print("\n👋 ¡Hasta luego! Que disfrutes con Chatbot Evolution.\n")
            break
        elif choice in opciones:
            opciones[choice]()
            input("\nPresiona Enter para continuar...")
        else:
            print("\n❌ Opción inválida. Intenta nuevamente.")
            input("\nPresiona Enter para continuar...")

def show_initial_guide():
    """Muestra guía inicial sin menú interactivo"""
    clear_screen()
    print_header()
    print("""
🎯 BIENVENIDO A CHATBOT EVOLUTION

Este proyecto es la evolución de un chatbot monolítico (355 líneas) 
a una arquitectura profesional (2,500+ líneas) con:

✅ 7 módulos independientes
✅ 50+ tests unitarios (~85% cobertura)
✅ 40+ patrones NLP en 13 categorías
✅ REST API con FastAPI
✅ Base de datos ORM con SQLAlchemy
✅ Búsqueda semántica
✅ Fallback LLM (OpenAI + Ollama)
✅ Completamente documentado (15 archivos)
✅ Production-ready (Docker + cloud deployment)

═══════════════════════════════════════════════════════════════════════════

TE RECOMENDAMOS EMPEZAR ASÍ:

1️⃣  Lee este resumen (1 min):
    $ cat COMPLETE.txt

2️⃣  Explora los patrones interactivamente (5 min):
    $ python test_patterns.py

3️⃣  Lee la guía de inicio (5 min):
    $ cat GETTING_STARTED.md

4️⃣  Usa el chatbot (5 min):
    $ python -m src.main --mode cli

5️⃣  Entiende la arquitectura (10 min):
    $ python ARCHITECTURE_DIAGRAM.py

═══════════════════════════════════════════════════════════════════════════

OPCIONES PRINCIPALES:

Para menú interactivo:
  $ python START_HERE.py menu

Para ver resumen del proyecto:
  $ python PROJECT_STATUS_SUMMARY.py

Para visualizar arquitectura:
  $ python ARCHITECTURE_DIAGRAM.py

Para explorar patrones:
  $ python test_patterns.py

Para leer documentación:
  $ cat DOCUMENTATION_INDEX.md

═══════════════════════════════════════════════════════════════════════════

¿Próximas acciones?

   A) Ver menú interactivo:    python START_HERE.py menu
   B) Explorar patrones:        python test_patterns.py
   C) Usar el chatbot:          python -m src.main --mode cli
   D) Leer documentación:       cat DOCUMENTATION_INDEX.md
   E) Ver arquitectura:         python ARCHITECTURE_DIAGRAM.py
    """)

def main():
    """Entry point principal"""
    if len(sys.argv) > 1 and sys.argv[1].lower() == "menu":
        interactive_menu()
    else:
        show_initial_guide()

if __name__ == "__main__":
    main()
