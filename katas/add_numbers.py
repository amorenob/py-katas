"""
Add Numbers Kata

Write a function that adds two numbers together.
"""

def kata_info():
    """Return kata metadata"""
    return {
        "id": "add-numbers",
        "title": "Add Two Numbers", 
        "description": "Write a function `add(a, b)` that returns the sum of two numbers.",
        "starter_code": "def add(a, b):\n    pass"
    }

def test_solution(user_code: str) -> dict:
    """Test the user's solution"""
    try:
        # Execute user code to define the function
        exec_globals = {}
        exec(user_code, exec_globals)
        
        # Get the add function
        add_func = exec_globals.get('add')
        if not add_func:
            return {
                "status": "ERROR",
                "message": "Function 'add' not found. Make sure you define a function named 'add'."
            }
        
        # Test cases
        test_cases = [
            (2, 3, 5),
            (0, 0, 0),
            (-1, 1, 0),
            (10, -5, 5),
            (100, 200, 300)
        ]
        
        for a, b, expected in test_cases:
            result = add_func(a, b)
            if result != expected:
                return {
                    "status": "FAIL",
                    "message": f"Test failed: add({a}, {b}) returned {result}, expected {expected}"
                }
        
        return {
            "status": "PASS", 
            "message": "All tests passed! Great job!"
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Error executing code: {str(e)}"
        }

# Example solution (for reference)
def add(a, b):
    """Example solution"""
    return a + b