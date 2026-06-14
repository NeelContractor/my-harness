# Review of `bubble_sort.py`

## Functionality
- The implementation correctly sorts a list using the classic bubble‑sort algorithm and returns the sorted list.
- It also includes a simple demonstration `print(bubble_sort(...))` which runs on import.

## Bugs / Logical Issues
- No bugs in the sorting logic itself.
- The demo `print` statement executes whenever the module is imported, which is undesirable for a library module.

## Style & Best Practices
- **PEP 8 compliance**: the file is very short, but a few improvements are possible:
  - Add a module‑level docstring describing the purpose.
  - Add a type hint for the function signature, e.g. `def bubble_sort(arr: list[int]) -> list[int]:`.
  - Use a `if __name__ == "__main__":` guard for the demo code.
  - Include an explicit `return` after the inner loop to avoid unnecessary iterations when the list becomes sorted early (optional optimization).
- Consider using `range(n - i - 1)` directly as done, but you could also break early when no swaps occur.

## Suggested Improvements
```python
"""Simple bubble‑sort implementation.

Provides a `bubble_sort` function that returns a **new** sorted list rather than
mutating the input, which is generally safer for callers.
"""

from __future__ import annotations
from typing import List


def bubble_sort(arr: List[int]) -> List[int]:
    """Return a sorted copy of *arr* using the bubble‑sort algorithm.

    The algorithm runs in O(n²) time and O(1) auxiliary space.
    """
    # Work on a copy to avoid side‑effects on the caller's list.
    result = arr.copy()
    n = len(result)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break
    return result


if __name__ == "__main__":
    sample = [64, 34, 25, 12, 22, 11, 90]
    print(bubble_sort(sample))
```

### Why these changes?
- **Docstrings** and type hints improve readability and IDE support.
- Working on a copy prevents surprising side‑effects for callers who may still need the original list.
- The `swapped` flag lets the algorithm stop early when the list is already sorted, saving time.
- Guarding the demo code ensures the module behaves as a pure library when imported.

## Quick Checklist
- ✅ No functional bugs in the original algorithm.
- ✅ Added documentation and typing.
- ✅ Removed unwanted side‑effects on import.
- ✅ Implemented early‑exit optimization.
- ✅ Provided a more Pythonic, reusable implementation.
