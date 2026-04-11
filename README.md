# SkyBalance_AVL

## Description
Flight management system built on AVL and BST tree structures. Flights are
loaded from JSON files, stored in a self-balancing AVL tree, and exposed
through a Flask REST API. Includes depth-based pricing penalties, intelligent
deletion by economic impact, undo history, and real-time tree metrics.

## Requirements
- Python 3.10+
- Flask: `pip install flask`

## Execution
```bash
python app.py
```
Server starts at `http://localhost:5000`.

## Project Structure
App/
├── Models/
│   ├── AVL.py              # AVL tree with automatic balancing
│   ├── BST.py              # Binary search tree, base class for AVL
│   ├── Flight.py           # Flight node with tree pointers
│   ├── JSON.py             # JSON loader (insertion and topology formats)
│   ├── Queue.py            # FIFO queue
│   └── Stack.py            # LIFO stack for undo history
├── Services/
│   ├── Flight_Service.py   # CRUD, undo, depth penalty, export
│   └── Metrics_Service.py  # Height, leaves, rotations, cancellations
├── routes.py               # Flask API endpoints
└── app.py                  # Entry point

## JSON Input Formats

**Insertion** — list of flights, inserted one by one into AVL and BST:
```json
{ "flights": [{ "codigo": 10, "origen": "Bogotá", "destino": "Medellín",
  "horaSalida": "08:00", "precioBase": 100.0, "precioFinal": 120.0,
  "pasajeros": 150, "promocion": 0.1, "alerta": false }] }
```

**Topology** — pre-built tree structure, reconstructed as-is:
```json
{ "codigo": 10, ..., "izquierdo": { ... }, "derecho": { ... } }
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/flights` | List all flights |
| POST | `/flights` | Insert a flight |
| PUT | `/flights/<id>` | Update a flight |
| DELETE | `/flights/<id>` | Delete a flight |
| DELETE | `/flights/lowest-profitability` | Delete least profitable subtree |
| GET | `/metrics` | Real-time tree metrics |
| PUT | `/config/max-depth` | Set depth penalty threshold |
| POST | `/tree/export` | Export full tree to JSON |