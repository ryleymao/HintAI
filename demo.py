"""
HintAI Demo - Complete End-to-End System

FLOW:
1. User pastes their code
2. We analyze it (AST parser detects pattern)
3. We embed it (convert to vector)
4. We search database (find similar solutions)
5. We retrieve hints (get appropriate guidance)
6. We show user the hint!

This demonstrates the CORE RAG pipeline working!
"""

import sys
sys.path.append('.')

from backend.parser.code_analyzer import CodeAnalyzer
from backend.rag.embedder import CodeEmbedder
from data.sample_solutions import SAMPLE_SOLUTIONS
import numpy as np


class HintAI:
    """
    Complete hint generation system

    ARCHITECTURE:
        User Code → Analyze → Embed → Search → Retrieve Hints → Return
    """

    def __init__(self):
        print("🚀 Initializing HintAI...")
        self.analyzer = CodeAnalyzer()
        self.embedder = CodeEmbedder()

        # Embed all solutions in our database
        print("📚 Loading solution database...")
        self._build_database()
        print("✓ HintAI ready!\n")

    def _build_database(self):
        """
        Pre-compute embeddings for all solutions

        WHY: We do this once at startup, so searches are fast later
        """
        self.solutions = SAMPLE_SOLUTIONS
        self.solution_embeddings = []

        for sol in self.solutions:
            # Embed: code + problem + approach for better matching
            embedding = self.embedder.embed_code_with_context(
                code=sol['code'],
                problem=sol['problem'],
                pattern=sol['approach']
            )
            self.solution_embeddings.append(embedding)

        print(f"  Embedded {len(self.solutions)} solutions")

    def get_hint(self, user_code: str, problem_name: str = None) -> dict:
        """
        Main function: Given user's code, return a helpful hint

        Args:
            user_code: The code the user wrote
            problem_name: Optional - what problem they're solving

        Returns:
            Dictionary with analysis, similar solutions, and hints
        """
        print("=" * 60)
        print("ANALYZING YOUR CODE")
        print("=" * 60)

        # STEP 1: Analyze code structure
        analysis = self.analyzer.analyze(user_code)
        print(f"\n📊 Code Analysis:")
        print(f"   Pattern detected: {analysis['pattern']}")
        print(f"   Complexity estimate: {analysis['complexity_estimate']}")
        print(f"   Loop count: {analysis['loop_count']}")

        # STEP 2: Embed user's code
        user_embedding = self.embedder.embed_code_with_context(
            code=user_code,
            problem=problem_name,
            pattern=analysis['pattern']
        )

        # STEP 3: Find similar solutions
        print(f"\n🔍 Searching database for similar solutions...")
        matches = self.embedder.find_most_similar(
            user_embedding,
            self.solution_embeddings,
            top_k=3
        )

        # STEP 4: Get hints from similar solutions
        print(f"\n💡 Top Matches:")
        hints_to_show = []

        for rank, (idx, score) in enumerate(matches, 1):
            sol = self.solutions[idx]
            print(f"\n   {rank}. [{score:.3f}] {sol['problem']} - {sol['approach']}")
            print(f"      Time: {sol['time_complexity']}, Space: {sol['space_complexity']}")

            # Collect hints from top match
            if rank == 1:
                hints_to_show = sol['hints']

        # STEP 5: Return structured result
        return {
            'analysis': analysis,
            'top_match': self.solutions[matches[0][0]],
            'similarity_score': matches[0][1],
            'hints': hints_to_show
        }

    def show_progressive_hints(self, hints: list):
        """Display hints progressively (Socratic method)"""
        print("\n" + "=" * 60)
        print("PROGRESSIVE HINTS")
        print("=" * 60)

        for level, hint in enumerate(hints, 1):
            print(f"\n💡 Level {level} Hint:")
            print(f"   {hint}")


def main():
    """Demo the system with example code"""

    # Initialize HintAI
    hint_ai = HintAI()

    # ===== TEST 1: Two Sum - Brute Force =====
    print("\n" + "=" * 60)
    print("TEST 1: User solving Two Sum with nested loops")
    print("=" * 60)

    user_code_1 = """
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

    result1 = hint_ai.get_hint(user_code_1, problem_name="Two Sum")
    hint_ai.show_progressive_hints(result1['hints'])

    # ===== TEST 2: Two Sum - Hash Map =====
    print("\n\n" + "=" * 60)
    print("TEST 2: User solving Two Sum with hash map")
    print("=" * 60)

    user_code_2 = """
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
"""

    result2 = hint_ai.get_hint(user_code_2, problem_name="Two Sum")
    hint_ai.show_progressive_hints(result2['hints'])

    # ===== TEST 3: Valid Parentheses =====
    print("\n\n" + "=" * 60)
    print("TEST 3: User solving Valid Parentheses")
    print("=" * 60)

    user_code_3 = """
def isValid(s):
    stack = []
    for char in s:
        if char in '({[':
            stack.append(char)
        else:
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0
"""

    result3 = hint_ai.get_hint(user_code_3, problem_name="Valid Parentheses")
    hint_ai.show_progressive_hints(result3['hints'])

    print("\n" + "=" * 60)
    print("✓ DEMO COMPLETE - HintAI is working!")
    print("=" * 60)


if __name__ == '__main__':
    main()
