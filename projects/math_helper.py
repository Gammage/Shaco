# Define functions for each operation
def add(a, b):
    return a + b # fill in: return the sum

def subtract(a, b):
    return a - b  # fill in: return the difference


def multiply(a, b):
    return a * b  # fill in: return the product


def divide(a, b):
    if b == 0:
        return "cannot divide by zero"
    return a / b  # fill in: return the division


# Main program
if __name__ == '__main__':
    print("Welcome to Math Helper Bot!")

    # Ask user for two numbers
    num1 = float(input("Enter the first number: "))
    num2 = float(input("Enter the second number: "))

    # Ask user for operation
    operation = input("Choose operation (add/subtract/multiply/divide): ").lower()

    # Decide which function to call
    if operation == "add":
        print(add(num1, num2)) # call add(num1, num2) and print result
    elif operation == "subtract":
        print(subtract(num1, num2)) # call subtract(num1, num2) and print result
    elif operation == "multiply":
        print(multiply(num1, num2))  # call multiply(num1, num2) and print result
    elif operation == "divide":
        print(divide(num1, num2))  # call divide(num1, num2) and print result
    else:
        print("Invalid operation")
