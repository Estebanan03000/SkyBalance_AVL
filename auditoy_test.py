import sys
import os
from datetime import datetime

# Agregar la carpeta App al path
sys.path.append(os.path.join(os.path.dirname(__file__), "App"))

from Models.Flight import Flight
from Services.Flight_Service import Flight_Service

# ============================
# 1. Crear servicio en modo Stress
# ============================
service = Flight_Service(mode="Stress")

# ============================
# 2. Insertar vuelos de prueba
# ============================
flights = [
    Flight(10, "Bogota", "Madrid", datetime.now(), 500, 650, 120, 0.19, False),
    Flight(20, "Cali", "Paris", datetime.now(), 450, 600, 100, 0.19, False),
    Flight(30, "Medellin", "Roma", datetime.now(), 550, 700, 130, 0.19, False),
    Flight(40, "Barranquilla", "Berlin", datetime.now(), 480, 620, 110, 0.19, False),
    Flight(50, "Cartagena", "Lisboa", datetime.now(), 530, 680, 125, 0.19, False),
]

for flight in flights:
    service.create_flight(flight)

# ============================
# 3. Ejecutar auditoría AVL
# ============================
nodes = service.Auditory_System("Stress")
report = service.Auditory_report(nodes)

# ============================
# 4. Mostrar reporte
# ============================
print("\n=== AVL AUDIT REPORT (STRESS MODE) ===\n")

for item in report:
    print(f"Nodo {item['Node']}")
    print(f"- Altura real: {item['Real Height']}")
    print(f"- Balance factor: {item['Balance Factor']}")
    print(f"- Estado AVL: {item['AVL Status']}")
    print()