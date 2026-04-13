#!/usr/bin/env python3
"""
Test script to verify tree structure preservation during mode switch
"""
import urllib.request
import json
import time

BASE_URL = 'http://127.0.0.1:5000'

def make_request(method, endpoint, data=None):
    """Make HTTP request and return JSON response"""
    url = BASE_URL + endpoint
    headers = {'Content-Type': 'application/json'}
    
    if data:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

print("TEST: Tree structure preservation during mode switch")
print("=" * 55)

# Insert flights
print("\n[1] Inserting 3 flights in AVL mode...")
flights = [
    {"id": 100, "origin": "BOG", "destiny": "MDE", "date": "2026-01-01 10:00:00", "basePrice": 150, "passengers": 100, "sold": False},
    {"id": 50, "origin": "BOG", "destiny": "CTG", "date": "2026-01-01 11:00:00", "basePrice": 120, "passengers": 80, "sold": False},
    {"id": 200, "origin": "BOG", "destiny": "CAL", "date": "2026-01-01 12:00:00", "basePrice": 200, "passengers": 120, "sold": False},
]
for flight in flights:
    status, resp = make_request('POST', '/flights', flight)
    if status != 201:
        print(f"  ❌ Failed to insert flight {flight['id']}: {resp}")
    else:
        print(f"  ✓ Flight {flight['id']} inserted")

time.sleep(0.5)

# Check AVL balance
print("\n[2] AVL Mode (initial structure):")
status, data1 = make_request('GET', '/tree/verify-all-balances')
d1 = data1['report']['tree_depth']
unb1 = data1['report']['unbalanced_nodes']
tot1 = data1['report']['total_nodes']
print(f"    Depth: {d1}")
print(f"    Unbalanced nodes: {unb1}/{tot1}")

# Switch to Stress mode
print("\n[3] Switching to Stress (BST mode)...")
status, resp = make_request('PUT', '/config/mode', {"mode": "Stress"})
if status == 200:
    print(f"    ✓ Mode switched")
else:
    print(f"    ❌ Failed: {resp}")

time.sleep(0.5)

# Check BST after switch (no insertions yet)
print("\n[4] BST Mode (AFTER SWITCH, no insertions):")
status, data2 = make_request('GET', '/tree/verify-all-balances')
d2 = data2['report']['tree_depth']
unb2 = data2['report']['unbalanced_nodes']
tot2 = data2['report']['total_nodes']
print(f"    Depth: {d2}")
print(f"    Unbalanced nodes: {unb2}/{tot2}")

print("\n" + "=" * 55)
if d1 == d2:
    print(f"✅ SUCCESS! Tree structure preserved (depth: {d1} → {d2})")
else:
    print(f"❌ FAILED! Tree was degraded (depth: {d1} → {d2})")

# Now test insertion in Stress mode
print("\n[5] Inserting flight 150 in Stress mode...")
status, resp = make_request('POST', '/flights', {"id": 150, "origin": "BOG", "destiny": "ARM", "date": "2026-01-01 14:00:00", "basePrice": 180, "passengers": 90, "sold": False})
if status == 201:
    print(f"    ✓ Flight 150 inserted")
else:
    print(f"    ❌ Failed: {resp}")

time.sleep(0.5)

# Check BST after insertion
print("\n[6] BST Mode (AFTER insertion in Stress):")
status, data3 = make_request('GET', '/tree/verify-all-balances')
d3 = data3['report']['tree_depth']
unb3 = data3['report']['unbalanced_nodes']
tot3 = data3['report']['total_nodes']
print(f"    Depth: {d3}")
print(f"    Unbalanced nodes: {unb3}/{tot3}")

if d3 >= d2:
    print(f"\n✅ Tree degradation when inserting in Stress mode (depth: {d2} → {d3})")
else:
    print(f"\n⚠️  Depth didn't increase (depth: {d2} → {d3})")

print("\n" + "=" * 55)

