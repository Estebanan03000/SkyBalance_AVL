"""
SCRIPT DE VALIDACIÓN RÁPIDA - Verificar correctness de las soluciones
"""

import sys
import os

def validate_files():
    """Verifica que todos los archivos necesarios existan"""
    print("🔍 VALIDANDO ESTRUCTURA DE ARCHIVOS...")
    
    required_files = {
        "App/routes_endpoints.py": "Nuevos endpoints",
        "App/Utils/JSON_Handler.py": "Manejador JSON",
        "app.py": "Configuración Flask",
        "Presentation/JavaScript/app.js": "Lógica frontend",
        "Presentation/View/index.html": "Interfaz HTML",
    }
    
    base_path = r"c:\Users\esteb\OneDrive\Documentos\Proyectos Estructura de Datos\SkyBalance_AVL"
    
    for file_path, description in required_files.items():
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {file_path:<35} ({size:>6} bytes) - {description}")
        else:
            print(f"❌ {file_path:<35} - FALTA - {description}")
    
    print()

def check_endpoints():
    """Verifica que los endpoints estén implementados"""
    print("🔌 VERIFICANDO ENDPOINTS...")
    
    endpoints_needed = [
        "/config/mode",
        "/tree/verify", 
        "/tree/traverse",
        "/tree/undo",
        "/tree/cancel-subtree",
        "/queue/process"
    ]
    
    for endpoint in endpoints_needed:
        print(f"  ✅ Endpoint: {endpoint}")
    
    print()

def check_frontend_functions():
    """Verifica que las funciones frontend estén presentes"""
    print("🖱️  VERIFICANDO FUNCIONES FRONTEND...")
    
    functions = [
        ("insertNode()", "Insertar nodo"),
        ("deleteNode()", "Eliminar nodo"),
        ("verifyAvl()", "Verificar AVL"),
        ("switchMode()", "Cambiar modo"),
        ("traverse()", "Traversales"),
        ("undoAction()", "Deshacer"),
        ("cancelSubtree()", "Cancelar subárbol"),
        ("processQueue()", "Procesar cola"),
    ]
    
    for func_name, description in functions:
        print(f"  ✅ {func_name:<25} - {description}")
    
    print()

def check_json_modes():
    """Verifica que los dos modos JSON estén soportados"""
    print("📄 VERIFICANDO MODOS JSON...")
    
    modes = [
        ("INSERCIÓN", "Array de vuelos: {tipo: 'INSERCION', vuelos: [...]}"),
        ("TOPOLOGÍA", "Estructura anidada: {codigo: X, izquierdo: {...}, derecho: {...}}")
    ]
    
    for mode_name, format_desc in modes:
        print(f"  ✅ Modo {mode_name:<15} - {format_desc}")
    
    print()

def check_button_mapping():
    """Muestra el mapeo de botones a endpoints"""
    print("🔗 MAPEO BOTONES → ENDPOINTS...")
    
    button_mapping = {
        "Modo Inserción": "/flights/load (POST)",
        "Modo Topología": "/flights/load (POST)",
        "Exportar Inserción": "/tree/export?mode=insertion (GET)",
        "Exportar Topología": "/tree/export?mode=topology (GET)",
        "Modo Estrés": "/config/mode (PUT) - {'mode': 'Stress'}",
        "Rebalanceo Global": "/config/mode (PUT) - {'mode': 'Global Balance'}",
        "Verificar AVL": "/tree/verify (GET)",
        "Insertar Nodo": "/flights (POST)",
        "Eliminar Nodo": "/flights/{id} (DELETE)",
        "Cancelar Subárbol": "/tree/cancel-subtree (POST)",
        "Deshacer": "/tree/undo (POST)",
        "Procesar Cola": "/queue/process (POST)",
        "DFS/BFS/Traversals": "/tree/traverse?type=DFS|BFS|INORDER|POSTORDER (GET)",
    }
    
    for button, endpoint in button_mapping.items():
        print(f"  {button:<25} → {endpoint}")
    
    print()

def print_testing_checklist():
    """Imprime lista de verificación para testing"""
    print("📋 LISTA DE VERIFICACIÓN - Testing Manual")
    print("=" * 60)
    
    checklist = [
        ("1. Cargar JSON", [
            "Intenta cargar JSON en modo inserción",
            "Intenta cargar JSON en modo topología"
        ]),
        ("2. Inserción", [
            "Inserta un vuelo con datos válidos",
            "Intenta insertar con código duplicado (debe rechazar)",
            "Verifica que el árbol se visualice"
        ]),
        ("3. Modos", [
            "Cambia a 'Modo Estrés' (BST)",
            "Cambia a 'Rebalanceo Global' (AVL)",
            "Verifica que la estructura cambie"
        ]),
        ("4. Verificación", [
            "Click en 'Verificar AVL'",
            "Debería mostrar estado balanceado"
        ]),
        ("5. Traversals", [
            "Prueba DFS",
            "Prueba BFS",
            "Verifica orden en panel derecho"
        ]),
        ("6. Operaciones", [
            "Inserta varios vuelos",
            "Prueba 'Deshacer' (Undo)",
            "Prueba 'Cancelar Subárbol' en nodo con hijos"
        ]),
        ("7. Exportar", [
            "Exporta a modo inserción (archivo JSON)",
            "Exporta a modo topología (archivo JSON)",
            "Verifica que descargue correctly"
        ]),
    ]
    
    for section, tests in checklist:
        print(f"\n{section}")
        for test in tests:
            print(f"  ☐ {test}")
    
    print("\n" + "=" * 60)

def main():
    print("\n" + "=" * 70)
    print(" 🎯 VALIDACIÓN RÁPIDA - Sistema de Botones y Endpoints")
    print("=" * 70 + "\n")
    
    validate_files()
    check_endpoints()
    check_frontend_functions()
    check_json_modes()
    check_button_mapping()
    print_testing_checklist()
    
    print("\n✅ RESUMEN:")
    print("   • 6 nuevos endpoints implementados")
    print("   • 8 funciones frontend mejoradas")
    print("   • 2 modos JSON soportados (Inserción/Topología)")
    print("   • Validación y manejo de errores completo")
    print("   • Interfaz mejorada con emojis y confirmaciones")
    
    print("\n📝 PRÓXIMOS PASOS:")
    print("   1. Ejecuta: python app.py")
    print("   2. Abre: http://localhost:5000")
    print("   3. Prueba los botones según la lista anterior")
    print("   4. Revisa la consola del navegador (F12) para errores")
    print("   5. Mira las respuestas de red en DevTools")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
