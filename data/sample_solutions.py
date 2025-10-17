"""
Sample Solutions Database

WHY: This is our knowledge base - examples of problems, solutions,
     and hints to guide users.

STRUCTURE: Each entry has:
- problem: Problem name
- approach: What approach/pattern this solution uses
- code: The actual solution code
- hints: Progressive hints (Level 1 → 2 → 3)
"""

SAMPLE_SOLUTIONS = [
    # ===== TWO SUM =====
    {
        "problem": "Two Sum",
        "approach": "nested_loops",
        "description": "Brute force approach checking all pairs",
        "code": """
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
""",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "hints": [
            "You're checking every pair - that's O(n²). Think about what information you need to track as you iterate.",
            "For each number, you're looking for its complement (target - number). What data structure gives O(1) lookup?",
            "Try using a dictionary to store numbers you've seen. For each new number, check if (target - number) is in the dictionary."
        ]
    },
    {
        "problem": "Two Sum",
        "approach": "hash_map",
        "description": "Optimized approach using hash map for O(1) lookup",
        "code": """
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
""",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "hints": [
            "Great! You're using a hash map for O(1) lookups. This is the optimal approach.",
            "Make sure you're storing the INDEX, not just the number.",
            "Edge case: What if the same number appears twice?"
        ]
    },

    # ===== VALID PARENTHESES =====
    {
        "problem": "Valid Parentheses",
        "approach": "stack",
        "description": "Using stack to match opening and closing brackets",
        "code": """
def isValid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}

    for char in s:
        if char in mapping:
            if not stack or stack[-1] != mapping[char]:
                return False
            stack.pop()
        else:
            stack.append(char)

    return len(stack) == 0
""",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "hints": [
            "Think about LIFO (Last In, First Out) - which data structure does that?",
            "When you see a closing bracket, what should the most recent opening bracket be?",
            "Use a stack: push opening brackets, pop when you see matching closing brackets."
        ]
    },

    # ===== BEST TIME TO BUY AND SELL STOCK =====
    {
        "problem": "Best Time to Buy and Sell Stock",
        "approach": "single_pass",
        "description": "Track minimum price and maximum profit in one pass",
        "code": """
def maxProfit(prices):
    min_price = float('inf')
    max_profit = 0

    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > max_profit:
            max_profit = price - min_price

    return max_profit
""",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "hints": [
            "You need to track two things: the lowest price so far, and the best profit so far.",
            "For each price, calculate: what if I bought at the lowest price and sold today?",
            "You only need one loop - update minimum price and maximum profit as you go."
        ]
    },

    # ===== CONTAINS DUPLICATE =====
    {
        "problem": "Contains Duplicate",
        "approach": "hash_set",
        "description": "Use set to track seen numbers",
        "code": """
def containsDuplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
""",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "hints": [
            "What data structure can tell you if you've seen something before in O(1)?",
            "Think about using a set to track numbers as you iterate.",
            "For each number, check: is it already in the set? If yes, you found a duplicate!"
        ]
    },

    # ===== REVERSE STRING =====
    {
        "problem": "Reverse String",
        "approach": "two_pointer",
        "description": "Two pointers from both ends, swap and move inward",
        "code": """
def reverseString(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
""",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "hints": [
            "You can do this in-place without extra space. Think about swapping elements.",
            "Use two pointers: one at the start, one at the end. What should they do?",
            "Swap elements at left and right pointers, then move them toward each other."
        ]
    }
]


def get_solutions_by_problem(problem_name: str):
    """Get all solutions for a specific problem"""
    return [sol for sol in SAMPLE_SOLUTIONS if sol['problem'] == problem_name]


def get_solutions_by_approach(approach: str):
    """Get all solutions using a specific approach"""
    return [sol for sol in SAMPLE_SOLUTIONS if sol['approach'] == approach]


def get_all_problems():
    """Get list of all problem names"""
    return list(set(sol['problem'] for sol in SAMPLE_SOLUTIONS))


if __name__ == '__main__':
    print("Sample Solutions Database")
    print("=" * 60)
    print(f"Total solutions: {len(SAMPLE_SOLUTIONS)}")
    print(f"Problems covered: {', '.join(get_all_problems())}")
    print()

    # Show Two Sum solutions
    print("Two Sum approaches:")
    for sol in get_solutions_by_problem("Two Sum"):
        print(f"  - {sol['approach']}: {sol['time_complexity']}")
