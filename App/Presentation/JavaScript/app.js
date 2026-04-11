const apiBase = "";

// Cache references to all important DOM elements used by the application.
const selectors = {
    loadJson: document.getElementById("load-json"),
    saveJson: document.getElementById("save-json"),
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
    traverseDfs: document.getElementById("traverse-dfs"),
    traverseBfs: document.getElementById("traverse-bfs"),
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
};

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
    selectors.rotaciones.textContent = JSON.stringify(metrics.rotations);
    selectors.cancelaciones.textContent = metrics.massive_cancelations;
}

/**
 * Display the traversal result returned by the API.
 */
function renderTraversal(result) {
    selectors.traversalResult.innerHTML = `
        <div class="traversal-box">
        <h4>Traversal ${result.order}</h4>
        <p>${result.nodes.join(" → ") || "No nodes available"}</p>
        </div>
    `;
}

/**
 * Render a simple tree representation using node IDs.
 */
function renderTree(nodes) {
    if (!nodes || nodes.length === 0) {
        selectors.treeContainer.innerHTML = "<p>No nodes in the tree.</p>";
        return;
    }

    selectors.treeContainer.innerHTML = `
        <div class="tree-nodes">
            ${nodes
                .map(
                    (value) => `
                <div class="tree-node">${value}</div>`
                )
                .join("")}
        </div>
    `;
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
        const treeData = await request("/tree/traverse?type=BFS");
        renderTree(treeData.nodes);
    } catch (error) {
        selectors.flightList.innerHTML = `<p class="error">${error.message}</p>`;
        selectors.treeContainer.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

/**
 * Load the default local JSON file on the server and refresh the view.
 */
async function loadJson() {
    try {
        const payload = await request("/tree/load", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: "App/Models/prueba_insercion.json" }),
        });
        alert(payload.message);
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Export the current tree to a JSON file with a custom filename.
 */
async function saveJson() {
    try {
        const filename = prompt("Filename to save", "tree_export.json");
        if (!filename) return;
        const payload = await request("/tree/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename }),
        });
        alert(payload.message);
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Save a versioned export of the current tree.
 */
async function versionJson() {
    try {
        const filename = `tree_version_${Date.now()}.json`;
        const payload = await request("/tree/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename }),
        });
        alert(payload.message);
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Open the hidden file input to upload a JSON file.
 */
function restoreJson() {
    selectors.jsonInput.click();
}

selectors.jsonInput.addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/tree/upload", {
            method: "POST",
            body: formData,
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Error uploading JSON");
        alert(data.message);
        refreshView();
    } catch (error) {
        alert(error.message);
    } finally {
        selectors.jsonInput.value = "";
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
        selectors.currentMode.textContent = `Mode ${mode}`;
        alert(payload.message);
        refreshView();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Request AVL verification from the backend and show the results.
 */
async function verifyAvl() {
    try {
        const payload = await request("/tree/verify");
        alert(`Balanced: ${payload.balanced}\nMode: ${payload.mode}\nInconsistent nodes: ${payload.inconsistent_nodes.join(", ")}`);
    } catch (error) {
        alert(error.message);
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
    selectors.loadJson.addEventListener("click", loadJson);
    selectors.saveJson.addEventListener("click", saveJson);
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
    selectors.traverseDfs.addEventListener("click", () => traverse("DFS"));
    selectors.traverseBfs.addEventListener("click", () => traverse("BFS"));
}

window.addEventListener("DOMContentLoaded", () => {
    attachEvents();
    refreshView();
});
