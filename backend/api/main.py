"""
FastAPI Backend - WebSocket Server for Real-Time Hint Generation

WHY: We need a server that can:
1. Accept user code from Chrome extension
2. Analyze it in real-time
3. Stream hints back via WebSocket
4. Handle multiple concurrent users

ARCHITECTURE:
    Chrome Extension → WebSocket → FastAPI → HintAI Engine → Stream Hints Back
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
import json
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.parser.code_analyzer import CodeAnalyzer
from backend.rag.embedder import CodeEmbedder
from data.sample_solutions import SAMPLE_SOLUTIONS

app = FastAPI(title="HintAI API", version="1.0.0")

# CORS - Allow Chrome extension to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Chrome extension origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HintAIEngine:
    """
    Core hint generation engine (singleton)

    WHY SINGLETON: We only want to load the embedding model ONCE
                   (it's expensive to load, but cheap to use)
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Load models and build database once at startup"""
        print("🚀 Initializing HintAI Engine...")
        self.analyzer = CodeAnalyzer()
        self.embedder = CodeEmbedder()

        # Pre-compute embeddings for all solutions
        print("📚 Building solution database...")
        self.solutions = SAMPLE_SOLUTIONS
        self.solution_embeddings = []

        for sol in self.solutions:
            embedding = self.embedder.embed_code_with_context(
                code=sol['code'],
                problem=sol['problem'],
                pattern=sol['approach']
            )
            self.solution_embeddings.append(embedding)

        print(f"✓ HintAI Engine ready! ({len(self.solutions)} solutions loaded)")

    def get_hint(self, user_code: str, problem_name: Optional[str] = None) -> Dict:
        """
        Main hint generation function

        Args:
            user_code: The code user wrote
            problem_name: Optional problem name from LeetCode

        Returns:
            Dictionary with analysis, matches, and hints
        """
        # Step 1: Analyze code
        analysis = self.analyzer.analyze(user_code)

        # Step 2: Embed user's code
        user_embedding = self.embedder.embed_code_with_context(
            code=user_code,
            problem=problem_name,
            pattern=analysis['pattern']
        )

        # Step 3: Find similar solutions
        matches = self.embedder.find_most_similar(
            user_embedding,
            self.solution_embeddings,
            top_k=3
        )

        # Step 4: Get hints from best match
        best_match_idx = matches[0][0]
        best_match_score = matches[0][1]
        best_solution = self.solutions[best_match_idx]

        return {
            'analysis': {
                'pattern': analysis['pattern'],
                'complexity': analysis['complexity_estimate'],
                'loop_count': analysis['loop_count']
            },
            'similarity_score': float(best_match_score),
            'matched_solution': {
                'problem': best_solution['problem'],
                'approach': best_solution['approach'],
                'time_complexity': best_solution['time_complexity'],
                'space_complexity': best_solution['space_complexity']
            },
            'hints': best_solution['hints'],
            'top_matches': [
                {
                    'problem': self.solutions[idx]['problem'],
                    'approach': self.solutions[idx]['approach'],
                    'similarity': float(score)
                }
                for idx, score in matches
            ]
        }


# Initialize engine at startup
hint_engine = HintAIEngine()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "HintAI API",
        "version": "1.0.0",
        "solutions_loaded": len(hint_engine.solutions)
    }


@app.post("/api/analyze")
async def analyze_code(request: Dict):
    """
    REST endpoint for code analysis

    Body:
        {
            "code": "def twoSum(nums, target): ...",
            "problem": "Two Sum"  # optional
        }

    Returns:
        Full analysis with hints
    """
    try:
        code = request.get('code', '')
        problem = request.get('problem')

        if not code.strip():
            return {"error": "No code provided"}

        result = hint_engine.get_hint(code, problem)
        return result

    except Exception as e:
        return {"error": str(e)}


@app.websocket("/ws/hints")
async def websocket_hints(websocket: WebSocket):
    """
    WebSocket endpoint for real-time hint streaming

    WHY WEBSOCKET:
    - Real-time bidirectional communication
    - User types → we analyze instantly
    - We can stream hints progressively (Level 1 → 2 → 3)

    PROTOCOL:
        Client sends: {"code": "...", "problem": "Two Sum"}
        Server sends: {"type": "analysis", "data": {...}}
                     {"type": "hint", "level": 1, "text": "..."}
                     {"type": "hint", "level": 2, "text": "..."}
                     {"type": "complete"}
    """
    await websocket.accept()
    print(f"✓ WebSocket client connected")

    try:
        while True:
            # Wait for message from Chrome extension
            data = await websocket.receive_text()
            message = json.loads(data)

            code = message.get('code', '')
            problem = message.get('problem')

            if not code.strip():
                await websocket.send_json({
                    "type": "error",
                    "message": "No code provided"
                })
                continue

            # Get hints
            result = hint_engine.get_hint(code, problem)

            # Send analysis first
            await websocket.send_json({
                "type": "analysis",
                "data": result['analysis']
            })

            # Send similarity info
            await websocket.send_json({
                "type": "match",
                "data": result['matched_solution'],
                "similarity": result['similarity_score']
            })

            # Stream hints progressively (Socratic method!)
            for level, hint_text in enumerate(result['hints'], 1):
                await websocket.send_json({
                    "type": "hint",
                    "level": level,
                    "text": hint_text
                })

            # Signal completion
            await websocket.send_json({
                "type": "complete"
            })

    except WebSocketDisconnect:
        print("✗ WebSocket client disconnected")
    except Exception as e:
        print(f"✗ WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Starting HintAI Backend Server")
    print("=" * 60)
    print("REST API: http://localhost:8000/api/analyze")
    print("WebSocket: ws://localhost:8000/ws/hints")
    print("Docs: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
