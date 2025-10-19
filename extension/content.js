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
                <h3 id="hintai-title">💡 HintAI</h3>
                <div class="hintai-header-controls">
                    <button id="hintai-minimize" class="hintai-toggle" title="Minimize">_</button>
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

        // Minimize to circle
        document.getElementById('hintai-minimize').addEventListener('click', (e) => {
            e.stopPropagation();
            const isMinimized = sidebar.classList.toggle('minimized');
            const title = document.getElementById('hintai-title');

            // Change text based on state
            if (isMinimized) {
                title.textContent = 'HintAI';
            } else {
                title.textContent = '💡 HintAI';
            }

            // Save state
            localStorage.setItem('hintai-minimized', isMinimized);
        });

        // Click minimized circle to restore (but not if they just dragged it!)
        sidebar.addEventListener('click', (e) => {
            // Check if this was a drag or a real click
            const justDragged = sidebar.getAttribute('data-just-dragged') === 'true';

            if (sidebar.classList.contains('minimized') &&
                e.target.tagName !== 'BUTTON' &&
                !justDragged) {
                sidebar.classList.remove('minimized');
                document.getElementById('hintai-title').textContent = '💡 HintAI';
                localStorage.setItem('hintai-minimized', false);
            }

            // Reset the flag
            sidebar.setAttribute('data-just-dragged', 'false');
        });

        // Restore minimized state
        if (localStorage.getItem('hintai-minimized') === 'true') {
            sidebar.classList.add('minimized');
            document.getElementById('hintai-title').textContent = 'HintAI';
        }
    }

    makeDraggable(element) {
        /**
         * Make sidebar draggable by header (even when minimized!)
         */
        let isDragging = false;
        let hasMoved = false; // Track if actually moved during drag
        let offsetX = 0;
        let offsetY = 0;
        let startX = 0;
        let startY = 0;

        const onMouseDown = (e) => {
            // Only drag from header or when minimized
            const isHeader = e.target.closest('.hintai-header') || element.classList.contains('minimized');
            const isButton = e.target.tagName === 'BUTTON';

            // Don't drag if:
            // - Clicking a button (unless minimized)
            // - Clicking inside content area (to allow text selection)
            if (isButton && !element.classList.contains('minimized')) {
                return;
            }

            if (!isHeader && !element.classList.contains('minimized')) {
                return; // Allow text selection in content
            }

            isDragging = true;
            hasMoved = false;

            // Get current position
            const rect = element.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            startX = e.clientX;
            startY = e.clientY;

            // Visual feedback
            element.style.cursor = 'grabbing';

            e.preventDefault();
            e.stopPropagation();
        };

        const onMouseMove = (e) => {
            if (!isDragging) return;

            e.preventDefault();

            const x = e.clientX - offsetX;
            const y = e.clientY - offsetY;

            // Check if actually moved (more than 5px)
            const moved = Math.abs(e.clientX - startX) > 5 || Math.abs(e.clientY - startY) > 5;
            if (moved) {
                hasMoved = true;
            }

            // Update position
            element.style.left = x + 'px';
            element.style.top = y + 'px';
            element.style.right = 'auto';
            element.style.bottom = 'auto';

            // Save position
            localStorage.setItem('hintai-position', JSON.stringify({ left: x, top: y }));
        };

        const onMouseUp = () => {
            if (isDragging) {
                isDragging = false;
                element.style.cursor = element.classList.contains('minimized') ? 'move' : '';

                // Store whether this was a drag or just a click
                element.setAttribute('data-just-dragged', hasMoved ? 'true' : 'false');
            }
        };

        // Attach listeners
        element.addEventListener('mousedown', onMouseDown);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);

        // Restore saved position
        const savedPos = localStorage.getItem('hintai-position');
        if (savedPos) {
            try {
                const pos = JSON.parse(savedPos);
                element.style.left = pos.left + 'px';
                element.style.top = pos.top + 'px';
                element.style.right = 'auto';
                element.style.bottom = 'auto';
            } catch (e) {
                console.log('Could not restore position');
            }
        }
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
         * Wait 500ms after user stops typing before analyzing (faster!)
         */

        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // Show typing indicator immediately
        this.updateStatus('Typing...', 'analyzing');

        this.debounceTimer = setTimeout(() => {
            this.updateStatus('Analyzing...', 'analyzing');
            this.analyzeCode(code);
        }, 500); // Reduced from 2000ms to 500ms
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
                this.displayHint(message.text);
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

        // Handle invalid/unknown patterns with friendly messages
        const pattern = analysis.pattern === 'invalid' ? 'No code yet' :
                       analysis.pattern === 'unknown' ? 'Custom approach' :
                       analysis.pattern;

        const complexity = analysis.complexity === 'Unknown' ? 'Not analyzed' : analysis.complexity;

        container.innerHTML = `
            <h4>📊 Code Analysis</h4>
            <div class="analysis-item">
                <span class="label">Pattern:</span>
                <span class="value">${pattern}</span>
            </div>
            <div class="analysis-item">
                <span class="label">Complexity:</span>
                <span class="value">${complexity}</span>
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

    displayHint(text) {
        const container = document.getElementById('hintai-hints');

        // Show single dynamic hint that updates as they type
        container.innerHTML = `
            <h4>💡 Current Hint</h4>
            <div class="hint-item">
                <div class="hint-text">${text}</div>
            </div>
        `;
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
