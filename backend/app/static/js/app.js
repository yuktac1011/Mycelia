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
        const response = await fetch(`/api/v1/jobs/status/${jobId}`);
        const data = await response.json();

        if (data.status === "SUCCESS") {
            clearInterval(interval);
            statusText.innerText = `Success! Saved ${data.result.nodes_saved} nodes. Loading graph...`;
            loadGraph(); // Automatically draw it!
        } else if (data.status === "FAILURE") {
            clearInterval(interval);
            statusText.innerText = "Extraction Failed. Check server logs.";
        }
    }, 2000); // Check every 2 seconds
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