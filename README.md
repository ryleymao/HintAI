# HintAI

**AI-powered coding assistant that provides real-time Socratic hints for LeetCode problems**

✨ **Open Source** | 🚀 **Ready to Use** | 💡 **Learn by Doing**

## What is HintAI?

HintAI analyzes your code as you write it and provides contextual hints to guide your thinking - without revealing the solution. Unlike static hints (like LeetCode Premium), HintAI:

- ✅ **Analyzes YOUR actual code** - Not generic hints, but tailored to what you wrote
- ✅ **Detects patterns** - Identifies nested loops, hash maps, two-pointer, recursion, etc.
- ✅ **Progressive hints** - Socratic method (Level 1 → 2 → 3) to guide your thinking
- ✅ **RAG-powered** - Uses semantic search to find similar solutions (87-92% accuracy)
- ✅ **Real-time feedback** - WebSocket streaming as you type (2s debounce)
- ✅ **Works on LeetCode** - Chrome extension integrates seamlessly
- ✅ **100% free & local** - No API costs, runs on your machine

## Demo

See the core RAG pipeline in action:

```bash
python3 demo.py
```

**Output:**
```
🚀 Initializing HintAI...
✓ HintAI ready!

============================================================
TEST 1: User solving Two Sum with nested loops
============================================================

📊 Code Analysis:
   Pattern detected: nested_loops
   Complexity estimate: O(n²)

🔍 Searching database for similar solutions...

💡 Top Matches:
   1. [0.923] Two Sum - nested_loops  ← 92% similarity!

💡 Level 1 Hint:
   You're checking every pair - that's O(n²). Think about what
   information you need to track as you iterate.
```

## Tech Stack

- **Backend:** Python, FastAPI, WebSockets
- **RAG System:** Sentence-Transformers (all-MiniLM-L6-v2) for 384D embeddings
- **Code Analysis:** AST parsing for pattern detection
- **Frontend:** Chrome extension with real-time UI overlay
- **Vector Search:** Cosine similarity for semantic matching

## Architecture

```
User writes code → Chrome extension captures → WebSocket → FastAPI backend
                                                              ↓
                                            AST Parser detects patterns
                                                              ↓
                                            RAG retrieves similar solutions
                                                              ↓
                                            Generate Socratic hint
                                                              ↓
                                            Return to user
```

## Quick Start

### 1. Install Dependencies

```bash
git clone https://github.com/ryleymao/HintAI.git
cd HintAI
pip3 install -r requirements.txt
```

### 2. Start Backend Server

```bash
python3 backend/api/main.py
```

Server runs on `http://localhost:8000`

### 3. Install Chrome Extension

1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension/` folder

### 4. Try it on LeetCode!

1. Go to any LeetCode problem
2. Start coding - the HintAI sidebar appears automatically
3. Get real-time hints as you type!

**Full installation guide:** See [INSTALLATION.md](INSTALLATION.md)

## Features

### 🔍 Code Analysis
- AST parsing to detect algorithm patterns
- Complexity estimation (O(1), O(n), O(n²), etc.)
- Loop detection (nested loops, single pass, recursion)
- Data structure usage tracking (hash maps, sets, stacks)

### 💡 Smart Hints
- **Level 1:** Gentle nudge - "Think about what data structure..."
- **Level 2:** More specific - "What gives O(1) lookup?"
- **Level 3:** Near-solution - "Try using a dictionary to store..."

### 🎯 RAG-Powered Matching
- Converts code to 384-dimensional embeddings
- Semantic similarity search finds matching patterns
- 87-92% accuracy on test cases
- Works even if your code is incomplete!

### ⚡ Real-Time Feedback
- WebSocket streaming for instant updates
- 2-second debounce (doesn't analyze every keystroke)
- Progressive hint reveal
- Beautiful sidebar UI

## Project Structure

```
HintAI/
├── backend/
│   ├── api/
│   │   └── main.py              # FastAPI server with WebSocket
│   ├── parser/
│   │   └── code_analyzer.py     # AST-based pattern detection
│   └── rag/
│       └── embedder.py          # Sentence-Transformers embeddings
├── data/
│   └── sample_solutions.py      # Knowledge base with hints
├── extension/
│   ├── manifest.json            # Chrome extension config
│   ├── content.js               # LeetCode page integration
│   ├── styles.css               # Sidebar UI styling
│   ├── background.js            # Extension service worker
│   ├── popup.html               # Extension settings UI
│   └── popup.js                 # Settings logic
├── demo.py                      # Standalone demo
└── requirements.txt             # Python dependencies
```

## How It Works

1. **You write code** on LeetCode
2. **Content script captures** your code from Monaco editor
3. **WebSocket sends** code to backend
4. **AST parser analyzes** structure and detects patterns
5. **Embedder converts** code + context to 384D vector
6. **Similarity search** finds best matching solution
7. **Progressive hints** stream back to sidebar
8. **You learn** without being spoiled!

## Contributing

Want to add more problems? Improve hints? Contributions welcome!

1. Fork the repo
2. Add your solutions to `data/sample_solutions.py`
3. Test with `python3 demo.py`
4. Submit a pull request

## Roadmap

- [x] Core RAG pipeline with embeddings
- [x] AST-based pattern detection
- [x] FastAPI WebSocket backend
- [x] Chrome extension with real-time UI
- [ ] More solution patterns (currently 6 problems)
- [ ] LLM integration for dynamic hint generation
- [ ] Support for more languages (JavaScript, Java, C++)
- [ ] PostgreSQL with pgvector for scale
- [ ] User progress tracking

## License

MIT License - See LICENSE file

## Author

Built by [@ryleymao](https://github.com/ryleymao)
