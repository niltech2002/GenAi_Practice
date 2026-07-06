public class Student {

    // Fields
    private String name;
    private int age;
    private String department;

    // Constructor
    public Student(String name, int age, String department) {
        this.name = name;
        this.age = age;
        this.department = department;
    }

    // Display student details
    public void displayDetails() {
        System.out.println("Name: " + name);
        System.out.println("Age: " + age);
        System.out.println("Department: " + department);
    }

    // Calculate grade based on marks
    public String calculateGrade(int marks) {
        String grade;
        if (marks >= 90) {
            grade = "A";
        } else if (marks >= 80) {
            grade = "B";
        } else if (marks >= 70) {
            grade = "C";
        } else if (marks >= 60) {
            grade = "D";
        } else {
            grade = "F";
        }
        System.out.println(name + "'s grade for " + marks + " marks: " + grade);
        return grade;
    }

    // Static method to calculate factorial
    public static long calculateFactorial(int n) {
        if (n < 0) {
            throw new IllegalArgumentException("Factorial is not defined for negative numbers");
        }
        if (n == 0 || n == 1) {
            return 1;
        }
        long result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    // Main method (entry point)
    public static void main(String[] args) {
        Student s = new Student("Alice", 20, "Computer Science");
        s.displayDetails();
        s.calculateGrade(85);

        // Factorial example
        System.out.println("Factorial of 5: " + calculateFactorial(5));
    }
}
