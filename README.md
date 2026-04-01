# SkyBalance_AVL

# Descripción
Sistema que gestiona estructuras de datos como AVL, BST, pilas y colas,
permitiendo operaciones sobre vuelos cargados desde archivos JSON.
## Ejecución
... Cómo hacerla...

## Estructura del proyecto

App/
│
├── Models/
│   ├── AVL.py          # Implementación de árbol AVL
│   ├── BST.py          # Árbol binario de búsqueda
│   ├── Flight.py       # Modelo de datos de vuelo
│   ├── JSON.py         # Manejo de archivos JSON
│   ├── Queue.py        # Implementación de cola
│   ├── Stack.py        # Implementación de pila
│
├── Services/
│   ├── Flight_Service.py   # Lógica para manejar vuelos
│   ├── Metrics_Service.py  # Cálculo de métricas
│
├── routes.py          # Definición de rutas (interacción)
├── app.py             # Punto de entrada del sistema


## Flujo del sistema

1. El sistema inicia desde app.py
2. Se cargan datos desde archivos JSON
3. Los vuelos se almacenan en estructuras como AVL o BST
4. Los servicios procesan la información (métricas, consultas)
5. El usuario interactúa mediante rutas definidas

## Componentes principales

- AVL: Se utiliza para mantener los datos balanceados y garantizar búsquedas eficientes
- BST: Implementación base para comparación de rendimiento
- Queue: Manejo de procesos en orden FIFO
- Stack: Soporte para operaciones auxiliares o recorridos

## Entrada de datos

El sistema carga información desde archivos JSON que contienen datos de vuelos.

Ejemplo de estructura:
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

## Funcionalidades

- Cargar vuelos desde archivos JSON
- Insertar datos en estructuras AVL y BST
- Consultar información de vuelos
- Calcular métricas del sistema
