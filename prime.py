import math

def is_prime(num):
    if num <= 1:
        return False
    if num <= 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    for i in range(5, math.isqrt(num) + 1, 2):
        if num % i == 0:
            return False
    return True


if __name__ == "__main__":
    try:
        num = int(input("Enter a number: "))
        if is_prime(num):
            print(f"{num} is prime")
        else:
            print(f"{num} is not prime")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")