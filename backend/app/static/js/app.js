let network = null;

async function startExtraction() {
    const platform = document.getElementById('platform').value;
    const username = document.getElementById('username').value;
    const statusText = document.getElementById('status');

    if (!username) return alert("Please enter a username!");

    statusText.innerText = "Submitting Job to Queue...";

    try {
        // 1. Submit the job
        const response = await fetch(`/api/v1/extract/${platform}/${username}`, { method: 'POST' });
        const data = await response.json();

        if (data.job_id) {
            pollJobStatus(data.job_id);
        } else {
            statusText.innerText = "Error submitting job.";
        }
    } catch (error) {
        statusText.innerText = "Network Error.";
    }
}

async function pollJobStatus(jobId) {
    const statusText = document.getElementById('status');
    statusText.innerText = `Scraping in background (Job ID: ${jobId})...`;

    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/v1/jobs/status/${jobId}`);

            // If the server returns a 404 or 500, stop the loop!
            if (!response.ok) {
                clearInterval(interval);
                statusText.innerText = `Error: Server returned ${response.status}. Check terminal.`;
                return;
            }

            const data = await response.json();

            if (data.status === "SUCCESS") {
                clearInterval(interval);
                statusText.innerText = `Success! Saved ${data.result.nodes_saved} nodes. Loading graph...`;
                loadGraph();
            } else if (data.status === "FAILURE") {
                clearInterval(interval);
                statusText.innerText = "Extraction Failed. Check server logs.";
            }
        } catch (error) {
            clearInterval(interval);
            statusText.innerText = "Network disconnected.";
        }
    }, 2000);
}

async function loadGraph() {
    const username = document.getElementById('username').value;
    const statusText = document.getElementById('status');

    if (!username) return alert("Please enter a username to view!");

    statusText.innerText = "Fetching graph from Neo4j...";

    try {
        const response = await fetch(`/api/v1/graph/network/${username}`);

        if (!response.ok) {
            statusText.innerText = "No data found. Try mapping them first!";
            return;
        }

        const data = await response.json();
        drawNetwork(data.nodes, data.edges);
        statusText.innerText = `Displaying network for ${username}`;
    } catch (error) {
        statusText.innerText = "Failed to load graph.";
    }
}

function drawNetwork(nodesData, edgesData) {
    const container = document.getElementById('mynetwork');

    const data = {
        nodes: new vis.DataSet(nodesData),
        edges: new vis.DataSet(edgesData)
    };

    const options = {
        nodes: { shape: 'dot', font: { color: '#ffffff' } },
        edges: { color: '#888888', smooth: { type: 'continuous' } },
        physics: {
            barnesHut: { gravitationalConstant: -2000, centralGravity: 0.3, springLength: 95 }
        }
    };

    network = new vis.Network(container, data, options);
}

// Add this variable at the top of your file below `let network = null;`
let nodesDataSet = null;

// Update your drawNetwork function slightly to capture the DataSet:
function drawNetwork(nodesData, edgesData) {
    const container = document.getElementById('mynetwork');

    nodesDataSet = new vis.DataSet(nodesData); // Capture it globally
    const edgesDataSet = new vis.DataSet(edgesData);

    const data = { nodes: nodesDataSet, edges: edgesDataSet };

    const options = {
        nodes: { shape: 'dot', font: { color: '#ffffff' } },
        edges: { color: '#888888', smooth: { type: 'continuous' } },
        physics: { barnesHut: { gravitationalConstant: -2000, centralGravity: 0.3, springLength: 95 } }
    };

    network = new vis.Network(container, data, options);
}

// NEW FUNCTION: Run the Analysis
async function runAnalysis() {
    const username = document.getElementById('username').value;
    const statusText = document.getElementById('status');

    if (!username || !network) return alert("Please load a graph first!");

    statusText.innerText = "Running Louvain Community Detection...";

    try {
        const response = await fetch(`/api/v1/graph/analyze/${username}`);
        const data = await response.json();

        if (data.flagged_nodes.length === 0) {
            statusText.innerText = `Analysis complete. Network looks clean! (0 rings found)`;
            return;
        }

        // Highlight the suspicious nodes
        let updatedNodes = [];
        data.flagged_nodes.forEach(nodeId => {
            // Check if the node actually exists in our current view
            if (nodesDataSet.get(nodeId)) {
                updatedNodes.push({
                    id: nodeId,
                    color: { background: '#ff5555', border: '#ff0000' },
                    borderWidth: 3,
                    shape: 'hexagon', // Change shape to make them stand out
                    title: '⚠️ SUSPICIOUS NODE: Potential Sybil Ring' // Tooltip on hover
                });
            }
        });

        // Push updates to the graph in real-time
        nodesDataSet.update(updatedNodes);

        statusText.innerText = `⚠️ ALERT: Found ${data.suspicious_rings.length} suspicious rings containing ${data.flagged_nodes.length} flagged accounts!`;
        statusText.style.color = "#ff5555";

    } catch (error) {
        statusText.innerText = "Analysis Failed.";
    }
}