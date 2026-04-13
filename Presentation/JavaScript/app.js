const apiBase = "";

// Track the current mode for JSON operations
let currentJsonMode = null;

// Cache references to all important DOM elements used by the application.
const selectors = {
    loadJsonInsertion: document.getElementById("load-json-insertion"),
    loadJsonTopology: document.getElementById("load-json-topology"),
    saveJsonInsertion: document.getElementById("save-json-insertion"),
    saveJsonTopology: document.getElementById("save-json-topology"),
    versionJson: document.getElementById("version-json"),
    restoreJson: document.getElementById("restore-json"),
    modeStress: document.getElementById("mode-stress"),
    modeGlobal: document.getElementById("mode-global"),
    verifyAvl: document.getElementById("verify-avl"),
    insertNode: document.getElementById("insert-node"),
    deleteNode: document.getElementById("delete-node"),
    cancelSubtree: document.getElementById("cancel-subtree"),
    undoAction: document.getElementById("undo-action"),
    processQueue: document.getElementById("process-queue"),
    deleteLowest: document.getElementById("delete-lowest"),
    traverseDepth: document.getElementById("traverse-depth"),
    traversePreorder: document.getElementById("traverse-preorder"),
    traverseInorder: document.getElementById("traverse-inorder"),
    traversePostorder: document.getElementById("traverse-postorder"),
    jsonInput: document.getElementById("json-file-input"),
    altura: document.getElementById("altura"),
    hojas: document.getElementById("hojas"),
    rotaciones: document.getElementById("rotaciones"),
    cancelaciones: document.getElementById("cancelaciones"),
    treeContainer: document.getElementById("tree-container"),
    flightList: document.getElementById("flight-list"),
    traversalResult: document.getElementById("traversal-result"),
    currentMode: document.getElementById("current-mode"),
    queueStatus: document.getElementById("queue-status"),
    maxDepthInput: document.getElementById("max-depth-input"),
    setMaxDepth: document.getElementById("set-max-depth"),
};

async function setMaxDepth() {
    const depth = Number(selectors.maxDepthInput.value);
    if (isNaN(depth) || depth < 0) return alert("Enter a valid depth");
    try {
        const payload = await request("/config/max-depth", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ maxDepth: depth }),
        });
        alert(payload.message);
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Perform an HTTP request to the backend API and return parsed JSON.
 * Throws an Error when the response is not OK.
 */
async function request(url, options = {}) {
    const res = await fetch(`${apiBase}${url}`, options);
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
}

/**
 * Render the list of flights in the right panel.
 */
function renderFlights(flights) {
    if (!flights || flights.length === 0) {
        selectors.flightList.innerHTML = "<p>No flights loaded.</p>";
        return;
    }

    selectors.flightList.innerHTML = `
        <table class="flight-table">
        <thead>
            <tr>
            <th>ID</th>
            <th>Origin</th>
            <th>Destination</th>
            <th>Base Price</th>
            <th>Final Price</th>
            <th>Passengers</th>
            </tr>
        </thead>
        <tbody>
            ${flights
            .map(
                (f) => `
            <tr>
                <td>${f.id}</td>
                <td>${f.origin}</td>
                <td>${f.destiny}</td>
                <td>${f.basePrice}</td>
                <td>${f.finalPrice}</td>
                <td>${f.passengers}</td>
            </tr>`
            )
            .join("")}
        </tbody>
        </table>
    `;
}

/**
 * Update the metric values displayed in the metrics panel.
 */
function renderMetrics(metrics) {
    selectors.altura.textContent = metrics.height;
    selectors.hojas.textContent = metrics.leaves;
    if (metrics.mode === "Stress") {
        selectors.rotaciones.textContent = "No aplica en modo Stress (BST)";
    } else {
        selectors.rotaciones.textContent = JSON.stringify(metrics.rotations || {});
    }
    selectors.cancelaciones.textContent = metrics.massive_cancelations;
}

/**
 * Display the traversal result returned by the API.
 */
