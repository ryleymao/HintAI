# HintAI Installation Guide

Complete guide to get HintAI working on your machine and LeetCode!

---

## Prerequisites

- **Python 3.9+** installed
- **Google Chrome** browser
- **Git** (to clone the repo)
- **Internet connection** (for downloading the embedding model)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/ryleymao/HintAI.git
cd HintAI
```

---

## Step 2: Install Python Dependencies

### Option A: Using pip (recommended)

```bash
pip3 install -r requirements.txt
```

### Option B: Using virtual environment (isolated)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Note:** First time installation will download the `all-MiniLM-L6-v2` embedding model (~80MB). This is normal and only happens once.

---

## Step 3: Test the Demo (Optional but Recommended)

Before setting up the full system, verify the core engine works:

```bash
python3 demo.py
```

**Expected output:**
```
🚀 Initializing HintAI...
✓ Model loaded! Embedding dimension: 384
📚 Loading solution database...
  Embedded 6 solutions
✓ HintAI ready!

============================================================
TEST 1: User solving Two Sum with nested loops
============================================================
...
💡 Top Matches:
   1. [0.923] Two Sum - nested_loops
...
```

If you see this, the core RAG pipeline is working! ✅

---

## Step 4: Start the Backend Server

Open a terminal and start the FastAPI server:

```bash
python3 backend/api/main.py
```

**Expected output:**
```
🚀 Initializing HintAI Engine...
✓ HintAI Engine ready! (6 solutions loaded)
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal running!** The backend needs to be active for the Chrome extension to work.

### Verify Backend is Running

Open another terminal and test:

```bash
curl http://localhost:8000/
```

Should return:
```json
{
  "status": "online",
  "service": "HintAI API",
  "version": "1.0.0",
  "solutions_loaded": 6
}
```

---

## Step 5: Install Chrome Extension

### Load Extension in Chrome

1. **Open Chrome Extensions Page**
   - Go to `chrome://extensions/`
   - OR: Click menu → More Tools → Extensions

2. **Enable Developer Mode**
   - Toggle "Developer mode" in the top-right corner

3. **Load the Extension**
   - Click "Load unpacked"
   - Navigate to the `HintAI/extension` folder
   - Click "Select"

4. **Verify Installation**
   - You should see "HintAI - LeetCode Coding Assistant" in your extensions list
   - A 💡 icon should appear in your Chrome toolbar

### Pin the Extension (Recommended)

- Click the puzzle piece icon in Chrome toolbar
- Find "HintAI" and click the pin icon
- Now you can easily access settings

---

## Step 6: Test on LeetCode!

### Navigate to a LeetCode Problem

1. Go to [leetcode.com/problems/two-sum](https://leetcode.com/problems/two-sum)
2. Make sure you're on the problem page (not the description, but the coding editor)

### You Should See

- A **HintAI sidebar** appears on the right side of the page
- Status shows "Connected" (green dot)

### Write Some Code

Try typing this in the LeetCode editor:

```python
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
```

### After 2 Seconds (debounce)

- Sidebar updates with code analysis
- Shows: "Pattern: nested_loops, Complexity: O(n²)"
- Displays similarity match: "92% match: Two Sum - nested_loops"
- Shows progressive hints:
  - Level 1: "You're checking every pair - that's O(n²)..."
  - Level 2: "What data structure gives O(1) lookup?"
  - Level 3: "Try using a dictionary..."

**If you see this, everything is working perfectly!** 🎉

---

## Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'sentence_transformers'`

**Fix:** Install dependencies again
```bash
pip3 install -r requirements.txt
```

---

### Extension Not Appearing

**Problem:** No sidebar on LeetCode page

**Fixes:**
1. Check if backend is running (`curl http://localhost:8000/`)
2. Open Chrome DevTools (F12) → Console tab
3. Look for HintAI logs: `🚀 HintAI Extension Loaded`
4. Refresh the LeetCode page
5. Make sure you're on a **problem page** (URL: `leetcode.com/problems/...`)

---

### "Connection Error" in Sidebar

**Problem:** Sidebar shows "Disconnected" or "Connection Error"

**Fixes:**
1. Verify backend is running: `curl http://localhost:8000/`
2. Check terminal running the backend for errors
3. Click extension icon → "Test Backend Connection"
4. Make sure port 8000 isn't blocked by firewall

---

### Hints Not Appearing

**Problem:** Code analysis shows but no hints

**Possible causes:**
1. Code might not match any patterns in database yet
2. WebSocket connection interrupted
3. Check browser console (F12) for errors

**Fixes:**
- Try a more complete code snippet
- Click "Analyze Current Code" in extension popup
- Restart the backend server

---

### Model Download Fails

**Error:** `Error downloading sentence-transformers model`

**Fix:** Manual download
```bash
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

This downloads the model explicitly.

---

## Architecture Overview

Understanding how it works:

```
┌─────────────────┐
│  LeetCode Page  │
│  (Your Code)    │
└────────┬────────┘
         │
         │ Content Script captures code
         ↓
┌─────────────────┐
│ Chrome Extension│  ← You see hints here
│   (Sidebar UI)  │
└────────┬────────┘
         │
         │ WebSocket (ws://localhost:8000)
         ↓
┌─────────────────┐
│  FastAPI Server │  ← Running in terminal
│  (Backend)      │
└────────┬────────┘
         │
         │ Calls HintAI Engine
         ↓
┌─────────────────┐
│   HintAI Core   │
│ - AST Analyzer  │  ← Detects patterns
│ - Embedder      │  ← Converts to vectors
│ - RAG Search    │  ← Finds similar solutions
└─────────────────┘
```

---

## Usage Tips

### Manual Analysis
- Click extension icon → "Analyze Current Code" to force analysis

### Toggle Auto-Analyze
- If auto-analysis is distracting, turn it off in extension popup
- Use manual analysis button instead

### Collapse Sidebar
- Click the "−" button in sidebar header to collapse
- Gives you more screen space

### Progressive Hints
- Level 1: Gentle nudge in the right direction
- Level 2: More specific guidance
- Level 3: Near-solution hint

**Pro tip:** Try to solve with Level 1 first! Don't jump to Level 3 immediately.

---

## Next Steps

### Add More Problems
Edit `data/sample_solutions.py` to add more problems and hints!

### Customize Hints
Modify the hints in the database to match your learning style.

### Contribute
Found a bug? Have ideas? Open an issue on [GitHub](https://github.com/ryleymao/HintAI/issues)!

---

## Uninstall

### Remove Extension
1. Go to `chrome://extensions/`
2. Find HintAI
3. Click "Remove"

### Stop Backend
- Press `Ctrl+C` in the terminal running the server

### Delete Files
```bash
rm -rf HintAI
```

---

## Support

- **GitHub Issues:** [github.com/ryleymao/HintAI/issues](https://github.com/ryleymao/HintAI/issues)
- **README:** [github.com/ryleymao/HintAI#readme](https://github.com/ryleymao/HintAI#readme)

Happy coding! 🚀
