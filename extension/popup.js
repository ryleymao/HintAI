/**
 * Popup Script - Controls for the extension popup
 */

document.addEventListener('DOMContentLoaded', () => {
    // Load settings
    loadSettings();

    // Check backend connection
    checkBackendConnection();

    // Event listeners
    document.getElementById('enabled-toggle').addEventListener('change', handleEnabledToggle);
    document.getElementById('auto-toggle').addEventListener('change', handleAutoToggle);
    document.getElementById('analyze-now').addEventListener('click', handleAnalyzeNow);
    document.getElementById('test-connection').addEventListener('click', handleTestConnection);
    document.getElementById('help-link').addEventListener('click', handleHelp);

    // Load stats
    loadStats();
});

function loadSettings() {
    chrome.storage.sync.get(['enabled', 'autoAnalyze'], (settings) => {
        document.getElementById('enabled-toggle').checked = settings.enabled !== false;
        document.getElementById('auto-toggle').checked = settings.autoAnalyze !== false;
    });
}

function handleEnabledToggle(event) {
    const enabled = event.target.checked;
    chrome.storage.sync.set({ enabled });

    // Notify content script
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, {
                type: 'settingsChanged',
                enabled
            });
        }
    });
}

function handleAutoToggle(event) {
    const autoAnalyze = event.target.checked;
    chrome.storage.sync.set({ autoAnalyze });

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, {
                type: 'settingsChanged',
                autoAnalyze
            });
        }
    });
}

function handleAnalyzeNow() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, {
                type: 'analyzeNow'
            });
        }
    });
}

function handleTestConnection() {
    const button = document.getElementById('test-connection');
    button.textContent = 'Testing...';
    button.disabled = true;

    fetch('http://localhost:8000/')
        .then(response => response.json())
        .then(data => {
            updateStatus(true, `Connected: ${data.solutions_loaded} solutions loaded`);
            button.textContent = 'Connection OK ✓';
            setTimeout(() => {
                button.textContent = 'Test Backend Connection';
                button.disabled = false;
            }, 2000);
        })
        .catch(error => {
            updateStatus(false, 'Backend not running - Start server with: python3 backend/api/main.py');
            button.textContent = 'Connection Failed ✗';
            setTimeout(() => {
                button.textContent = 'Test Backend Connection';
                button.disabled = false;
            }, 2000);
        });
}

function checkBackendConnection() {
    fetch('http://localhost:8000/')
        .then(response => response.json())
        .then(data => {
            updateStatus(true, 'Connected to backend');
        })
        .catch(error => {
            updateStatus(false, 'Backend offline - Start server');
        });
}

function updateStatus(isConnected, message) {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');

    indicator.className = 'status-dot ' + (isConnected ? 'connected' : 'disconnected');
    text.textContent = message;
}

function loadStats() {
    chrome.storage.local.get(['hintsGiven', 'problemsSolved'], (data) => {
        document.getElementById('hints-count').textContent = data.hintsGiven || 0;
        document.getElementById('problems-count').textContent = data.problemsSolved || 0;
    });
}

function handleHelp(event) {
    event.preventDefault();
    chrome.tabs.create({
        url: 'https://github.com/ryleymao/HintAI#readme'
    });
}
