/**
 * Content Script - Runs on LeetCode problem pages
 *
 * RESPONSIBILITIES:
 * 1. Detect when user is on a LeetCode problem page
 * 2. Capture the code editor content
 * 3. Extract problem name
 * 4. Send code to backend via WebSocket
 * 5. Display hints in a sidebar overlay
 *
 * WHY CONTENT SCRIPT:
 * Content scripts can access the DOM of the page, so we can:
 * - Read the Monaco editor (LeetCode's code editor)
 * - Inject our hint sidebar
 * - Monitor code changes in real-time
 */

console.log('🚀 HintAI Extension Loaded');

class HintAIClient {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.currentCode = '';
        this.debounceTimer = null;
        this.sidebarElement = null;

        this.init();
    }

    init() {
        // Create hint sidebar UI
        this.createSidebar();

        // Connect to backend
        this.connectWebSocket();

        // Start monitoring code editor
        this.startCodeMonitoring();
    }

    createSidebar() {
        /**
         * Create floating sidebar for hints
         *
         * DESIGN:
         * - Fixed position on right side
         * - Collapsible
         * - Shows hints progressively
         * - Doesn't block code view
         */

        // Check if sidebar already exists
        if (document.getElementById('hintai-sidebar')) {
            this.sidebarElement = document.getElementById('hintai-sidebar');
            return;
        }

        const sidebar = document.createElement('div');
        sidebar.id = 'hintai-sidebar';
        sidebar.className = 'hintai-sidebar';

        sidebar.innerHTML = `
            <div class="hintai-header" id="hintai-header">
                <h3>💡 HintAI</h3>
                <div class="hintai-header-controls">
                    <button id="hintai-minimize" class="hintai-toggle" title="Minimize">_</button>
                    <button id="hintai-toggle" class="hintai-toggle" title="Collapse">−</button>
                </div>
            </div>
            <div class="hintai-content" id="hintai-content">
                <div class="hintai-status">
                    <span class="status-dot"></span>
                    <span id="hintai-status">Connecting...</span>
                </div>
                <div id="hintai-analysis" class="hintai-section"></div>
                <div id="hintai-hints" class="hintai-section"></div>
            </div>
        `;

        document.body.appendChild(sidebar);
        this.sidebarElement = sidebar;

        // Make draggable
        this.makeDraggable(sidebar);

        // Toggle collapse
        document.getElementById('hintai-toggle').addEventListener('click', (e) => {
            e.stopPropagation();
            const content = document.getElementById('hintai-content');
            const isCollapsed = content.style.display === 'none';
            content.style.display = isCollapsed ? 'block' : 'none';
            document.getElementById('hintai-toggle').textContent = isCollapsed ? '−' : '+';
        });

        // Minimize to circle
        document.getElementById('hintai-minimize').addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('minimized');
        });

        // Click minimized circle to restore
        sidebar.addEventListener('click', () => {
            if (sidebar.classList.contains('minimized')) {
                sidebar.classList.remove('minimized');
            }
        });
    }

    makeDraggable(element) {
        /**
         * Make sidebar draggable by header
         */
        const header = document.getElementById('hintai-header');
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;

        header.addEventListener('mousedown', (e) => {
            // Don't drag if clicking buttons
            if (e.target.tagName === 'BUTTON') return;

            isDragging = true;
            initialX = e.clientX - element.offsetLeft;
            initialY = e.clientY - element.offsetTop;
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;

                element.style.left = currentX + 'px';
                element.style.top = currentY + 'px';
                element.style.right = 'auto'; // Remove right positioning
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
    }

    connectWebSocket() {
        /**
         * Establish WebSocket connection to backend
         *
         * WHY: Real-time bidirectional communication
         *      User types → instant analysis → stream hints back
         */

        try {
            this.websocket = new WebSocket('ws://localhost:8000/ws/hints');

            this.websocket.onopen = () => {
                console.log('✓ Connected to HintAI backend');
                this.isConnected = true;
                this.updateStatus('Connected', 'success');
            };

            this.websocket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleServerMessage(message);
            };

            this.websocket.onerror = (error) => {
                console.error('✗ WebSocket error:', error);
                this.updateStatus('Connection Error', 'error');
            };

            this.websocket.onclose = () => {
                console.log('✗ Disconnected from HintAI backend');
                this.isConnected = false;
                this.updateStatus('Disconnected - Start backend server', 'error');

                // Try to reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            };

        } catch (error) {
            console.error('✗ Failed to connect:', error);
            this.updateStatus('Backend server not running', 'error');
        }
    }

    startCodeMonitoring() {
        /**
         * Monitor LeetCode editor for code changes
         *
         * CHALLENGE: LeetCode uses Monaco editor (same as VS Code)
         *            We need to access the editor instance
         *
         * SOLUTION: Look for the Monaco editor in the DOM and
         *           listen for content changes
         */

        // Try to find the editor every second until we find it
        const findEditor = setInterval(() => {
            const editor = this.getCodeEditor();
            if (editor) {
                console.log('✓ Found LeetCode code editor');
                clearInterval(findEditor);
                this.attachEditorListener(editor);
            }
        }, 1000);
    }

    getCodeEditor() {
        /**
         * Extract Monaco editor instance from LeetCode page
         *
         * Monaco editor stores instance in the DOM element
         */

        // LeetCode's code editor class
        const editorElement = document.querySelector('.monaco-editor');

        if (!editorElement) return null;

        // Try to get editor content from textarea
        const textarea = document.querySelector('.monaco-editor textarea');
        return textarea;
    }

    attachEditorListener(editorElement) {
        /**
         * Listen for code changes in the editor
         *
         * DEBOUNCING: Don't analyze on every keystroke (too expensive!)
         *             Wait 2 seconds after user stops typing
         */

        // Use MutationObserver to detect content changes
        const observer = new MutationObserver(() => {
            const code = this.extractCode();
            if (code && code !== this.currentCode) {
                this.currentCode = code;
                this.scheduleAnalysis(code);
            }
        });

        // Also listen to input events
        editorElement.addEventListener('input', () => {
            const code = this.extractCode();
            if (code && code !== this.currentCode) {
                this.currentCode = code;
                this.scheduleAnalysis(code);
            }
        });

        // Start observing
        const editorContainer = document.querySelector('.monaco-editor');
        if (editorContainer) {
            observer.observe(editorContainer, {
                childList: true,
                subtree: true,
                characterData: true
            });
        }
    }

    extractCode() {
        /**
         * Extract code from Monaco editor
         *
         * METHODS:
         * 1. Try to get from Monaco API (if accessible)
         * 2. Fallback: Parse from DOM
         */

        // Method 1: Try Monaco API
        if (window.monaco && window.monaco.editor) {
            const editors = window.monaco.editor.getModels();
            if (editors && editors.length > 0) {
                return editors[0].getValue();
            }
        }

        // Method 2: Parse from DOM (fallback)
        const lines = document.querySelectorAll('.view-line');
        if (lines.length > 0) {
            return Array.from(lines)
                .map(line => line.textContent)
                .join('\n');
        }

        return '';
    }

    extractProblemName() {
        /**
         * Extract problem name from LeetCode page
         *
         * LOCATION: Usually in the page title or header
         */

        // Try multiple selectors
        const selectors = [
            'a[href^="/problems/"]',
            '.question-title',
            'div[data-cy="question-title"]'
        ];

        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                return element.textContent.trim();
            }
        }

        // Fallback: Parse from URL
        const match = window.location.pathname.match(/\/problems\/([^\/]+)/);
        if (match) {
            return match[1].replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        }

        return null;
    }

    scheduleAnalysis(code) {
        /**
         * Debounce code analysis
         *
         * Wait 2 seconds after user stops typing before analyzing
         */

        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        this.updateStatus('Analyzing...', 'analyzing');

        this.debounceTimer = setTimeout(() => {
            this.analyzeCode(code);
        }, 2000);
    }

    analyzeCode(code) {
        /**
         * Send code to backend for analysis
         */

        if (!this.isConnected) {
            this.updateStatus('Not connected to backend', 'error');
            return;
        }

        const problemName = this.extractProblemName();

        this.websocket.send(JSON.stringify({
            code: code,
            problem: problemName
        }));
    }

    handleServerMessage(message) {
        /**
         * Handle messages from backend
         *
         * MESSAGE TYPES:
         * - analysis: Code pattern and complexity
         * - match: Best matching solution
         * - hint: Progressive hint (level 1, 2, 3)
         * - complete: Analysis finished
         * - error: Something went wrong
         */

        switch (message.type) {
            case 'analysis':
                this.displayAnalysis(message.data);
                break;

            case 'match':
                this.displayMatch(message.data, message.similarity);
                break;

            case 'hint':
                this.displayHint(message.level, message.text);
                break;

            case 'complete':
                this.updateStatus('Ready', 'success');
                break;

            case 'error':
                this.updateStatus('Error: ' + message.message, 'error');
                break;
        }
    }

    updateStatus(text, type) {
        const statusElement = document.getElementById('hintai-status');
        if (statusElement) {
            statusElement.textContent = text;
            statusElement.className = 'status-' + type;
        }
    }

    displayAnalysis(analysis) {
        const container = document.getElementById('hintai-analysis');
        container.innerHTML = `
            <h4>📊 Code Analysis</h4>
            <div class="analysis-item">
                <span class="label">Pattern:</span>
                <span class="value">${analysis.pattern}</span>
            </div>
            <div class="analysis-item">
                <span class="label">Complexity:</span>
                <span class="value">${analysis.complexity}</span>
            </div>
        `;
    }

    displayMatch(match, similarity) {
        const container = document.getElementById('hintai-analysis');
        const matchHtml = `
            <div class="match-info">
                <span class="similarity-badge">${(similarity * 100).toFixed(0)}% match</span>
                <div class="match-details">
                    ${match.problem} - ${match.approach}
                </div>
                <div class="complexity-info">
                    Time: ${match.time_complexity} | Space: ${match.space_complexity}
                </div>
            </div>
        `;
        container.innerHTML += matchHtml;
    }

    displayHint(level, text) {
        const container = document.getElementById('hintai-hints');

        // Clear previous hints if this is level 1
        if (level === 1) {
            container.innerHTML = '<h4>💡 Hints</h4>';
        }

        const hintElement = document.createElement('div');
        hintElement.className = 'hint-item hint-level-' + level;
        hintElement.innerHTML = `
            <div class="hint-header">Level ${level}</div>
            <div class="hint-text">${text}</div>
        `;

        container.appendChild(hintElement);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new HintAIClient();
    });
} else {
    new HintAIClient();
}
