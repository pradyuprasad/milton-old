const backendUrl = 'http://localhost:8000/api';
let selectedSeries = {};
let query = '';

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded event fired");
    const analyzeBtn = document.getElementById('analyzeBtn');
    const queryInput = document.getElementById('queryInput');
    const searchNodesContainer = document.getElementById('searchNodesContainer');
    const nextBtn = document.getElementById('nextBtn');
    const resultsContainer = document.getElementById('resultsContainer');

    analyzeBtn.addEventListener('click', () => {
        console.log("Analyze button clicked");
        query = queryInput.value.trim();
        if (query) {
            startAnalysis(query);
        } else {
            alert('Please enter a query.');
        }
    });

    nextBtn.addEventListener('click', () => {
        console.log("Next button clicked");
        const searchNodes = document.querySelectorAll('.search-node');
        let allSelected = true;

        searchNodes.forEach(node => {
            const nodeId = node.getAttribute('data-node-id');
            if (!selectedSeries[nodeId]) {
                allSelected = false;
            }
        });

        if (!allSelected) {
            alert('Please select one series for each search node before proceeding.');
        } else {
            processSelectedSeries();
        }
    });

    function startAnalysis(query) {
        console.log("Starting analysis for query:", query);

        searchNodesContainer.innerHTML = '';
        resultsContainer.innerHTML = '';
        selectedSeries = {};
        nextBtn.style.display = 'none';

        console.log("Sending initial query to backend");
        fetch(`${backendUrl}/initial_query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Received data:', data);
            handleDAGResponse(data.dag);
            handleSearchResults(data.search_results);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function handleDAGResponse(dag) {
        console.log('Handling DAG response:', dag);
        const container = document.getElementById('dagVisualization');
        
        if (!dag || !dag.nodes) {
            console.error('Invalid DAG data:', dag);
            return;
        }

        const nodes = new vis.DataSet(
            dag.nodes
                .filter(node => node.node_type !== 'DisplayNode')
                .map(node => ({
                    id: node.id,
                    label: `${node.id}: ${node.task.substring(0, 20)}...`, // Truncate long tasks
                    shape: getNodeShape(node.node_type)
                }))
        );

        const edges = new vis.DataSet(
            dag.nodes
                .filter(node => node.node_type !== 'DisplayNode')
                .flatMap(node => 
                    node.dependencies.map(dep => ({ from: dep, to: node.id }))
                )
        );

        const data = { nodes, edges };

        const options = {
            layout: {
                hierarchical: {
                    direction: 'LR',
                    sortMethod: 'directed'
                }
            },
            edges: {
                arrows: 'to'
            }
        };

        try {
            new vis.Network(container, data, options);
            console.log('DAG visualization created');
        } catch (error) {
            console.error('Error creating DAG visualization:', error);
        }
    }

    function handleSearchResults(searchResults) {
        console.log('Handling search results:', searchResults);
        for (const nodeId in searchResults) {
            const results = searchResults[nodeId];
            displaySearchResults(nodeId, results);
        }
        nextBtn.style.display = 'block'; // Show the "Next" button after search results are displayed
    }

    function displaySearchResults(nodeId, results) {
        console.log('Displaying search results for node:', nodeId, results);
        const nodeDiv = document.createElement('div');
        nodeDiv.className = 'search-node';
        nodeDiv.setAttribute('data-node-id', nodeId);
        nodeDiv.innerHTML = `<h3>Search Results for Node ${nodeId}</h3>`;
        
        results.forEach(series => {
            const button = document.createElement('button');
            button.className = 'series-button';
            button.textContent = `${series.fred_id}: ${series.title}`;
            button.onclick = (event) => handleSeriesClick(nodeId, series, event);
            nodeDiv.appendChild(button);
        });

        searchNodesContainer.appendChild(nodeDiv);
    }

    function handleSeriesClick(nodeId, series, event) {
        console.log('Clicked series:', series);
        
        const previousButton = document.querySelector(`.search-node[data-node-id="${nodeId}"] .series-button.selected`);
        if (previousButton) {
            previousButton.classList.remove('selected');
        }
        
        event.target.classList.add('selected');
        
        selectedSeries[nodeId] = series;
    }

    function processSelectedSeries() {
        console.log('Processing selected series:', selectedSeries);
        fetch(`${backendUrl}/analyze_series`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                series_list: Object.values(selectedSeries)
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Received analysis result:', data);
            displayAnalysisResult(data.result);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function displayAnalysisResult(result) {
        const resultDiv = document.createElement('div');
        resultDiv.innerHTML = `<p>${result}</p>`;
        resultsContainer.appendChild(resultDiv);
    }

    function getNodeShape(nodeType) {
        switch (nodeType) {
            case 'SearchNode':
                return 'diamond';
            case 'CodeNode':
                return 'box';
            default:
                return 'dot';
        }
    }
});
