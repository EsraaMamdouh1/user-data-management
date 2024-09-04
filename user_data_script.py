import os
import json
import pyodbc
from cryptography.fernet import Fernet
from getpass import getpass


# Use the generated key
KEY = b'ICBiE4dWseK76SwIrDyzvCCEFLrae0pNLzfktHetO3s='  # Ensure the key ends with '='

cipher = Fernet(KEY)

# Function to encrypt sensitive data
def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

# Function to decrypt sensitive data
def decrypt_data(data):
    return cipher.decrypt(data.encode()).decode()

# Function to parse command-line arguments
def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description="User Data Management Script")
    parser.add_argument('--file', type=str, default="user_data.txt", help="File name for storing user data")
    return parser.parse_args()

# Function to load existing user data from file
def load_user_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        else:
            return {}
    except IOError as e:
        print(f"Error loading user data: {e}")
        return {}

# Function to save user data to file
def save_user_data(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            print("Data saved successfully.")
    except IOError as e:
        print(f"Error saving user data: {e}")

# SQL Database Functions
def connect_to_db():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;'
            'DATABASE=UserDatabase;'
            'Trusted_Connection=yes;'
        )
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_table_if_not_exists(cursor):
    try:
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
        CREATE TABLE Users (
            user_id VARCHAR(255) PRIMARY KEY,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            age INT,
            gender VARCHAR(50),
            year_of_birth INT
        )
        """)
    except pyodbc.Error as e:
        print(f"Error creating table: {e}")

def insert_user_to_db(user_id, first_name, last_name, age, gender, year_of_birth):
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            create_table_if_not_exists(cursor)

            # Check if user_id already exists
            cursor.execute("SELECT COUNT(*) FROM Users WHERE user_id = ?", (user_id,))
            if cursor.fetchone()[0] > 0:
                print(f"User ID {user_id} already exists in the database.")
                return

            # Insert user data
            insert_query = """
            INSERT INTO Users (user_id, first_name, last_name, age, gender, year_of_birth)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (user_id, first_name, last_name, age, gender, year_of_birth))
            conn.commit()
            print(f"User ID {user_id} added to the database.")
        except pyodbc.Error as e:
            print(f"Error inserting user: {e}")
        finally:
            conn.close()

# Function to display all users from the SQL database
def display_all_users_db():
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users")
            rows = cursor.fetchall()

            if not rows:
                print("No users found in the database.")
            else:
                for row in rows:
                    print(f"User ID: {row.user_id}")
                    print(f"First Name: {row.first_name}")
                    print(f"Last Name: {row.last_name}")
                    print(f"Age: {row.age}")
                    print(f"Gender: {row.gender}")
                    print(f"Year of Birth: {row.year_of_birth}")
                    print("-" * 30)
        except pyodbc.Error as e:
            print(f"Error retrieving users: {e}")
        finally:
            conn.close()

# Function to search for a user by User ID in the SQL database
def search_user_by_id_db(user_id):
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()

            if user:
                print(f"User ID: {user.user_id}")
                print(f"First Name: {user.first_name}")
                print(f"Last Name: {user.last_name}")
                print(f"Age: {user.age}")
                print(f"Gender: {user.gender}")
                print(f"Year of Birth: {user.year_of_birth}")
            else:
                print(f"User ID {user_id} not found in the database.")
        except pyodbc.Error as e:
            print(f"Error searching for user: {e}")
        finally:
            conn.close()

# Validation functions
def is_unique_user_id(user_id, user_data):
    return user_id.isalnum() and encrypt_data(user_id) not in user_data

def is_valid_name(name):
    return name.isalpha()

def is_valid_age(age):
    return age.isdigit() and int(age) > 0

def is_valid_gender(gender):
    return gender in ["Male", "Female", "Other"]

def is_valid_year_of_birth(year_of_birth, age):
    return year_of_birth.isdigit() and len(year_of_birth) == 4 and (2024 - int(year_of_birth)) == int(age)

# Function to get validated input
def get_validated_input(prompt, validation_func, *args):
    while True:
        try:
            user_input = input(prompt)
            if validation_func(user_input, *args):
                return user_input
            else:
                print("Invalid input. Please try again.")
        except ValueError as e:
            print(f"Input error: {e}. Please try again.")

# Function to display all user data from JSON
def display_all_users_json(user_data):
    if not user_data:
        print("No user data available.")
    else:
        try:
            for encrypted_user_id, user_info in user_data.items():
                user_id = decrypt_data(encrypted_user_id)
                print(f"\nUser ID: {user_id}")
                for key, value in user_info.items():
                    print(f"{key.capitalize()}: {decrypt_data(value) if key in ['first_name', 'last_name'] else value}")
        except Exception as e:
            print(f"An error occurred while displaying user data: {e}")

# Function to search for a specific user by User ID in JSON
def search_user_by_id_json(user_data):
    user_id = input("Enter User ID to search: ")
    encrypted_search_id = encrypt_data(user_id)  # Encrypting the search ID

    print(f"Searching for encrypted User ID: {encrypted_search_id}")

    if encrypted_search_id in user_data:
        user_info = user_data[encrypted_search_id]
        print(f"User found: {user_info}")
    else:
        print("User ID not found.")

# Function to add a new user
def add_user(user_data, file_path, user_id, first_name, last_name, age, gender, year_of_birth):
    encrypted_user_id = encrypt_data(user_id)
    encrypted_first_name = encrypt_data(first_name)
    encrypted_last_name = encrypt_data(last_name)

    user_data[encrypted_user_id] = {
        "first_name": encrypted_first_name,
        "last_name": encrypted_last_name,
        "age": age,
        "gender": gender,
        "year_of_birth": year_of_birth
    }
    
    print(f"Adding user to file: {user_data[encrypted_user_id]}")

    save_user_data(user_data, file_path)

# Main program loop
def main():
    """Main function to handle user input and menu options."""
    args = parse_arguments()
    file_path = args.file
    user_data = load_user_data(file_path)
    
    while True:
        print("\nMenu:")
        print("1. Add new user")
        print("2. Display all users from file")
        print("3. Display all users from database")
        print("4. Search for a user by User ID in database")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")

        try:
            if choice == "1":
                # Collect User Data
                user_id = get_validated_input("Enter User ID: ", is_unique_user_id, user_data)
                first_name = get_validated_input("Enter First Name: ", is_valid_name)
                last_name = get_validated_input("Enter Last Name: ", is_valid_name)
                age = get_validated_input("Enter Age: ", is_valid_age)
                gender = get_validated_input("Enter Gender (Male/Female/Other): ", is_valid_gender)
                year_of_birth = get_validated_input("Enter Year of Birth: ", is_valid_year_of_birth, age)

                add_user(user_data, file_path, user_id, first_name, last_name, age, gender, year_of_birth)
                insert_user_to_db(user_id, first_name, last_name, age, gender, year_of_birth)

            elif choice == "2":
                display_all_users_json(user_data)

            elif choice == "3":
                display_all_users_db()

            elif choice == "4":
                user_id = input("Enter User ID to search: ")
                search_user_by_id_db(user_id)

            elif choice == "5":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please enter a number between 1 and 5.")
        
        except Exception as e:
            print(f"An error occurred: {e}")

# Run the main function
if __name__ == "__main__":
    main()






