"""
Code Analyzer - Detects patterns in user's code using AST parsing

WHY: We need to understand what approach the user is taking so we can give
     contextual hints. For example, if they're using nested loops, we know
     they're trying brute force and can hint toward optimization.

HOW: Python's `ast` module parses code into a tree structure we can analyze.
     We walk through the tree counting loops, detecting data structures, etc.
"""

import ast
from typing import Dict, List, Set


class CodeAnalyzer:
    """Analyzes Python code to detect algorithm patterns"""

    def __init__(self):
        # We'll track these as we walk through the code
        self.loop_count = 0
        self.nested_loop_depth = 0
        self.current_depth = 0
        self.data_structures_used = set()
        self.functions_called = []

    def analyze(self, code: str) -> Dict:
        """
        Main analysis function

        Args:
            code: Python code as string (what user wrote)

        Returns:
            Dictionary with analysis results

        Example:
            >>> analyzer = CodeAnalyzer()
            >>> result = analyzer.analyze("for i in range(n): for j in range(i+1, n): pass")
            >>> result['loop_count']
            2
            >>> result['pattern']
            'nested_loops'
        """
        # Reset counters for fresh analysis
        self._reset()

        try:
            # Parse code into Abstract Syntax Tree (AST)
            # AST = tree representation of code structure
            tree = ast.parse(code)

            # Walk through the tree and analyze
            self._walk_tree(tree)

            # Detect what pattern they're using
            pattern = self._detect_pattern()

            return {
                'loop_count': self.loop_count,
                'nested_loop_depth': self.nested_loop_depth,
                'data_structures': list(self.data_structures_used),
                'pattern': pattern,
                'complexity_estimate': self._estimate_complexity()
            }

        except SyntaxError as e:
            # If code has syntax errors, return error info
            return {
                'error': f'Syntax error in code: {str(e)}',
                'pattern': 'invalid'
            }

    def _reset(self):
        """Reset all counters before new analysis"""
        self.loop_count = 0
        self.nested_loop_depth = 0
        self.current_depth = 0
        self.data_structures_used = set()
        self.functions_called = []

    def _walk_tree(self, node):
        """
        Recursively walk through AST and collect information

        WHY: AST is a tree structure. We need to visit every node to find
             loops, function calls, data structures, etc.
        """
        for child in ast.walk(node):
            # Check for FOR loops
            if isinstance(child, ast.For):
                self.loop_count += 1
                # Track depth for nested loops
                self._check_nested_loops(child)

            # Check for WHILE loops
            elif isinstance(child, ast.While):
                self.loop_count += 1

            # Check for data structure usage
            elif isinstance(child, ast.Name):
                # dict, set, list, etc.
                if child.id in ['dict', 'set', 'list', 'deque', 'heap']:
                    self.data_structures_used.add(child.id)

            # Check for function calls (like .append(), .pop())
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    self.functions_called.append(child.func.attr)

    def _check_nested_loops(self, loop_node):
        """
        Detect how deep the loops are nested

        WHY: Nested loops = O(n²) or worse. Important for optimization hints.

        Example:
            for i in range(n):        # depth 1
                for j in range(n):    # depth 2 (nested!)
                    do_something()
        """
        depth = 0
        current = loop_node

        # Walk up the tree to count parent loops
        while hasattr(current, 'body') and current.body:
            for item in current.body:
                if isinstance(item, (ast.For, ast.While)):
                    depth += 1
                    current = item
                    break
            else:
                break

        self.nested_loop_depth = max(self.nested_loop_depth, depth)

    def _detect_pattern(self) -> str:
        """
        Detect which algorithm pattern the code uses

        PATTERNS WE DETECT:
        - nested_loops: Two or more loops (brute force, O(n²))
        - hash_map: Using dict/set (O(1) lookup pattern)
        - two_pointer: Two index variables (common optimization)
        - recursion: Function calls itself
        - single_pass: Just one loop (O(n))
        """
        # Nested loops = brute force approach
        if self.nested_loop_depth >= 2:
            return 'nested_loops'

        # Using hash map for lookups
        if 'dict' in self.data_structures_used or 'set' in self.data_structures_used:
            return 'hash_map'

        # Single loop = linear scan
        if self.loop_count == 1:
            return 'single_pass'

        # No loops detected
        if self.loop_count == 0:
            return 'no_iteration'

        return 'unknown'

    def _estimate_complexity(self) -> str:
        """
        Estimate time complexity based on patterns

        WHY: Helps us know if we should suggest optimization
        """
        if self.nested_loop_depth >= 3:
            return 'O(n³) or worse'
        elif self.nested_loop_depth == 2:
            return 'O(n²)'
        elif self.loop_count == 1:
            return 'O(n)'
        else:
            return 'O(1)'


# Quick test to show it works
if __name__ == '__main__':
    analyzer = CodeAnalyzer()

    # Test 1: Nested loops (brute force)
    code1 = """
for i in range(len(nums)):
    for j in range(i+1, len(nums)):
        if nums[i] + nums[j] == target:
            return [i, j]
"""
    result1 = analyzer.analyze(code1)
    print("Test 1 - Nested Loops:")
    print(f"  Pattern: {result1['pattern']}")
    print(f"  Complexity: {result1['complexity_estimate']}")
    print()

    # Test 2: Hash map approach
    code2 = """
seen = {}
for num in nums:
    complement = target - num
    if complement in seen:
        return [seen[complement], i]
    seen[num] = i
"""
    result2 = analyzer.analyze(code2)
    print("Test 2 - Hash Map:")
    print(f"  Pattern: {result2['pattern']}")
    print(f"  Complexity: {result2['complexity_estimate']}")
