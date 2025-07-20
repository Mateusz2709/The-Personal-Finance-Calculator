# Imported modules
import hashlib
import os
import logging
import csv
from datetime import datetime
from tabulate import tabulate

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='app.log')

income = 0
guest_expenses = []
logged_in = False
profile = {}
PROFILE_FILE = "user_list.csv"
EXPENSES_FILE = "expenses.csv"


# Hashes a password using SHA-256 for secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Creates a new user profile and saves it to the user list
def create_profile():
    global profile, logged_in

    name = input("Enter your name:\n")
    password = input("Enter your password:\n")

    if check_if_user_exists(name):
        print("Username already exists. Try again.")
        setup()
        return

    hashed_password = hash_password(password)
    initial_income = 0

    profile = {
        "name": name,
        "password": hashed_password,
        "income": initial_income
    }

    with open(PROFILE_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, hashed_password, initial_income])

    logged_in = True
    print(f"{name}, your profile is created!")
    main_menu()


# Checks if a user with the specified username already exists
def check_if_user_exists(username):
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username:
                    return True
    return False


# Displays the initial setup menu and handles user choice
def setup():
    print("1. Login")
    print("2. Create Profile")
    print("3. Continue as a guest")

    try:

        choice = int(input("Choose an option:\n"))

        if choice == 1:
            load_profile()
        elif choice == 2:
            create_profile()
        elif choice == 3:
            main_menu()
        else:

            raise ValueError("Invalid choice.")
    except ValueError as e:
        logging.warning(f"Setup error: {e}")
        print("Please enter a valid option.")
        setup()


# Loads an existing user profile by verifying username and password
def load_profile():
    global profile, income, logged_in

    name = input("Enter your name:\n")
    password = input("Enter your password:\n")

    hashed_password = hash_password(password)

    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as file:
            reader = csv.reader(file)

            for row in reader:
                if row[0] == name and row[1] == hashed_password:
                    profile = {
                        "name": name,
                        "password": hashed_password,
                        "income": float(row[2])
                    }
                    income = profile["income"]
                    logged_in = True

                    print(f"Welcome back {name}!")
                    main_menu()
                    return

    logging.warning(f"Failed login attempt for user: {name}")
    print("Login failed. Please try again.")
    setup()


