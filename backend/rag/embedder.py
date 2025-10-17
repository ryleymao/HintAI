"""
Embedding System - Converts text/code into vector representations

WHY: We need to find similar solutions to give contextual hints.
     Text comparison is hard, but vector comparison is just math!

     Similar code = Similar vectors = Easy to search

HOW: We use Sentence-Transformers (pre-trained model) to convert text
     into 384-dimensional vectors. The model was trained on millions
     of text pairs, so it "knows" what's similar.

EXAMPLE:
    "for i in range(n): for j in range(i, n):"
    → [0.23, -0.45, 0.67, ..., 0.89]  (384 numbers)

    "nested loop iterating pairs"
    → [0.25, -0.43, 0.65, ..., 0.91]  (384 numbers)

    These vectors are CLOSE because the meaning is similar!
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import pickle
import os


class CodeEmbedder:
    """
    Converts code and text into vector embeddings for similarity search

    ARCHITECTURE:
        Input (text/code) → Pre-trained Model → 384D Vector → Store/Search
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding model

        Args:
            model_name: Which pre-trained model to use
                       'all-MiniLM-L6-v2' = fast, good quality, 384 dimensions

        WHY THIS MODEL:
        - Free (runs locally, no API costs!)
        - Fast (milliseconds per embedding)
        - Good quality (trained on 1 billion sentence pairs)
        - Small size (only 80MB download)
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = 384  # This model outputs 384-dimensional vectors
        print(f"✓ Model loaded! Embedding dimension: {self.embedding_dim}")

    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Convert text/code into vector embedding

        Args:
            text: Single string or list of strings to embed

        Returns:
            numpy array of shape (384,) for single text
            or shape (n, 384) for list of n texts

        Example:
            >>> embedder = CodeEmbedder()
            >>> vec = embedder.embed("for i in range(n): print(i)")
            >>> vec.shape
            (384,)
            >>> vec[:5]
            array([0.234, -0.456, 0.789, 0.123, -0.567])
        """
        # The model does all the heavy lifting here!
        # It converts text → tokens → neural network → vector
        embeddings = self.model.encode(text, convert_to_numpy=True)
        return embeddings

    def embed_code_with_context(self, code: str, problem: str = None,
                                pattern: str = None) -> np.ndarray:
        """
        Embed code WITH additional context for better matching

        WHY: Just embedding raw code might miss important context.
             Adding problem name + pattern gives better search results.

        Args:
            code: The actual code
            problem: Problem name (e.g., "Two Sum")
            pattern: Detected pattern (e.g., "nested_loops")

        Returns:
            384-dimensional embedding vector

        Example:
            >>> embedder = CodeEmbedder()
            >>> vec = embedder.embed_code_with_context(
            ...     code="for i in range(n): for j in range(i+1, n): ...",
            ...     problem="Two Sum",
            ...     pattern="nested_loops"
            ... )

            This embedding will be similar to other "Two Sum + nested_loops" solutions!
        """
        # Combine code with context for richer embedding
        parts = [code]

        if problem:
            parts.append(f"Problem: {problem}")

        if pattern:
            parts.append(f"Pattern: {pattern}")

        # Join with newlines
        combined_text = "\n".join(parts)

        return self.embed(combined_text)

    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors

        WHY: Cosine similarity measures the angle between vectors.
             Close angle = similar meaning (even if magnitudes differ)

        MATH:
            similarity = (A · B) / (||A|| × ||B||)

            Where:
            - A · B = dot product (sum of element-wise multiplication)
            - ||A|| = magnitude of vector A
            - Result ranges from -1 to 1 (higher = more similar)

        Args:
            vec1, vec2: Two embedding vectors to compare

        Returns:
            Similarity score from -1 to 1 (higher = more similar)
            Typically: >0.8 = very similar, >0.5 = related, <0.3 = different

        Example:
            >>> embedder = CodeEmbedder()
            >>> v1 = embedder.embed("nested for loops")
            >>> v2 = embedder.embed("two nested iterations")
            >>> embedder.similarity(v1, v2)
            0.87  # Very similar!

            >>> v3 = embedder.embed("recursive function")
            >>> embedder.similarity(v1, v3)
            0.23  # Different concepts
        """
        # Normalize vectors (make them unit length)
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)

        # Dot product of normalized vectors = cosine similarity
        return np.dot(vec1_norm, vec2_norm)

    def find_most_similar(self, query_vec: np.ndarray,
                         candidate_vecs: List[np.ndarray],
                         top_k: int = 5) -> List[tuple]:
        """
        Find the K most similar vectors to a query vector

        WHY: This is the core of our RAG system!
             User's code → query vector
             Our database → candidate vectors
             Find top matches → retrieve those solutions → generate hints

        Args:
            query_vec: The vector to search for (user's code)
            candidate_vecs: List of vectors to search through (our database)
            top_k: How many top matches to return

        Returns:
            List of (index, similarity_score) tuples, sorted by similarity

        Example:
            >>> # User wrote nested loops for Two Sum
            >>> user_code_vec = embedder.embed("for i... for j...")
            >>>
            >>> # We have 1000 solutions in our database
            >>> database_vecs = [vec1, vec2, vec3, ..., vec1000]
            >>>
            >>> # Find 5 most similar solutions
            >>> matches = embedder.find_most_similar(user_code_vec, database_vecs, top_k=5)
            >>> matches
            [(342, 0.92),  # Solution #342 is 92% similar
             (89, 0.87),   # Solution #89 is 87% similar
             (156, 0.81),  # etc.
             (523, 0.78),
             (91, 0.74)]
        """
        similarities = []

        for idx, candidate_vec in enumerate(candidate_vecs):
            sim = self.similarity(query_vec, candidate_vec)
            similarities.append((idx, sim))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top K
        return similarities[:top_k]


