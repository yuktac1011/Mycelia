# Mycelia: Ethical OSINT Graph & Threat Intelligence System

Mycelia is an advanced, production-ready Open-Source Intelligence (OSINT) system designed to map developer relationship graphs on GitHub and automatically identify coordinated inauthentic behavior (Sybil Attacks / Sockpuppet Rings) using network topology and graph algorithms.

Traditional OSINT tools are either prohibitively expensive enterprise systems or fragile scripts that violate privacy. Mycelia fills this gap by utilizing **Ethics-by-Design** principles alongside a high-throughput, asynchronous backend architecture.

---

## 🔬 Architectural Overview

1. **Client Layer:** A lightweight frontend utilizing `Vis.js` for real-time, physics-based canvas rendering of network graphs.
2. **API Gateway Layer:** Built with `FastAPI` (asynchronous Python), serving as a non-blocking request handler and rate-limiting gateway.
3. **Task Queue Layer:** Decoupled background task execution utilizing `Celery` with a `Redis` message broker, ensuring the main server never lags during deep network crawls.
4. **Ethics Engine (Middleware):** An inline sanitizer enforcing *Data Minimization* (stripping all personal identifying information (PII) before storage) and checking an *Opt-Out Registry*.
5. **Graph Database Layer:** Powered by `Neo4j` utilizing native graph structures to query up to 2-degrees of separation without costly SQL join queries.

---

## 🧮 Theoretical & Mathematical Framework

### 1. Louvain Modularity for Sybil Ring Detection
Coordinated botnets on social platforms often form tightly knit "cliques" where accounts follow each other to game popularity algorithms. Mycelia detects these anomalies using **Louvain Modularity**, which partitions the graph into communities by maximizing the modularity index $Q$:

$$Q = \frac{1}{2m} \sum_{ij} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

Where:
* $A_{ij}$ is the weight of the edge between nodes $i$ and $j$.
* $k_i$ and $k_j$ are the sum of the weights of the edges attached to nodes $i$ and $j$.
* $m$ is the sum of all edge weights in the network.
* $\delta(c_i, c_j)$ is the Kronecker delta function, which is $1$ if $i$ and $j$ are assigned to the same community, and $0$ otherwise.

### 2. Topological Anomaly Heuristics
Once communities are detected, they pass through a secondary heuristic filter to reduce false positives (e.g., separating an actual botnet from a natural group of student coworkers):

$$\text{Density } (D) = \frac{2|E|}{|V|(|V| - 1)}$$

A community is flagged as a **Sybil Ring** if:
1. The node count $|V|$ satisfies $3 \le |V| \le 15$.
2. The internal density $D > 0.8$ (representing a near-complete clique).
3. The external degree centrality is low (isolated from the rest of the network).

---

## 🛡️ Ethics-by-Design Compliance
Mycelia is designed to comply with modern privacy laws (GDPR, CCPA) through technical constraints built into the codebase:

* **Data Minimization:** No personal data (emails, location, phone numbers, bio strings) is allowed past the validation layer. The system only stores structural nodes (username, platform) and edges.
* **Consent Preservation:** If a target's username is registered in the Redis-backed Opt-Out cache, the `EthicsEngine` drops all associated nodes before they ever touch physical disk storage.
* **Infrastructure Protection:** Adaptive rate-limiting ensures the scrapers mimic human behaviors, protecting platform infrastructure from artificial load.

---

## 🛠️ Local Installation & Setup

### Prerequisites
* Docker & Docker Desktop
* Python 3.10+
* Virtual Environment manager

### 1. Clone & Set up Environment
```bash
git clone https://github.com/yourusername/Mycelia.git
cd Mycelia
python -m venv venv
./venv/Scripts/Activate.ps1   # Windows PowerShell
pip install -r requirements.txt