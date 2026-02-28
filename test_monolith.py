#!/usr/bin/env python3
"""
Script de demostración automática del chatbot monolítico
Ejecuta conversaciones de prueba sin interacción del usuario
"""

import sys
import subprocess

def run_test_conversation():
    """Ejecuta una conversación de prueba"""
    
    print("\n" + "="*70)
    print("🤖 CHATBOT MONOLITH - DEMOSTRACIÓN AUTOMÁTICA")
    print("="*70 + "\n")
    
    # Importa el chatbot
    sys.path.insert(0, '.')
    from chatbot_monolith import Actor, get_default_brain, SimpleConversationStorage
    
    # Inicializa
    pattern_responses, default_responses = get_default_brain()
    actor = Actor(pattern_responses, default_responses)
    storage = SimpleConversationStorage()
    
    # Conversaciones de prueba
    test_messages = [
        "hello",
        "my name is alice",
        "how are you",
        "i like programming",
        "what is artificial intelligence",
        "help me",
        "thank you",
        "goodbye",
    ]
    
    print("📝 CONVERSACIÓN DE PRUEBA:\n")
    
    session_id = "demo_session"
    
    for msg in test_messages:
        print(f"👤 User: {msg}")
        
        # Procesa mensaje
        response = actor.process(msg)
        
        # Guarda en almacenamiento
        storage.save(session_id, msg, response.text)
        
        # Muestra respuesta
        print(f"🤖 Bot: {response.text}")
        print(f"   Source: {response.source} | Confidence: {response.confidence:.2f}\n")
    
    # Muestra historial
    print("\n" + "="*70)
    print("📊 HISTORIAL GUARDADO")
    print("="*70 + "\n")
    
    history = storage.get_history(session_id)
    for i, interaction in enumerate(history, 1):
        print(f"{i}. USER:  {interaction['user']}")
        print(f"   BOT:   {interaction['bot']}")
        print(f"   TIME:  {interaction['timestamp']}\n")
    
    # Estadísticas
    print("="*70)
    print("📈 ESTADÍSTICAS")
    print("="*70)
    print(f"Total de mensajes procesados: {len(test_messages)}")
    print(f"Sesiones almacenadas: {len(storage.data)}")
    print(f"Total de interacciones guardadas: {sum(len(msgs) for msgs in storage.data.values())}")
    print(f"Archivo de almacenamiento: conversations.json\n")
    
    print("✅ Demostración completada exitosamente!\n")


if __name__ == "__main__":
    try:
        run_test_conversation()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
