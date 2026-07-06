class Student:
    def __init__(self, name, age, department):
        if not isinstance(age, int) or age <= 0:
            raise ValueError(f"Age must be a positive integer, got {age}")
        self.name = name
        self.age = age
        self.department = department

    def __str__(self):
        return f"Student({self.name}, {self.age}, {self.department})"

    def display_details(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")
        print(f"Department: {self.department}")

    def calculate_grade(self, marks):
        if not (0 <= marks <= 100):
            raise ValueError(f"Marks must be between 0 and 100, got {marks}")
        thresholds = [(90, "A"), (80, "B"), (70, "C"), (60, "D")]
        grade = next((g for threshold, g in thresholds if marks >= threshold), "F")
        return grade


def calculate_factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# Example usage
if __name__ == "__main__":
    s = Student("Alice", 20, "Computer Science")
    s.display_details()
    grade = s.calculate_grade(85)
    print(f"{s.name}'s grade for 85 marks: {grade}")
    print(f"Factorial of 5: {calculate_factorial(5)}")
