import tkinter as tk
from tkinter import messagebox
import json
from amadeus import Client, ResponseError
import os
from datetime import datetime

# Initialize the Amadeus API client
amadeus = Client(
    client_id='GjhePLReGbWdfzVXdZBldBmmKAJ27l7d',  # Your API key
    client_secret='ZXYipad3RIsoy1JN',               # Your API secret
    hostname='test'                                 # Specify 'test' environment
)

class User:
    def __init__(self, username, email, password, tracked_flights=None, **kwargs):
        self.username = username
        self.email = email
        self.password = password  # In a real application, use password hashing
        self.tracked_flights = tracked_flights or []
        # Ignore any additional keyword arguments

    def add_tracked_flight(self, flight, price_alert=None):
        self.tracked_flights.append({'flight': flight, 'price_alert': price_alert})

    def remove_tracked_flight(self, flight_id):
        self.tracked_flights = [tf for tf in self.tracked_flights if tf['flight']['id'] != flight_id]

class UserManager:
    def __init__(self, user_file='users.json'):
        # Use absolute path to ensure correct file is accessed
        self.user_file = os.path.join(os.path.dirname(__file__), user_file)
        self.users = []
        self.load_users()

    def load_users(self):
        self.users = []
        allowed_keys = {'username', 'email', 'password', 'tracked_flights'}
        try:
            with open(self.user_file, 'r') as file:
                data = json.load(file)
                for user_data in data:
                    # Debug statement to print loaded user data
                    print(f"Loaded user data: {user_data}")
                    # Filter out any unexpected keys
                    filtered_user_data = {k: v for k, v in user_data.items() if k in allowed_keys}
                    user = User(**filtered_user_data)
                    self.users.append(user)
        except FileNotFoundError:
            pass  # No users to load if file doesn't exist
        except Exception as e:
            print(f"Error loading users: {e}")

    def save_users(self):
        data = [user.__dict__ for user in self.users]
        with open(self.user_file, 'w') as file:
            json.dump(data, file, default=lambda o: o.__dict__)

    def register_user(self, username, email, password):
        if any(user.email == email for user in self.users):
            return "Email already registered."
        new_user = User(username, email, password)
        self.users.append(new_user)
        self.save_users()
        return "Registration successful."

    def login_user(self, email, password):
        for user in self.users:
            if user.email == email:
                if user.password == password:
                    return "Login successful.", user
                else:
                    return "Incorrect password.", None
        return "Email not registered.", None

    def get_user_by_email(self, email):
        for user in self.users:
            if user.email == email:
                return user
        return None

    def reset_password(self, email, new_password):
        user = self.get_user_by_email(email)
        if user:
            user.password = new_password
            self.save_users()
            return "Password reset successful."
        return "Email not registered."

    def view_profile(self, email):
        user = self.get_user_by_email(email)
        if user:
            return f"Username: {user.username}, Email: {user.email}"
        return "User not found."

    def edit_profile(self, email, new_username=None, new_password=None):
        user = self.get_user_by_email(email)
        if user:
            if new_username:
                user.username = new_username
            if new_password:
                user.password = new_password
            self.save_users()
            return "Profile updated successfully."
        return "User not found."

    def delete_account(self, email):
        user = self.get_user_by_email(email)
        if user:
            self.users.remove(user)
            self.save_users()
            return "Account deleted successfully."
        return "User not found."

    def sign_out(self):
        return "Signed out successfully."

