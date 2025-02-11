total_bill = float(input("Welcome to the tip calculator!\n What was the total bill? $"))

tip_percentage = int(input("How much would you like to tip? 10, 12, or 15? "))

number_of_people = int(input("How many people to split the bill? "))

amount_per_person = round((total_bill + (total_bill * (tip_percentage / 100)) / number_of_people), 2)

print(f"Each person should pay ${amount_per_person:.2f}")
