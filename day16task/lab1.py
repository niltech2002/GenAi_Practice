student_name = "Rudranil"


def greet_user():
    print("Hello, " + student_name + "! Welcome to the lab.")


# Create a function that takes user's name, email and location and prints a greeting message.
def user_details(name, email, location):
    print(f"Hello, {name}! Your email is {email} and you are located in {location}.")


def calculate_scores(mark1, mark2, mark3, mark4, mark5):
    marks = [mark1, mark2, mark3, mark4, mark5]
    total = sum(marks)
    average = total / 5
    highest = max(marks)
    lowest = min(marks)
    
    print(f"Total: {total}")
    print(f"Average: {average}")
    print(f"Highest: {highest}")
    print(f"Lowest: {lowest}")


def display_student_details(name, email, location, mark1, mark2, mark3, mark4, mark5):
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Location: {location}")
    print("Score Details:")
    calculate_scores(mark1, mark2, mark3, mark4, mark5)


greet_user()
 
user_details(
    "Rudranil",
    "rudranil@gmail.com",
    "Kolkata"
)
 
calculate_scores(
    90,
    87,
    92,
    95,
    88
)
 
display_student_details(
    "Rudranil",
    "rudranil@gmail.com",
    "Kolkata",
    90,
    87,
    92,
    95,
    88
)