class App:
    def __init__(self, root):
        self.root = root
        self.user_manager = UserManager(user_file='users.json')
        self.current_user_email = None  # Keep track of the logged-in user
        self.current_user = None
        self.setup_main_window()

    def setup_main_window(self):
        self.root.title("Flight Price Tracker")
        self.root.geometry("300x400")

        tk.Button(self.root, text="Register", command=self.register).pack(pady=10)
        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)

    def register(self):
        def submit_registration():
            username = entry_username.get()
            email = entry_email.get()
            password = entry_password.get()
            message = self.user_manager.register_user(username, email, password)
            messagebox.showinfo("Registration", message)
            if message == "Registration successful.":
                register_window.destroy()

        register_window = tk.Toplevel(self.root)
        register_window.title("Register")

        tk.Label(register_window, text="Username").pack()
        entry_username = tk.Entry(register_window)
        entry_username.pack()

        tk.Label(register_window, text="Email").pack()
        entry_email = tk.Entry(register_window)
        entry_email.pack()

        tk.Label(register_window, text="Password").pack()
        entry_password = tk.Entry(register_window, show="*")
        entry_password.pack()

        tk.Button(register_window, text="Register", command=submit_registration).pack()

    def login(self):
        def submit_login():
            email = entry_email.get()
            password = entry_password.get()
            message, user = self.user_manager.login_user(email, password)
            messagebox.showinfo("Login", message)
            if message == "Login successful.":
                self.current_user_email = email
                self.current_user = user
                login_window.destroy()
                # Hide the main window
                self.root.withdraw()
                self.main_menu()
            else:
                messagebox.showerror("Login Failed", message)

        login_window = tk.Toplevel(self.root)
        login_window.title("Login")

        tk.Label(login_window, text="Email").pack()
        entry_email = tk.Entry(login_window)
        entry_email.pack()

        tk.Label(login_window, text="Password").pack()
        entry_password = tk.Entry(login_window, show="*")
        entry_password.pack()

        tk.Button(login_window, text="Login", command=submit_login).pack()

    def main_menu(self):
        menu_window = tk.Toplevel(self.root)
        menu_window.title("Main Menu")

        def search_flights_action():
            menu_window.destroy()
            self.search_flights()

        def view_tracked_flights_action():
            menu_window.destroy()
            self.view_tracked_flights()

        def profile_action():
            menu_window.destroy()
            self.user_profile()

        def sign_out_action():
            messagebox.showinfo("Sign Out", self.user_manager.sign_out())
            menu_window.destroy()
            self.current_user_email = None
            self.current_user = None
            # Show the main window again
            self.root.deiconify()

        tk.Button(menu_window, text="Search Flights", command=search_flights_action).pack(pady=5)
        tk.Button(menu_window, text="View Tracked Flights", command=view_tracked_flights_action).pack(pady=5)
        tk.Button(menu_window, text="Profile", command=profile_action).pack(pady=5)
        tk.Button(menu_window, text="Sign Out", command=sign_out_action).pack(pady=5)

    def search_flights(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Flights")

        tk.Label(search_window, text="Origin (IATA code)").pack()
        entry_origin = tk.Entry(search_window)
        entry_origin.pack()

        tk.Label(search_window, text="Destination (IATA code)").pack()
        entry_destination = tk.Entry(search_window)
        entry_destination.pack()

        tk.Label(search_window, text="Departure Date (YYYY-MM-DD)").pack()
        entry_date = tk.Entry(search_window)
        entry_date.pack()

        tk.Label(search_window, text="Return Date (YYYY-MM-DD)").pack()
        entry_return_date = tk.Entry(search_window)
        entry_return_date.pack()

        tk.Label(search_window, text="Number of Passengers").pack()
        entry_passengers = tk.Entry(search_window)
        entry_passengers.pack()

        def perform_search():
            origin = entry_origin.get().strip().upper()
            destination = entry_destination.get().strip().upper()
            departure_date = entry_date.get().strip()
            return_date = entry_return_date.get().strip()
            passengers = entry_passengers.get().strip()

            # Input validation
            if not origin or not destination or not departure_date or not passengers:
                messagebox.showerror("Input Error", "Please fill in all required fields.")
                return

            if not passengers.isdigit() or int(passengers) <= 0:
                messagebox.showerror("Input Error", "Please enter a valid number of passengers.")
                return

            # Validate date format
            date_format = "%Y-%m-%d"
            try:
                datetime.strptime(departure_date, date_format)
                if return_date:
                    datetime.strptime(return_date, date_format)
            except ValueError:
                messagebox.showerror("Input Error", "Please enter dates in YYYY-MM-DD format.")
                return

            try:
                search_params = {
                    'originLocationCode': origin,
                    'destinationLocationCode': destination,
                    'departureDate': departure_date,
                    'adults': int(passengers),
                    'nonStop': False,
                    'max': 10
                }
                if return_date:
                    search_params['returnDate'] = return_date

                response = amadeus.shopping.flight_offers_search.get(**search_params)
                flights = response.data
                if flights:
                    search_window.destroy()
                    self.display_search_results(flights)
                else:
                    messagebox.showinfo("Search Results", "No flights found.")
            except ResponseError as error:
                # Extract detailed error message
                error_data = error.response.result
                if 'errors' in error_data:
                    error_message = error_data['errors'][0].get('detail', 'An error occurred.')
                else:
                    error_message = 'An error occurred.'
                messagebox.showerror("Error", f"An error occurred: {error_message}")

        def back_to_main_menu():
            search_window.destroy()
            self.main_menu()

        tk.Button(search_window, text="Search", command=perform_search).pack()
        tk.Button(search_window, text="Back to Main Menu", command=back_to_main_menu).pack(pady=5)

    def display_search_results(self, flights):
        results_window = tk.Toplevel(self.root)
        results_window.title("Search Results")

        results_frame = tk.Frame(results_window)
        results_frame.pack()

        for flight in flights:
            frame = tk.Frame(results_frame)
            frame.pack(fill="x", pady=5)

            # Extract flight details
            flight_info = flight['itineraries'][0]['segments'][0]
            airline = flight_info['carrierCode']
            departure = flight_info['departure']
            arrival = flight_info['arrival']
            price = flight['price']['total']
            flight_id = flight['id']

            info_text = f"Flight ID: {flight_id}, Airline: {airline}, Price: ${price}"
            tk.Label(frame, text=info_text).pack(side="left")

            def track_flight(flight_data=flight):
                self.track_flight(flight_data)
                messagebox.showinfo("Flight Tracking", "Flight added to your tracking list.")

            tk.Button(frame, text="Track Flight", command=track_flight).pack(side="right")

        def back_to_main_menu():
            results_window.destroy()
            self.main_menu()

        tk.Button(results_window, text="Back to Main Menu", command=back_to_main_menu).pack(pady=5)

    def track_flight(self, flight):
        # Add the flight to the current user's tracked flights
        price_alert = None  # Default, can be set later
        self.current_user.add_tracked_flight(flight, price_alert)
        self.user_manager.save_users()

    def view_tracked_flights(self):
        tracked_window = tk.Toplevel(self.root)
        tracked_window.title("Tracked Flights")

        if not self.current_user.tracked_flights:
            tk.Label(tracked_window, text="You have no tracked flights.").pack()
            return

        for tf in self.current_user.tracked_flights:
            flight = tf['flight']
            price_alert = tf.get('price_alert')
            frame = tk.Frame(tracked_window)
            frame.pack(fill="x", pady=5)

            flight_id = flight['id']
            price = flight['price']['total']
            airline = flight['itineraries'][0]['segments'][0]['carrierCode']
            flight_info = f"Flight ID: {flight_id}, Airline: {airline}, Current Price: ${price}"
            if price_alert:
                flight_info += f", Price Alert: ${price_alert}"
            tk.Label(frame, text=flight_info).pack(side="left")

            def edit_alert(flight_id=flight_id):
                self.edit_price_alert(flight_id)

            def remove_tracked(flight_id=flight_id):
                self.current_user.remove_tracked_flight(flight_id)
                self.user_manager.save_users()
                messagebox.showinfo("Tracked Flights", "Flight removed from tracking list.")
                tracked_window.destroy()
                self.view_tracked_flights()

            tk.Button(frame, text="Edit Alert", command=edit_alert).pack(side="left")
            tk.Button(frame, text="Remove", command=remove_tracked).pack(side="left")

            # Check for price alerts
            self.check_price_alert(flight, price_alert)

        def back_to_main_menu():
            tracked_window.destroy()
            self.main_menu()

        tk.Button(tracked_window, text="Back to Main Menu", command=back_to_main_menu).pack(pady=5)

    def check_price_alert(self, flight, price_alert):
        flight_id = flight['id']
        try:
            search_params = {
                'originLocationCode': flight['itineraries'][0]['segments'][0]['departure']['iataCode'],
                'destinationLocationCode': flight['itineraries'][0]['segments'][-1]['arrival']['iataCode'],
                'departureDate': flight['itineraries'][0]['segments'][0]['departure']['at'].split('T')[0],
                'adults': 1,
                'max': 1
            }
            response = amadeus.shopping.flight_offers_search.get(**search_params)
            updated_flight = response.data[0]
            current_price = updated_flight['price']['total']
            if price_alert and float(current_price) <= float(price_alert):
                messagebox.showinfo(
                    "Price Alert",
                    f"Price for flight {flight_id} has dropped to ${current_price}."
                )
        except ResponseError as error:
            print(f"Error updating flight {flight_id}: {error}")
        except Exception as e:
            print(f"Unexpected error while checking price alert for flight {flight_id}: {e}")

    def edit_price_alert(self, flight_id):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Price Alert")

        tk.Label(edit_window, text="Set new price alert").pack()
        entry_price_alert = tk.Entry(edit_window)
        entry_price_alert.pack()

        def submit_new_alert():
            try:
                new_price_alert = float(entry_price_alert.get())
                for tf in self.current_user.tracked_flights:
                    if tf['flight']['id'] == flight_id:
                        tf['price_alert'] = new_price_alert
                        self.user_manager.save_users()
                        messagebox.showinfo("Price Alert", "Price alert updated.")
                        edit_window.destroy()
                        return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for the price alert.")

        tk.Button(edit_window, text="Submit", command=submit_new_alert).pack()

    def user_profile(self):
        profile_window = tk.Toplevel(self.root)
        profile_window.title("User Profile")

        # Display user profile information
        profile_info = self.user_manager.view_profile(self.current_user_email)
        tk.Label(profile_window, text=profile_info).pack()

        # Update Profile
        def show_update_fields():
            update_window = tk.Toplevel(profile_window)
            update_window.title("Update Profile")

            tk.Label(update_window, text="New Username").pack()
            entry_new_username = tk.Entry(update_window)
            entry_new_username.pack()

            tk.Label(update_window, text="New Password").pack()
            entry_new_password = tk.Entry(update_window, show="*")
            entry_new_password.pack()

            def update_profile():
                new_username = entry_new_username.get()
                new_password = entry_new_password.get()
                message = self.user_manager.edit_profile(self.current_user_email, new_username, new_password)
                messagebox.showinfo("Profile Update", message)
                if message == "Profile updated successfully.":
                    update_window.destroy()
                    profile_window.destroy()
                    self.user_profile()

            tk.Button(update_window, text="Submit", command=update_profile).pack()

        tk.Button(profile_window, text="Update Profile", command=show_update_fields).pack()

        # Delete Account
        def delete_account_action():
            if messagebox.askyesno("Delete Account", "Are you sure you want to delete your account?"):
                message = self.user_manager.delete_account(self.current_user_email)
                messagebox.showinfo("Delete Account", message)
                profile_window.destroy()
                self.current_user_email = None
                self.current_user = None
                # Show the main window again
                self.root.deiconify()

        tk.Button(profile_window, text="Delete Account", command=delete_account_action).pack()

        # Back to Main Menu
        def back_to_main_menu():
            profile_window.destroy()
            self.main_menu()

        tk.Button(profile_window, text="Back to Main Menu", command=back_to_main_menu).pack()

def main():
        root = tk.Tk()
        app = App(root)
        root.mainloop()

if __name__ == "__main__":
    main()
