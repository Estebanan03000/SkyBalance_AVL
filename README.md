# SkyBalance_AVL

# Description
System that manages data structures such as AVL, BST, stacks, and queues,
allowing operations on flights loaded from JSON files.

## Execution
... How to run it...

## Project Structure

App/
│
├── Models/
│   ├── AVL.py          # AVL tree implementation
│   ├── BST.py          # Binary search tree
│   ├── Flight.py       # Flight data model
│   ├── JSON.py         # JSON file handling
│   ├── Queue.py        # Queue implementation
│   ├── Stack.py        # Stack implementation
│
├── Services/
│   ├── Flight_Service.py   # Logic for managing flights
│   ├── Metrics_Service.py  # Metrics calculation
│
├── routes.py          # Route definitions (interaction)
├── app.py             # System entry point


## System Flow

1. The system starts from app.py
2. Data is loaded from JSON files
3. Flights are stored in structures such as AVL or BST
4. Services process the information (metrics, queries)
5. The user interacts through defined routes

## Main Components

- AVL: Used to keep data balanced and ensure efficient searches
- BST: Base implementation for performance comparison
- Queue: Handles processes in FIFO order
- Stack: Supports auxiliary operations or traversals

## Input Data

The system loads information from JSON files containing flight data.

Example structure:
{
    "codigo": 10,
    "origen": "Bogotá",
    "destino": "Medellín",
    "horaSalida": "08:00",
    "precioBase": 100.0,
    "precioFinal": 120.0,
    "pasajeros": 150,
    "promocion": 0.1,
    "alerta": false
}

## Functionalities

- Load flights from JSON files
- Insert data into AVL and BST structures
- Query flight information
- Calculate system metrics