function renderTraversal(result) {
    const nodes = Array.isArray(result.nodes) ? result.nodes : [];
    selectors.traversalResult.innerHTML = `
        <div class="traversal-box">
            <h4>${result.order || "Recorrido"}</h4>
            <p>${nodes.join(" → ") || "No data"}</p>
        </div>
    `;
}

/**
 * Render a simple tree representation using node IDs.
 */
async function loadTreeImage() {
    try {
        const response = await fetch("/tree/render");
        const data = await response.json();

        if (!data.image) {
            selectors.treeContainer.innerHTML = "<p>No tree available</p>";
            return;
        }

        selectors.treeContainer.innerHTML = `
            <img 
                src="data:image/png;base64,${data.image}" 
                class="tree-image"
            />
        `;
    } catch (error) {
        console.error("Error rendering tree:", error);
        selectors.treeContainer.innerHTML = "<p>Error loading tree</p>";
    }
}

/**
 * Fetch the latest tree state, metrics, and flight list from the backend.
 */
async function refreshView() {
    try {
        const flights = await request("/flights");
        renderFlights(flights);
        const metrics = await request("/metrics");
        renderMetrics(metrics);
        await loadTreeImage();
    } catch (error) {
        selectors.flightList.innerHTML = `<p class="error">${error.message}</p>`;
        selectors.treeContainer.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

/**
 * Load JSON file in Insertion mode.
 * Opens file picker to select a JSON file with "vuelos" array.
 */
function loadJsonInsertion() {
    currentJsonMode = "insertion";
    selectors.jsonInput.click();
}

/**
 * Load JSON file in Topology mode.
 * Opens file picker to select a JSON file with tree structure.
 */
function loadJsonTopology() {
    currentJsonMode = "topology";
    selectors.jsonInput.click();
}

/**
 * Export the current tree to a JSON file in Insertion mode format.
 */
async function saveJsonInsertion() {
    try {
        const filename = prompt("Filename to save (Insertion mode)", "flights_insertion.json");
        if (!filename) return;
        const payload = await request("/tree/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename, mode: "insertion" }),
        });
        alert(payload.message);
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Export the current tree to a JSON file in Topology mode format.
 */
async function saveJsonTopology() {
    try {
        const filename = prompt("Filename to save (Topology mode)", "flights_topology.json");
        if (!filename) return;
        const payload = await request("/tree/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename, mode: "topology" }),
        });
        alert(payload.message);
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Load the default local JSON file on the server and refresh the view.
 */
async function loadJson() {
    selectors.jsonInput.value = "";
    selectors.jsonInput.click();
}

/**
 * Export the current tree to a JSON file with a custom filename.
 */
async function saveJson() {
    try {
        const filename = prompt("Filename to save", "tree_export.json");
        if (!filename) return;

        const response = await fetch("/tree/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename }),
        });

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a); // opcional pero más seguro
        a.click();
        a.remove();

        window.URL.revokeObjectURL(url);
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Save a versioned export of the current tree.
 */
async function versionJson() {
    const name = prompt("Version name", "Simulacion Alta Demanda");
    if (!name) return;
    try {
        const payload = await request("/versions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name }),
        });
        alert(payload.message);
    } catch (error) {
        alert(error.message);
    }
}
/**
 * Open the hidden file input to upload a JSON file.
 */
async function restoreJson() {
    try {
        // First get the list of saved versions
        const versions = await request("/versions");
        if (versions.length === 0) return alert("No saved versions found");

        const name = prompt(
            "Available versions:\n" + versions.join("\n") + "\n\nEnter version name to restore:",
            versions[0]
        );
        if (!name) return;

        const payload = await request(`/versions/${encodeURIComponent(name)}/restore`, {
            method: "PUT",
        });
        alert(payload.message);
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

// Triggered when the user selects a file from the file picker
selectors.jsonInput.addEventListener("change", async (event) => {
    // Get the selected file from the input
    const file = event.target.files[0];
    if (!file) return;

    try {
        // Read the file content as plain text
        const text = await file.text();

        // Parse the text into a JavaScript object
        const jsonData = JSON.parse(text);

        // INSERTION MODE
        if (currentJsonMode === "insertion") {
            const response = await fetch("/flights/load", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(jsonData),
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Error loading JSON");

            // Show AVL vs BST comparison for insertion mode
            alert(
                `✅ Árbol cargado en MODO INSERCIÓN\n\n` +
                `📊 AVL → Raíz: ${data.avl.root} | Profundidad: ${data.avl.depth} | Hojas: ${data.avl.leaves}\n` +
                `🌳 BST → Raíz: ${data.bst.root} | Profundidad: ${data.bst.depth} | Hojas: ${data.bst.leaves}`
            );
        } 
        // TOPOLOGY MODE
        else if (currentJsonMode === "topology") {
            const response = await fetch("/flights/load", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(jsonData),
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Error loading JSON");

            // Show topology mode confirmation
            alert(
                `✅ Árbol cargado en MODO TOPOLOGÍA\n\n` +
                `📊 Raíz: ${data.avl.root} | Profundidad: ${data.avl.depth} | Hojas: ${data.avl.leaves}`
            );
        }

        // Refresh the tree visualization and metrics on screen
        refreshView();

    } catch (error) {
        alert("❌ Error: " + error.message);
    } finally {
        // Reset the file input so the same file can be loaded again if needed
        selectors.jsonInput.value = "";
        currentJsonMode = null;
    }
});

/**
 * Switch the tree evaluation mode between BST stress mode and AVL global balance mode.
 */
async function switchMode(mode) {
    try {
        const payload = await request("/config/mode", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode }),
        });
        
        selectors.currentMode.textContent = `Mode: ${mode}`;
        
        // If performing rebalance, show detailed information
        if (payload.rebalance_report) {
            const report = payload.rebalance_report;
            const message = `✅ ${payload.message}\n\n📊 Cambios:
            • Profundidad anterior: ${report.initial_depth} → ${report.final_depth}
            • Altura anterior: ${report.initial_height} → ${report.final_height}
            • Vuelos rebalanceados: ${report.flights_rebalanced}
            • Tipo de árbol: ${report.tree_type}`;
            alert(message);
        } else {
            alert(payload.message + `\n\nTipo de árbol: ${payload.tree_type || 'Desconocido'}`);
        }
        
        refreshView();
    } catch (error) {
        alert("❌ Error: " + error.message);
    }
}

/**
 * Request AVL verification from the backend and show the results.
 */
async function verifyAvl() {
    try {
        const payload = await request("/tree/verify");
        const inconsistentList = payload.inconsistent_nodes.length > 0 
            ? payload.inconsistent_nodes.map(n => `Vuelo ${n.id} (BF: ${n.balance_factor})`).join(", ")
            : "Ninguno";
        const message = `🔍 Estado del árbol:\n
Modo: ${payload.mode}
Balanceado: ${payload.balanced ? "✅ Sí" : "❌ No"}
Nodos inconsistentes: ${inconsistentList}`;
        alert(message);
    } catch (error) {
        alert("❌ Error: " + error.message);
    }
}

/**
 * Verify balance factor of all nodes in the tree.
 */
async function verifyAllBalances() {
    try {
        const payload = await request("/tree/verify-all-balances");
        const report = payload.report;
        
        let detailedMessage = `📊 Reporte completo de balance:\n
Modo: ${report.mode}
Total de nodos: ${report.total_nodes}
Nodos balanceados: ${report.balanced_nodes}
Nodos desbalanceados: ${report.unbalanced_nodes}
Profundidad: ${report.tree_depth}\n`;

        if (report.unbalanced_nodes > 0) {
            detailedMessage += "⚠️ Nodos desbalanceados:\n";
            report.unbalanced_details.forEach(node => {
                detailedMessage += `  • Vuelo ${node.id}: BF=${node.balance_factor}, Profundidad=${node.depth}\n`;
            });
        }
        
        alert(detailedMessage);
    } catch (error) {
        alert("❌ Error: " + error.message);
    }
}

/**
 * Ask the user for flight details and create a new node in the tree.
 */
async function insertNode() {
    try {
        const id = Number(prompt("Flight ID", "1"));
        const origin = prompt("Origin", "Bogotá");
        const destiny = prompt("Destination", "Medellín");
        const date = prompt("Date and time (YYYY-MM-DD HH:MM:SS)", "2026-01-01 12:00:00");
        const basePrice = Number(prompt("Base price", "100"));
        const finalPrice = Number(prompt("Final price", "120"));
        const passengers = Number(prompt("Passengers", "100"));

        if (!id || !origin || !destiny) {
            return alert("Required fields are missing");
        }

        await request("/flights", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id, origin, destiny, date, basePrice, finalPrice, passengers }),
        });
        alert("Flight inserted successfully");
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Prompt for a flight ID and delete the corresponding node.
 */
async function deleteNode() {
    try {
        const id = Number(prompt("Flight ID to delete", ""));
        if (!id) return;
        await request(`/flights/${id}`, { method: "DELETE" });
        alert("Flight deleted");
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Cancel a subtree rooted at the specified flight node.
 */
async function cancelSubtree() {
    try {
        const id = Number(prompt("Root flight ID for subtree cancellation", ""));
        if (!id) return;
        const payload = await request("/tree/cancel-subtree", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id }),
        });
        alert(`${payload.message}: ${payload.deleted_count} flights deleted`);
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Undo the previous tree operation.
 */
async function undoAction() {
    try {
        const payload = await request("/tree/undo", { method: "POST" });
        alert(payload.message);
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Send a list of flight objects to the queue processing endpoint.
 */
async function processQueue() {
    try {
        const raw = prompt("Enter a JSON array of flights to process", "[]");
        if (!raw) return;
        const flights = JSON.parse(raw);
        const payload = await request("/queue/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ flights }),
        });
        alert(payload.message);
        selectors.queueStatus.innerHTML = `<p>${payload.reports.length} flights processed in queue.</p>`;
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Delete the flight with the lowest profitability from the tree.
 */
async function deleteLowestProfitability() {
    try {
        const payload = await request("/flights/lowest-profitability", { method: "DELETE" });
        alert(`Flight ${payload.flight_id} deleted due to lowest profitability`);
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Request a traversal from the backend and display the result.
 */
async function traverse(type) {
    try {
        const payload = await request(`/tree/traverse?type=${type}`);
        renderTraversal(payload);
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Attach click listeners to all interactive buttons.
 */
function attachEvents() {
    // New specific mode buttons
    selectors.loadJsonInsertion.addEventListener("click", loadJsonInsertion);
    selectors.loadJsonTopology.addEventListener("click", loadJsonTopology);
    selectors.saveJsonInsertion.addEventListener("click", saveJsonInsertion);
    selectors.saveJsonTopology.addEventListener("click", saveJsonTopology);
    
    selectors.versionJson.addEventListener("click", versionJson);
    selectors.restoreJson.addEventListener("click", restoreJson);
    selectors.modeStress.addEventListener("click", () => switchMode("Stress"));
    selectors.modeGlobal.addEventListener("click", () => switchMode("Global Balance"));
    selectors.verifyAvl.addEventListener("click", verifyAvl);
    selectors.insertNode.addEventListener("click", insertNode);
    selectors.deleteNode.addEventListener("click", deleteNode);
    selectors.cancelSubtree.addEventListener("click", cancelSubtree);
    selectors.undoAction.addEventListener("click", undoAction);
    selectors.processQueue.addEventListener("click", processQueue);
    selectors.deleteLowest.addEventListener("click", deleteLowestProfitability);
    selectors.traverseDepth.addEventListener("click", () => traverse("BFS"));
    selectors.traversePreorder.addEventListener("click", () => traverse("PREORDER"));
    selectors.traverseInorder.addEventListener("click", () => traverse("INORDER"));
    selectors.traversePostorder.addEventListener("click", () => traverse("POSTORDER"));
    selectors.setMaxDepth.addEventListener("click", setMaxDepth);
}

window.addEventListener("DOMContentLoaded", () => {
    attachEvents();
    refreshView();
});

function normalizeFlightId(rawId) {
    const value = String(rawId || "").trim();
    if (!value) return null;

    if (/^\d+$/.test(value)) {
        return Number(value);
    }

    const match = value.match(/(\d+)$/);
    if (match) {
        return Number(match[1]);
    }

    return null;
}
/**
 * Ask the user for flight details and create a new node in the tree.
 */
async function insertNode() {
    try {
        const id = prompt("ID del Vuelo (ej: 800 o SB800)", "SB800");
        const origin = prompt("Origen", "Bogotá");
        const destiny = prompt("Destino", "Medellín");
        const date = prompt("Fecha y hora (YYYY-MM-DD HH:MM:SS)", "2026-01-01 12:00:00");
        const basePrice = prompt("Precio Base", "100");
        const finalPrice = prompt("Precio Final", "120");
        const passengers = prompt("Pasajeros", "100");

        // Validate required fields
        if (!id || !origin || !destiny || !date) {
            return alert("❌ Campos requeridos: ID, Origen, Destino y Fecha");
        }

        // Validate number fields
        const numId = normalizeFlightId(id);
        const numBase = Number(basePrice) || 0;
        const numFinal = Number(finalPrice) || numBase;
        const numPass = Number(passengers) || 0;

        if (numId === null || isNaN(numId) || numId <= 0) {
            return alert("❌ El ID debe ser numérico o tipo SB### (ej: SB800)");
        }

        const payload = await request("/flights", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id: numId,
                origin: origin.trim(),
                destiny: destiny.trim(),
                date: date.trim(),
                basePrice: numBase,
                finalPrice: numFinal,
                passengers: numPass,
                discount: 0,
                sold: false
            }),
        });
        alert(`✅ Vuelo ${numId} insertado correctamente\n${payload.message || ""}`);
        refreshView();
    } catch (error) {
        alert(`❌ Error al insertar: ${error.message}`);
    }
}
/**
 * Request AVL verification from the backend and show the results.
 */
async function verifyAvl() {
    try {
        const payload = await request("/tree/verify");
        const balanced = payload.balanced ? "✅ SÍ (AVL válido)" : "❌ NO (no es un AVL válido)";
        const mode = payload.mode || "Desconocido";
        const inconsistent = payload.inconsistent_nodes;
        
        let message = `🔍 VERIFICACIÓN AVL\n\n`;
        message += `Árbol Balanceado: ${balanced}\n`;
        message += `Modo: ${mode}\n`;
        
        if (inconsistent && inconsistent.length > 0) {
            message += `\n⚠️ Nodos con desbalance:\n`;
            inconsistent.forEach(node => {
                message += `  • ID ${node.id}: Factor = ${node.balance_factor}\n`;
            });
        } else {
            message += `\n✅ Todos los nodos están balanceados`;
        }
        
        alert(message);
    } catch (error) {
        alert(`❌ Error en verificación: ${error.message}`);
    }
}
/**
 * Switch the tree evaluation mode between BST stress mode and AVL global balance mode.
 */
async function switchMode(mode) {
    try {
        const payload = await request("/config/mode", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode }),
        });
        
        const modeDisplay = mode === "Stress" ? "🚨 ESTRÉS (BST)" : "⚖️ BALANCE GLOBAL (AVL)";
        selectors.currentMode.textContent = modeDisplay;
        alert(`${payload.message || "Modo cambiado"}\n\n${modeDisplay}`);
        refreshView();
    } catch (error) {
        alert(`❌ Error al cambiar modo: ${error.message}`);
    }
}
/**
 * Request a traversal from the backend and display the result.
 */
async function traverse(type) {
    try {
        const payload = await request(`/tree/traverse?type=${type}`);
        
        // Map type names for display
        const typeNames = {
            "DFS": "🌳 DFS (Pre-Order)",
            "BFS": "📊 BFS (Breadth-First)",
            "INORDER": "📈 In-Order",
            "POSTORDER": "📉 Post-Order"
        };
        
        const displayType = typeNames[type] || payload.order || type;
        
        if (!payload.nodes || payload.nodes.length === 0) {
            alert(`${displayType}\n\nÁrbol vacío - No hay nodos para recorrer`);
            return;
        }
        
        // Display in traversal result panel
        const nodesText = payload.nodes.join(" → ");
        const countText = `${payload.count} nodo${payload.count !== 1 ? 's' : ''}`;
        
        selectors.traversalResult.innerHTML = `
            <div class="traversal-box">
                <h4>${displayType}</h4>
                <p><strong>Conteo:</strong> ${countText}</p>
                <p><strong>Secuencia:</strong> ${nodesText}</p>
            </div>
        `;
        
        alert(`${displayType}\n\nTotal: ${countText}\nSecuencia: ${nodesText}`);
    } catch (error) {
        alert(`❌ Error en traversal: ${error.message}`);
    }
}
/**
 * Undo the previous tree operation.
 */
async function undoAction() {
    try {
        const payload = await request("/tree/undo", { method: "POST" });
        alert(`↩️ DESHACER\n\n${payload.message || "Operación deshecha"}`);
        refreshView();
    } catch (error) {
        alert(`❌ Error en undo: ${error.message}`);
    }
}
/**
 * Cancel a subtree rooted at the specified flight node.
 */
async function cancelSubtree() {
    try {
        const rawId = prompt("ID del vuelo raíz para cancelar subárbol (ej: 800 o SB800)", "");
        const id = normalizeFlightId(rawId);
        if (id === null || Number.isNaN(id)) {
            return alert("❌ Debes ingresar un ID válido (numérico o SB###)");
        }
        
        const confirmed = confirm(`⚠️ ¿Seguro de cancelar el subárbol con raíz ID ${id}?\n\nEsto eliminará este vuelo y todos sus descendientes.`);
        if (!confirmed) return;
        
        const payload = await request("/tree/cancel-subtree", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id }),
        });
        
        const deletedText = payload.deleted_ids ? payload.deleted_ids.join(", ") : "N/A";
        alert(`✅ ${payload.message}\n\n📊 Cantidad eliminada: ${payload.deleted_count}\n🆔 IDs: ${deletedText}`);
        refreshView();
    } catch (error) {
        alert(`❌ Error al cancelar subárbol: ${error.message}`);
    }
}
/**
 * Send a list of flight objects to the queue processing endpoint.
 */
async function processQueue() {
    try {
        const raw = prompt(
            "Ingresa un JSON array de vuelos para procesar\n\n" +
            "Ejemplo:\n" +
            '[{"id": 1, "origin": "BOG", "destiny": "MDE", "basePrice": 100, "passengers": 50}]',
            '[]'
        );
        if (!raw || raw === '[]') {
            return alert("⚠️ Cola vacía");
        }
        
        let flights;
        try {
            flights = JSON.parse(raw);
        } catch (e) {
            return alert(`❌ JSON inválido: ${e.message}`);
        }
        
        if (!Array.isArray(flights)) {
            return alert("❌ Debes enviar un array JSON válido");
        }
        
        const payload = await request("/queue/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ flights }),
        });
        
        const processed = payload.processed || 0;
        const message = `${payload.message || "Cola procesada"}\n\n📊 Vuelos procesados: ${processed}`;
        alert(message);
        
        selectors.queueStatus.innerHTML = `
            <p>✅ ${processed} vuelo${processed !== 1 ? 's' : ''} procesado${processed !== 1 ? 's' : '}'}</p>
        `;
        refreshView();
    } catch (error) {
        alert(`❌ Error al procesar cola: ${error.message}`);
    }
}
/**
 * Prompt for a flight ID and delete the corresponding node.
 */
async function deleteNode() {
    try {
        const id = prompt("ID del vuelo a eliminar", "");
        if (!id || isNaN(Number(id))) {
            return alert("❌ Debes ingresar un ID válido");
        }
        
        const confirmed = confirm(`⚠️ ¿Seguro de eliminar el vuelo ${id}?`);
        if (!confirmed) return;
        
        const payload = await request(`/flights/${Number(id)}`, { method: "DELETE" });
        alert(`✅ Vuelo ${id} eliminado correctamente\n${payload.message || ""}`);
        refreshView();
    } catch (error) {
        alert(`❌ Error al eliminar: ${error.message}`);
    }
}