# Deletes a user account and all associated expenses
def delete_user(username):
    global profile, logged_in

    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as file:
            rows = list(csv.reader(file))

        with open(PROFILE_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[0] != username:
                    writer.writerow(row)

    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, "r") as file:
            rows = list(csv.reader(file))

        with open(EXPENSES_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[0] != username:
                    writer.writerow(row)

    profile.clear()
    logged_in = False

    logging.info(f"Account and expenses deleted for user: {username}")
    print("Your account and all associated expenses have been deleted.")


# Resets all expenses for a given username
def reset_expenses(username):
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, "r") as file:
            rows = list(csv.reader(file))

        with open(EXPENSES_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[0] != username:
                    writer.writerow(row)

    main_menu()


# Displays the main menu and handles navigation to various features
def main_menu():
    while True:

        print("\nMain Menu")
        print("1. Enter Income")
        print("2. Add Expense")
        print("3. View Budget Summary")
        print("4. Generate Expense Report")

        if logged_in:
            print("5. Delete Account")
            print("6. Exit")
        else:
            print("5. Exit")

        try:

            choice = int(input("Enter your choice: ").strip())

            if choice == 1:
                enter_income()
            elif choice == 2:
                add_expense()
            elif choice == 3:
                view_budget()
            elif choice == 4:
                generate_expense_report()
            elif choice == 5 and logged_in:
                delete_user(profile["name"])
                print("Goodbye!")
                exit()
            elif choice == 5 and not logged_in or choice == 6:

                print("Goodbye!")
                exit()
            else:

                print("Please enter a valid option.")

        except ValueError:

            print(
                "Invalid input. Please enter a number corresponding to your choice."
            )


# Allows the user to enter their monthly income
def enter_income():
    global income

    while True:
        try:
            user_income = float(input("Enter your monthly income: "))

            if user_income < 0:
                print("Please enter a positive amount\n")
            else:
                break
        except ValueError:

            print("Invalid input. Please enter a number for the amount.")

    income = user_income

    if logged_in:
        profile["income"] = user_income
        update_user_profile(profile)
        logging.info(f"Income added for {profile['name']}: {user_income}")
    else:
        logging.info(f"Guest income entered: {user_income}")

    print(f"Your current income is {income}")


# Updates a user's profile in the user list
def update_user_profile(updated_profile):
    if "name" in updated_profile:
        profiles = []

        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == updated_profile["name"]:
                        profiles.append(
                            [row[0], row[1], updated_profile["income"]])
                    else:
                        profiles.append(row)

        with open(PROFILE_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(profiles)


# Adds a new expense for the logged-in user or a guest user
def add_expense():
    category = input("Enter the category for this expense:\n")
    description = input("Enter a description for this expense:\n")

    while True:
        try:
            amount = float(input("Enter the amount:\n"))
            if amount < 0:
                print("Please enter a positive amount.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number for the amount.")

    while True:
        expense_type = input(
            "Is this expense essential or non-essential? Enter 'E' for essential, 'N' for "
            "non-essential:\n").strip().upper()

        if expense_type in ("E", "N"):
            expense_type = "Essential" if expense_type == "E" else "Non-Essential"
            break
        else:
            print(
                "Invalid choice. Please enter 'E' for essential or 'N' for non-essential."
            )

    username = profile.get("name", "Guest")

    if logged_in:
        with open(EXPENSES_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                username,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category,
                description, amount, expense_type
            ])
            logging.info(
                f"Expense added to file: {category}, {description}, £{amount}, {expense_type}"
            )
    else:
        guest_expenses.append({
            "date":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category":
            category,
            "description":
            description,
            "amount":
            amount,
            "type":
            expense_type
        })
        logging.info(
            f"Guest expense added in memory: {category}, {description}, £{amount}, {expense_type}"
        )

    print(
        f"Expense added: {category}, {description}, £{amount}, {expense_type}."
    )


# Calculates the total expenses for the logged-in user or guest
def calculate_total_expenses():
    total = 0
    if logged_in:
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 5:
                        continue
                    if row[0] == profile["name"]:
                        try:
                            total += float(row[4])
                        except ValueError:
                            print(
                                f"Skipping a row with invalid amount format: {row[4]}"
                            )
    else:
        for expense in guest_expenses:
            total += expense["amount"]

    return total


# Generates and displays various expense reports based on user input
def generate_expense_report():
    while True:

        print("---Expense Generator---")
        print("1. View expenses by category")
        print("2. View expenses by date range")
        print("3. View expenses by type (Essential or Non-Essential)")
        print("4. View all expenses.")
        print("5. Return to Main Menu")

        try:

            choice = int(input("Enter your choice: ").strip())

            if choice == 1:

                category = input("Enter the category to filter by:\n")
                display_expenses_by_category(category)
            elif choice == 2:

                start_year = input("Enter start year(YYYY): ")
                start_month = input("Enter start month(MM): ")
                start_day = input("Enter start day(DD): ")
                start_date = f"{start_year}-{start_month}-{start_day}"

                end_year = input("Enter start year(YYYY): ")
                end_month = input("Enter start month(MM): ")
                end_day = input("Enter start day(DD): ")
                end_date = f"{end_year}-{end_month}-{end_day}"

                display_expenses_by_date(start_date, end_date)
            elif choice == 3:

                expense_type = input(
                    "Enter 'Essential' or 'Non-Essential' to filter by type: "
                ).strip().capitalize()
                display_expenses_by_type(expense_type)
            elif choice == 4:

                display_all_expenses()
            elif choice == 5:

                print("Returning to Main Menu...")
                return
            else:

                print("Invalid choice. Please enter a number between 1 and 5.")
                continue

            while True:
                next_action = input(
                    "\nWould you like to view another report? (y/n): ").strip(
                    ).lower()
                if next_action == 'y':
                    break
                elif next_action == 'n':
                    print("Returning to Main Menu...")
                    return
                else:
                    print(
                        "Invalid input. Please enter 'y' for yes or 'n' for no."
                    )

        except ValueError:

            print("Please enter a valid option.")


# Resets the user's income to zero and updates the profile
def reset_income():
    global income
    income = 0

    profile["income"] = income

    update_user_profile(profile)


# Displays a budget summary, including income, expenses, and remaining balance
def view_budget():
    global income

    total_expenses = calculate_total_expenses()
    remaining_budget = income - total_expenses

    feedback = get_spending_feedback(total_expenses, income)

    print("\n------Budget Summary------")
    print(f"Income: £{income}")
    print(f"Total Expenses: £{total_expenses}")
    print(f"Remaining Budget: £{remaining_budget}")
    print(feedback)

    print("1. Reset your account.")
    print("2. Return to Main Menu.")

    while True:
        choice = input("Enter your choice: ")
        if choice == "1":

            reset_income()
            if logged_in:
                reset_expenses(profile["name"])
            else:
                guest_expenses.clear()
            print("All expenses and income have been reset.")
            break
        elif choice == "2":

            main_menu()
            break
        else:

            print("Invalid choice. Please try again.")


# Provides feedback on spending habits based on income and expenses
def get_spending_feedback(total_expenses, income):
    if income == 0:
        return "🤔 Income missing! Are you living on air and good vibes? 🌬️✨"

    spending_ratio = total_expenses / income

    if spending_ratio < 0.5:
        return "💸 Money Maestro! Your budget’s tighter than a drum! Keep stacking those coins! 💰🐖"
    elif spending_ratio < 0.75:
        return "🧠 Budget Boss! You're spending smart, leaving room for a splurge here and there. Treat yo'self! 🍰🎈"
    elif spending_ratio < 1:
        return "🫣 Walking the Line! Just a few coins away from 'Uh-oh'... Maybe rethink that daily latte ☕️💸"
    else:
        return "🛑 Danger Zone! You’re in 'Champagne dreams on a lemonade budget' territory! 🍾➡️🥤"


# Displays expenses filtered by type (Essential or Non-Essential)
def display_expenses_by_type(expense_type):
    """
    Display expenses filtered by a specified expense type.
    """
    print(f"\n--- {expense_type.capitalize()} Expenses ---")
    found_expenses = False
    data_list = []

    if logged_in:
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 6:
                        continue
                    if row[0] == profile["name"] and row[5].strip().capitalize(
                    ) == expense_type.capitalize():
                        try:
                            formatted_date = datetime.strptime(
                                row[1],
                                "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                        except ValueError:
                            formatted_date = "Invalid date"
                        data_list.append([
                            formatted_date, row[2], row[3], f"£{row[4]}",
                            row[5]
                        ])
                        found_expenses = True
    else:
        for expense in guest_expenses:
            if expense["type"].capitalize() == expense_type.capitalize():
                try:
                    formatted_date = datetime.strptime(
                        expense["date"],
                        "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                except ValueError:
                    formatted_date = "Invalid date"
                data_list.append([
                    formatted_date, expense["category"],
                    expense["description"], f"£{expense['amount']}",
                    expense["type"]
                ])
                found_expenses = True

    if found_expenses:
        print(
            tabulate(data_list,
                     headers=[
                         "Date", "Category", "Description", "Amount",
                         "Expense Type"
                     ],
                     tablefmt="grid"))
    else:
        print(f"No {expense_type.lower()} expenses recorded.")


# Displays expenses filtered by a specified category
def display_expenses_by_category(category):
    """
    Display expenses filtered by the specified category.
    """
    print(f"\n--- Expenses in Category: {category} ---")
    found_expenses = False
    data_list = []

    if logged_in:
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 6:
                        continue
                    if row[0] == profile["name"] and row[2].strip().lower(
                    ) == category.strip().lower():
                        try:
                            formatted_date = datetime.strptime(
                                row[1],
                                "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                        except ValueError:
                            formatted_date = "Invalid date"
                        data_list.append(
                            [formatted_date, row[3], f"£{row[4]}"])
                        found_expenses = True
    else:
        for expense in guest_expenses:
            if expense["category"].strip().lower() == category.strip().lower():
                try:
                    formatted_date = datetime.strptime(
                        expense["date"],
                        "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                except ValueError:
                    formatted_date = "Invalid date"
                data_list.append([
                    formatted_date, expense["description"],
                    f"£{expense['amount']}"
                ])
                found_expenses = True

    if found_expenses:
        print(
            tabulate(data_list,
                     headers=["Date", "Description", "Amount"],
                     tablefmt="grid"))
    else:
        print(f"No expenses recorded in category '{category}'.")


# Displays all expenses for the logged-in user or guest user
def display_all_expenses():
    """
    Display all expenses for the logged-in user or guest user.
    """
    print("\n--- All Expenses ---")
    found_expenses = False
    data_list = []

    if logged_in:
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 6:
                        continue
                    if row[0] == profile["name"]:
                        try:
                            formatted_date = datetime.strptime(
                                row[1],
                                "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                        except ValueError:
                            formatted_date = "Invalid date"
                        data_list.append([
                            formatted_date, row[2], row[3], f"£{row[4]}",
                            row[5]
                        ])
                        found_expenses = True
    else:
        for expense in guest_expenses:
            try:
                formatted_date = datetime.strptime(
                    expense["date"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            except ValueError:
                formatted_date = "Invalid date"
            data_list.append([
                formatted_date, expense["category"], expense["description"],
                f"£{expense['amount']}", expense["type"]
            ])
            found_expenses = True

    if found_expenses:
        print(
            tabulate(data_list,
                     headers=[
                         "Date", "Category", "Description", "Amount",
                         "Expense Type"
                     ],
                     tablefmt="grid"))
    else:
        print("No expenses recorded yet.")


# Displays expenses filtered by a specified date range
def display_expenses_by_date(start_date, end_date):
    """
    Display expenses filtered by a specified date range.
    """
    print(f"\n--- Expenses from {start_date} to {end_date} ---")
    found_expenses = False
    data_list = []

    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Please enter dates in the correct format: YYYY-MM-DD")
        return

    if logged_in:
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 6:
                        continue
                    if row[0] == profile["name"]:
                        try:
                            row_date = datetime.strptime(
                                row[1], "%Y-%m-%d %H:%M:%S")
                            if start_date_parsed <= row_date <= end_date_parsed:
                                formatted_date = row_date.strftime("%Y-%m-%d")
                                data_list.append([
                                    formatted_date, row[2], row[3],
                                    f"£{row[4]}", row[5]
                                ])
                                found_expenses = True
                        except ValueError:
                            print(
                                f"Skipping a row with an invalid date format: {row[1]}"
                            )
    else:
        for expense in guest_expenses:
            try:
                expense_date = datetime.strptime(expense["date"],
                                                 "%Y-%m-%d %H:%M:%S")
                if start_date_parsed <= expense_date <= end_date_parsed:
                    formatted_date = expense_date.strftime("%Y-%m-%d")
                    data_list.append([
                        formatted_date, expense["category"],
                        expense["description"], f"£{expense['amount']}",
                        expense["type"]
                    ])
                    found_expenses = True
            except ValueError:
                print(
                    f"Skipping an expense with an invalid date format: {expense['date']}"
                )

    if found_expenses:
        print(
            tabulate(data_list,
                     headers=[
                         "Date", "Category", "Description", "Amount",
                         "Expense Type"
                     ],
                     tablefmt="grid"))
    else:
        print("No expenses recorded in this date range.")


# Prints a table using the tabulate library
def print_table(data, column_headers):
    table = tabulate(data, headers=column_headers, tablefmt="grid")
    print(table)


# Entry point of the program
if __name__ == "__main__":
    print("Welcome to Personal Finance Calculator")
    setup()
