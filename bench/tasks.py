"""Coding tasks + hidden test cases for the Ornith quality benchmark.

Add your own by appending to TASKS:
  name    short id (used in filenames)
  fn      the function name the model must define
  prompt  the instruction sent to the model
  cases   list of (input, expected) — `input` is passed as the function's single arg
"""

TASKS = [
    {
        "name": "merge_intervals",
        "fn": "merge_intervals",
        "prompt": (
            "Write a Python function `merge_intervals(intervals)` that takes a list of "
            "[start, end] integer intervals (possibly unsorted, possibly overlapping) and "
            "returns a new list of merged, non-overlapping intervals sorted by start. "
            "Touching intervals like [1,4] and [4,5] merge into [1,5]. "
            "Put the final solution in a single ```python code block."
        ),
        "cases": [
            ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
            ([[1, 4], [4, 5]], [[1, 5]]),
            ([], []),
            ([[1, 4], [0, 4]], [[0, 4]]),
            ([[1, 4], [2, 3]], [[1, 4]]),
            ([[1, 4], [5, 6]], [[1, 4], [5, 6]]),
            ([[2, 3], [1, 5], [6, 7]], [[1, 5], [6, 7]]),
        ],
    },
    {
        "name": "roman_to_int",
        "fn": "roman_to_int",
        "prompt": (
            "Write a Python function `roman_to_int(s)` that converts a Roman numeral string "
            "(valid, uppercase, 1..3999) to its integer value, handling subtractive notation "
            "(IV=4, IX=9, XL=40, CD=400, CM=900). "
            "Put the final solution in a single ```python code block."
        ),
        "cases": [
            ("III", 3), ("IV", 4), ("IX", 9), ("LVIII", 58),
            ("MCMXCIV", 1994), ("MMMCMXCIX", 3999), ("XL", 40), ("CD", 400),
        ],
    },
    {
        "name": "calc",
        "fn": "calc",
        "prompt": (
            "Write a Python function `calc(expr)` that evaluates an arithmetic expression "
            "string containing non-negative integers, the binary operators + - * /, and "
            "parentheses, with correct operator precedence and left-to-right associativity. "
            "Division is normal float division. Do NOT use eval/exec. "
            "Return the numeric result. Put the final solution in a single ```python code block."
        ),
        "cases": [
            ("1+2*3", 7), ("(1+2)*3", 9), ("2*3+4*5", 26), ("10/2-3", 2),
            ("2*(3+(4-1))", 12), ("(2+3)*(4-1)/3", 5), ("1-2-3", -4), ("100/10/2", 5),
        ],
    },
]