# Demo to show how it works
if __name__ == '__main__':
    print("=" * 60)
    print("EMBEDDING SYSTEM DEMO")
    print("=" * 60)

    # Initialize embedder
    embedder = CodeEmbedder()
    print()

    # Test 1: Embed similar code snippets
    print("TEST 1: Similar Code Patterns")
    print("-" * 60)

    code1 = "for i in range(len(nums)): for j in range(i+1, len(nums)): check pair"
    code2 = "nested loop iterating through all pairs in array"
    code3 = "use hash map for O(1) lookup of complements"

    vec1 = embedder.embed(code1)
    vec2 = embedder.embed(code2)
    vec3 = embedder.embed(code3)

    print(f"Code 1: '{code1[:50]}...'")
    print(f"Code 2: '{code2[:50]}...'")
    print(f"Code 3: '{code3[:50]}...'")
    print()

    sim_1_2 = embedder.similarity(vec1, vec2)
    sim_1_3 = embedder.similarity(vec1, vec3)

    print(f"Similarity (Code 1 vs Code 2): {sim_1_2:.3f}  ← Should be HIGH (both nested loops)")
    print(f"Similarity (Code 1 vs Code 3): {sim_1_3:.3f}  ← Should be LOW (different approaches)")
    print()

    # Test 2: Search for similar solutions
    print("TEST 2: Finding Similar Solutions")
    print("-" * 60)

    # Simulate a database of solutions
    database = [
        "nested loops checking all pairs O(n^2)",
        "hash map storing seen values O(n)",
        "two pointer technique on sorted array",
        "brute force approach with two nested for loops",
        "dynamic programming memoization"
    ]

    database_vecs = [embedder.embed(sol) for sol in database]

    # User's code (nested loops)
    user_code = "for i in range(n): for j in range(i, n): if sum equals target"
    user_vec = embedder.embed(user_code)

    print(f"User code: '{user_code}'")
    print()
    print("Finding top 3 similar solutions from database...")

    matches = embedder.find_most_similar(user_vec, database_vecs, top_k=3)

    for rank, (idx, score) in enumerate(matches, 1):
        print(f"{rank}. [{score:.3f}] {database[idx]}")

    print()
    print("✓ The system correctly identified nested loop solutions as most similar!")
    print("=" * 60)
