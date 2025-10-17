# HintAI

**AI-powered coding assistant that provides real-time Socratic hints for algorithm problems**

🚧 **Work in Progress** - Building in public!

## What is HintAI?

HintAI analyzes your code as you write it and provides contextual hints to guide your thinking - without revealing the solution. Unlike static hints (like LeetCode Premium), HintAI:

- ✅ Analyzes YOUR actual code in real-time
- ✅ Detects algorithm patterns (two-pointer, DP, sliding window)
- ✅ Generates personalized Socratic questions
- ✅ Learns from 1,000+ solution patterns
- ✅ Works on any coding platform (Chrome extension)

## Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL (pgvector), Redis
- **RAG System:** Sentence-Transformers for embeddings, semantic search
- **Code Analysis:** AST parsing for pattern detection
- **Frontend:** Chrome extension with WebSocket streaming
- **Testing:** Pytest with comprehensive coverage

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

## Getting Started

*Coming soon - under active development!*

## License

MIT License - See LICENSE file

## Author

Built by [@ryleymao](https://github.com/ryleymao)
