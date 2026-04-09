import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App"))
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "Models")
)
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "Services")
)

from Models.Flight import Flight
from Services.Flight_Service import Flight_Service

# El resto del código igual...
service = Flight_Service()
service.setMaxDepth(0)

f1 = Flight(10, "Bogotá", "Medellín", "08:00", 100.0, 120.0, 150, 0.1, False)
f2 = Flight(5, "Cali", "Bogotá", "10:00", 80.0, 90.0, 100, 0.0, True)
f3 = Flight(15, "Medellín", "Cali", "12:00", 110.0, 130.0, 120, 0.05, False)

service.create_flight(f1)
service.create_flight(f2)
service.create_flight(f3)

print("=== maxDepth = 0 ===")
for f in service.get_all_flights():
    depth = service._tree.getNodeDepth(f)
    print(
        f"ID: {f.getValue()} | Depth: {depth} | Critical: {f.getIsCritical()} | FinalPrice: {f.getFinalPrice()}"
    )

print("\n=== maxDepth = 1 ===")
service.setMaxDepth(1)
for f in service.get_all_flights():
    depth = service._tree.getNodeDepth(f)
    print(
        f"ID: {f.getValue()} | Depth: {depth} | Critical: {f.getIsCritical()} | FinalPrice: {f.getFinalPrice()}"
    )
