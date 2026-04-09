import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "Models"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "Services"))

from Models.Flight import Flight
from Services.Flight_Service import Flight_Service

# =============================================
# HELPER: print all flights with profitability
# =============================================
def print_flights(service):
    flights = service.get_all_flights()
    if not flights:
        print("  (tree is empty)")
        return
    for f in flights:
        depth = service._tree.getNodeDepth(f)
        profit = service._calculateProfitability(f)
        print(f"  ID: {f.getValue()} | Depth: {depth} | Passengers: {f.getPassengers()} | FinalPrice: {f.getFinalPrice()} | Promotion: {f.getPromotion()} | Critical: {f.getIsCritical()} | Profitability: {profit}")

# =============================================
# TEST 1: Basic case — lowest profitability
# =============================================
print("\n========== TEST 1: Basic deletion ==========")
service = Flight_Service()
service.setMaxDepth(10)  # high limit so no node is critical

f1 = Flight(10, "Bogota",   "Medellin", "08:00", 100.0, 120.0, 150, 0.1,  False)
f2 = Flight(5,  "Cali",     "Bogota",   "10:00", 80.0,  90.0,  100, 0.0,  False)
f3 = Flight(15, "Medellin", "Cali",     "12:00", 110.0, 130.0, 120, 0.05, False)
f4 = Flight(20, "Pereira",  "Bogota",   "14:00", 40.0,  50.0,  50,  0.0,  False)

service.create_flight(f1)
service.create_flight(f2)
service.create_flight(f3)
service.create_flight(f4)

print("Before deletion:")
print_flights(service)

deleted_id = service.deleteLowestProfitability()
print(f"\nDeleted flight ID: {deleted_id}  (expected: 20)")

print("\nAfter deletion:")
print_flights(service)

# =============================================
# TEST 2: Tiebreaker by depth
# =============================================
print("\n========== TEST 2: Tiebreaker by depth ==========")
service2 = Flight_Service()
service2.setMaxDepth(10)

# ID 5 and ID 3 have same profitability: 100 * 90 = 9000
# ID 3 will be deeper in the tree, so it should be deleted first
g1 = Flight(10, "Bogota",   "Medellin", "08:00", 100.0, 120.0, 150, 0.0, False)
g2 = Flight(5,  "Cali",     "Bogota",   "10:00", 80.0,  90.0,  100, 0.0, False)
g3 = Flight(3,  "Medellin", "Cali",     "12:00", 80.0,  90.0,  100, 0.0, False)

service2.create_flight(g1)
service2.create_flight(g2)
service2.create_flight(g3)

print("Before deletion:")
print_flights(service2)

# Check depths manually
for f in service2.get_all_flights():
    print(f"  ID: {f.getValue()} depth: {service2._tree.getNodeDepth(f)}")

deleted_id2 = service2.deleteLowestProfitability()
print(f"\nDeleted flight ID: {deleted_id2}  (expected: 3, deepest among ties)")

print("\nAfter deletion:")
print_flights(service2)

# =============================================
# TEST 3: Tiebreaker by largest ID
# =============================================
print("\n========== TEST 3: Tiebreaker by largest ID ==========")
service3 = Flight_Service()
service3.setMaxDepth(10)

# Both ID 5 and ID 15 are at depth 1 with same profitability
# So the one with the largest ID (15) should be deleted
h1 = Flight(10, "Bogota",   "Medellin", "08:00", 100.0, 120.0, 150, 0.0, False)
h2 = Flight(5,  "Cali",     "Bogota",   "10:00", 80.0,  90.0,  100, 0.0, False)  # depth 1, profit 9000
h3 = Flight(15, "Medellin", "Cali",     "12:00", 80.0,  90.0,  100, 0.0, False)  # depth 1, profit 9000

service3.create_flight(h1)
service3.create_flight(h2)
service3.create_flight(h3)

print("Before deletion:")
print_flights(service3)

# Verify both are at same depth
for f in service3.get_all_flights():
    print(f"  ID: {f.getValue()} depth: {service3._tree.getNodeDepth(f)}")

deleted_id3 = service3.deleteLowestProfitability()
print(f"\nDeleted flight ID: {deleted_id3}  (expected: 15, largest ID among ties at same depth)")

print("\nAfter deletion:")
print_flights(service3)

# =============================================
# TEST 4: Subtree deletion
# =============================================
print("\n========== TEST 4: Subtree deletion ==========")
service4 = Flight_Service()
service4.setMaxDepth(10)

# Insert flights so that the least profitable node HAS children
# Tree will look like:
#        10
#       /  \
#      3    15
#       \
#        5   <- children of node 3
i1 = Flight(10, "Bogota",   "Medellin", "08:00", 100.0, 120.0, 150, 0.0, False)
i2 = Flight(3,  "Cali",     "Bogota",   "10:00", 20.0,  25.0,  10,  0.0, False)  # very low profitability
i3 = Flight(15, "Medellin", "Cali",     "12:00", 110.0, 130.0, 120, 0.0, False)
i4 = Flight(5,  "Pereira",  "Bogota",   "14:00", 20.0,  25.0,  80,  0.0, False)  # child of node 3

service4.create_flight(i1)
service4.create_flight(i2)
service4.create_flight(i3)
service4.create_flight(i4)

print("Before deletion:")
print_flights(service4)
print(f"  Total flights: {len(service4.get_all_flights())}")

deleted_id4 = service4.deleteLowestProfitability()
print(f"\nDeleted flight ID: {deleted_id4}")

print("\nAfter deletion (node AND its subtree should be gone):")
print_flights(service4)
print(f"  Total flights: {len(service4.get_all_flights())}")