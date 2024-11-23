import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import threading
import time
import json
import datetime
import re
import os  

# -------------------------- User Management --------------------------

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password  

class UserManager:
    def __init__(self, user_file='users.txt'):
        self.user_file = user_file
        self.users = []
        self.load_users()
    
    def load_users(self):
        self.users = []
        try:
            with open(self.user_file, 'r') as file:
                for line in file:
                    username, email, password = line.strip().split(',')
                    user = User(username, email, password)
                    self.users.append(user)
        except FileNotFoundError:
            pass  # No users to load if file doesn't exist
    
    def save_users(self):
        with open(self.user_file, 'w') as file:
            for user in self.users:
                file.write(f"{user.username},{user.email},{user.password}\n")
    
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
                    return "Login successful."
                else:
                    return "Incorrect password."
        return "Email not registered."
    
    def reset_password(self, email, new_password):
        for user in self.users:
            if user.email == email:
                user.password = new_password
                self.save_users()
                return "Password reset successful."
        return "Email not registered."
    
    def view_profile(self, email):
        for user in self.users:
            if user.email == email:
                return f"Username: {user.username}, Email: {user.email}"
        return "User not found."
    
    def edit_profile(self, email, new_username=None, new_password=None):
        for user in self.users:
            if user.email == email:
                if new_username:
                    user.username = new_username
                if new_password:
                    user.password = new_password
                self.save_users()
                return "Profile updated successfully."
        return "User not found."
    
    def delete_account(self, email):
        for user in self.users:
            if user.email == email:
                self.users.remove(user)
                self.save_users()
                return "Account deleted successfully."
        return "User not found."
    
    def sign_out(self):
        return "Signed out successfully."

# -------------------------- Flight Tracking --------------------------

class FlightTracker:
    def __init__(self, tracker_file='tracked_flights.txt'):
        self.tracker_file = tracker_file
        self.tracked_flights = []
        self.load_tracked_flights()
        self.lock = threading.RLock()
    
    def load_tracked_flights(self):
        self.tracked_flights = []
        try:
            with open(self.tracker_file, 'r') as file:
                for line in file:
                    data = json.loads(line.strip())
                    self.tracked_flights.append(data)
        except FileNotFoundError:
            pass
    
    def save_tracked_flights(self):
        with open(self.tracker_file, 'w') as file:
            for flight in self.tracked_flights:
                file.write(json.dumps(flight) + '\n')
    
    def add_tracked_flight(self, user_email, flight_data, price_threshold):
        with self.lock:
            # Check if the flight is already being tracked by the user
            for flight in self.tracked_flights:
                if flight['user_email'] == user_email and flight['flight_id'] == flight_data['id']:
                    return "Flight is already being tracked."
            tracked_flight = {
                'user_email': user_email,
                'flight_id': flight_data['id'],
                'flight_data': flight_data,
                'price_threshold': price_threshold,
                'last_refreshed': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.tracked_flights.append(tracked_flight)
            self.save_tracked_flights()
            return "Flight added to tracking list."
    
    def get_user_tracked_flights(self, user_email):
        with self.lock:
            return [flight for flight in self.tracked_flights if flight['user_email'] == user_email]
    
    def remove_tracked_flight(self, user_email, flight_id):
        with self.lock:
            for flight in self.tracked_flights:
                if flight['user_email'] == user_email and flight['flight_id'] == flight_id:
                    self.tracked_flights.remove(flight)
                    self.save_tracked_flights()
                    return "Flight removed from tracking list."
            return "Flight not found in your tracking list."
    
    def update_price_threshold(self, user_email, flight_id, new_threshold):
        with self.lock:
            for flight in self.tracked_flights:
                if flight['user_email'] == user_email and flight['flight_id'] == flight_id:
                    flight['price_threshold'] = new_threshold
                    self.save_tracked_flights()
                    return "Price threshold updated."
            return "Flight not found in your tracking list."

# -------------------------- Notification Management --------------------------

class NotificationManager:
    def __init__(self, notification_file='notifications.txt'):
        self.notification_file = notification_file
        self.notifications = []
        self.load_notifications()
        self.lock = threading.RLock()

    def load_notifications(self):
        self.notifications = []
        try:
            with open(self.notification_file, 'r') as file:
                for line in file:
                    data = json.loads(line.strip())
                    self.notifications.append(data)
        except FileNotFoundError:
            pass

    def save_notifications(self):
        with open(self.notification_file, 'w') as file:
            for notification in self.notifications:
                file.write(json.dumps(notification) + '\n')

    def add_notification(self, user_email, message, timestamp, origin, destination):
        with self.lock:
            notification = {
                'user_email': user_email,
                'message': message,
                'timestamp': timestamp,
                'origin': origin,
                'destination': destination
            }
            self.notifications.append(notification)
            self.save_notifications()

    def get_user_notifications(self, user_email):
        with self.lock:
            return [n for n in self.notifications if n['user_email'] == user_email]

# -------------------------- Search History Management --------------------------

class SearchHistoryManager:
    def __init__(self, search_history_file='search_history.txt'):
        self.search_history_file = search_history_file
        self.search_history = []
        self.load_search_history()
        self.lock = threading.RLock()

    def load_search_history(self):
        self.search_history = []
        try:
            with open(self.search_history_file, 'r') as file:
                for line in file:
                    data = json.loads(line.strip())
                    self.search_history.append(data)
        except FileNotFoundError:
            pass

    def save_search_history(self):
        with open(self.search_history_file, 'w') as file:
            for entry in self.search_history:
                file.write(json.dumps(entry) + '\n')

    def add_search_entry(self, user_email, search_params, timestamp):
        with self.lock:
            entry = {
                'user_email': user_email,
                'search_params': search_params,
                'timestamp': timestamp
            }
            self.search_history.append(entry)
            self.save_search_history()

    def get_user_search_history(self, user_email):
        with self.lock:
            return [entry for entry in self.search_history if entry['user_email'] == user_email]

    def clear_user_search_history(self, user_email):
        with self.lock:
            self.search_history = [entry for entry in self.search_history if entry['user_email'] != user_email]
            self.save_search_history()

# -------------------------- Favorites Management --------------------------

class FavoritesManager:
    def __init__(self, favorites_file='favorites.txt'):
        self.favorites_file = favorites_file
        self.favorites = []
        self.load_favorites()
        self.lock = threading.RLock()

    def load_favorites(self):
        self.favorites = []
        try:
            with open(self.favorites_file, 'r') as file:
                for line in file:
                    data = json.loads(line.strip())
                    self.favorites.append(data)
        except FileNotFoundError:
            pass

    def save_favorites(self):
        with open(self.favorites_file, 'w') as file:
            for favorite in self.favorites:
                file.write(json.dumps(favorite) + '\n')

    def add_favorite(self, user_email, flight_data):
        with self.lock:
            # Check if the flight is already in favorites
            for fav in self.favorites:
                if fav['user_email'] == user_email and fav['flight_id'] == flight_data['id']:
                    return "Flight is already in favorites."
            favorite = {
                'user_email': user_email,
                'flight_id': flight_data['id'],
                'flight_data': flight_data
            }
            self.favorites.append(favorite)
            self.save_favorites()
            return "Flight added to favorites."

    def get_user_favorites(self, user_email):
        with self.lock:
            return [fav for fav in self.favorites if fav['user_email'] == user_email]

    def remove_favorite(self, user_email, flight_id):
        with self.lock:
            for fav in self.favorites:
                if fav['user_email'] == user_email and fav['flight_id'] == flight_id:
                    self.favorites.remove(fav)
                    self.save_favorites()
                    return "Flight removed from favorites."
            return "Flight not found in favorites."

# -------------------------- User Preferences Management --------------------------

class UserPreferencesManager:
    def __init__(self, preferences_file='user_preferences.json'):
        self.preferences_file = preferences_file
        self.preferences = {}
        self.lock = threading.RLock()
        self.load_preferences()
    
    def load_preferences(self):
        try:
            with open(self.preferences_file, 'r') as file:
                self.preferences = json.load(file)
        except FileNotFoundError:
            self.preferences = {}
    
    def save_preferences(self):
        with self.lock:
            with open(self.preferences_file, 'w') as file:
                json.dump(self.preferences, file, indent=4)
    
    def get_user_preferences(self, user_email):
        with self.lock:
            return self.preferences.get(user_email, {
                'preferred_airlines': [],
                'preferred_layovers': None,
                'automatic_updates': True,
                'update_interval': 1,                  # In minutes
                'currency': 'USD',
                'default_origin': ''
            })
    
    def set_user_preferences(self, user_email, new_preferences):
        with self.lock:
            self.preferences[user_email] = new_preferences
            self.save_preferences()

# -------------------------- Application Settings Management --------------------------

class AppSettingsManager:
    def __init__(self, settings_file='app_settings.json'):
        self.settings_file = settings_file
        self.settings = {}
        self.lock = threading.RLock()
        self.load_settings()
    
    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as file:
                self.settings = json.load(file)
        except FileNotFoundError:
            self.settings = {
                'notification_frequency': 'Immediate',  # Default value
                'notification_delivery': 'Desktop',     # Default value
                'notification_sound': True              # Default value
            }
    
    def save_settings(self):
        with self.lock:
            with open(self.settings_file, 'w') as file:
                json.dump(self.settings, file, indent=4)
    
    def get_notification_frequency(self):
        with self.lock:
            return self.settings.get('notification_frequency', 'Immediate')
    
    def set_notification_frequency(self, frequency):
        with self.lock:
            self.settings['notification_frequency'] = frequency
            self.save_settings()
    
    def get_notification_delivery(self):
        with self.lock:
            return self.settings.get('notification_delivery', 'Desktop')
    
    def set_notification_delivery(self, delivery_method):
        with self.lock:
            self.settings['notification_delivery'] = delivery_method
            self.save_settings()
    
    def get_notification_sound(self):
        with self.lock:
            return self.settings.get('notification_sound', True)
    
    def set_notification_sound(self, sound_enabled):
        with self.lock:
            self.settings['notification_sound'] = sound_enabled
            self.save_settings()

# -------------------------- Main Application --------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.user_manager = UserManager()
        self.flight_tracker = FlightTracker()
        self.notification_manager = NotificationManager()
        self.search_history_manager = SearchHistoryManager()
        self.favorites_manager = FavoritesManager()
        self.current_user_email = None  # Keep track of the logged-in user
        self.api_key = 'GjhePLReGbWdfzVXdZBldBmmKAJ27l7d'       
        self.api_secret = 'ZXYipad3RIsoy1JN' 
        self.access_token = None
        self.token_expiry = None
        self.thread_lock = threading.Lock()
        self.tracked_treeview = None  # For automatic updates of tracked flights window

        # New managers for preferences and settings
        self.user_preferences_manager = UserPreferencesManager()
        self.app_settings_manager = AppSettingsManager()

        # Existing attributes for background thread...
        self.price_check_thread = None
        self.stop_thread = threading.Event()
        self.notified_flights = set()  # To keep track of flights already notified

        self.setup_login_register_view()

    def clear_root_window(self):
        # Remove all widgets from the root window
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_login_register_view(self):
        self.clear_root_window()
        self.root.title("Flight Price Tracker")
        self.root.geometry("300x400")

        tk.Label(self.root, text="Flight Price Tracker", font=("Helvetica", 16)).pack(pady=20)

        tk.Button(self.root, text="Register", width=20, command=self.register).pack(pady=10)
        tk.Button(self.root, text="Login", width=20, command=self.login).pack(pady=10)

    def register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("300x250")

        tk.Label(register_window, text="Username").pack(pady=5)
        entry_username = tk.Entry(register_window)
        entry_username.pack()

        tk.Label(register_window, text="Email").pack(pady=5)
        entry_email = tk.Entry(register_window)
        entry_email.pack()

        tk.Label(register_window, text="Password").pack(pady=5)
        entry_password = tk.Entry(register_window, show="*")
        entry_password.pack()

        def submit_registration():
            username = entry_username.get().strip()
            email = entry_email.get().strip().lower()
            password = entry_password.get().strip()
            if not username or not email or not password:
                messagebox.showerror("Input Error", "All fields are required.")
                return
            message = self.user_manager.register_user(username, email, password)
            messagebox.showinfo("Registration", message)
            if message == "Registration successful.":
                register_window.destroy()

        tk.Button(register_window, text="Register", command=submit_registration).pack(pady=15)

    def login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")
        login_window.geometry("300x200")

        tk.Label(login_window, text="Email").pack(pady=5)
        entry_email = tk.Entry(login_window)
        entry_email.pack()

        tk.Label(login_window, text="Password").pack(pady=5)
        entry_password = tk.Entry(login_window, show="*")
        entry_password.pack()

        def submit_login():
            email = entry_email.get().strip().lower()
            password = entry_password.get().strip()
            if not email or not password:
                messagebox.showerror("Input Error", "Both fields are required.")
                return
            message = self.user_manager.login_user(email, password)
            messagebox.showinfo("Login", message)
            if message == "Login successful.":
                self.current_user_email = email
                login_window.destroy()  # Close the login window
                self.setup_main_application_view()  # Update root window to main application
                self.start_price_check_thread()  # Start the background thread

        tk.Button(login_window, text="Login", command=submit_login).pack(pady=15)

    def show_update_fields(self):
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Profile")
        update_window.geometry("300x250")

        tk.Label(update_window, text="New Username").pack(pady=5)
        entry_new_username = tk.Entry(update_window)
        entry_new_username.pack()

        tk.Label(update_window, text="New Password").pack(pady=5)
        entry_new_password = tk.Entry(update_window, show="*")
        entry_new_password.pack()

        def update_profile():
            new_username = entry_new_username.get().strip()
            new_password = entry_new_password.get().strip()
            if not new_username and not new_password:
                messagebox.showerror("Input Error", "At least one field must be filled.")
                return
            message = self.user_manager.edit_profile(self.current_user_email, new_username, new_password)
            messagebox.showinfo("Profile Update", message)
            if message == "Profile updated successfully.":
                update_window.destroy()
                self.setup_main_application_view()

        tk.Button(update_window, text="Submit", command=update_profile).pack(pady=15)

    def delete_account_action(self):
        if messagebox.askyesno("Delete Account", "Are you sure you want to delete your account? This action cannot be undone."):
            message = self.user_manager.delete_account(self.current_user_email)
            messagebox.showinfo("Delete Account", message)
            self.current_user_email = None
            self.stop_price_check_thread()  # Stop the background thread
            self.setup_login_register_view()

    def sign_out_action(self):
        if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
            messagebox.showinfo("Sign Out", self.user_manager.sign_out())
            self.current_user_email = None
            self.stop_price_check_thread()  # Stop the background thread
            self.setup_login_register_view()

    def search_flights(self):
        if self.current_user_email is None:
            messagebox.showerror("Access Denied", "You must be logged in to search for flights.")
            return

        # Check if the window is already open
        if hasattr(self, 'search_window') and self.search_window.winfo_exists():
            self.search_window.lift()
            return

        self.search_window = tk.Toplevel(self.root)
        self.search_window.title("Flight Search")
        self.search_window.geometry("400x800")

        user_prefs = self.user_preferences_manager.get_user_preferences(self.current_user_email)

        tk.Label(self.search_window, text="Origin (e.g., LAX)").pack(pady=5)
        entry_origin = tk.Entry(self.search_window)
        entry_origin.pack()
        if user_prefs.get('default_origin'):
            entry_origin.insert(0, user_prefs['default_origin'])

        tk.Label(self.search_window, text="Destination (e.g., JFK)").pack(pady=5)
        entry_destination = tk.Entry(self.search_window)
        entry_destination.pack()

        tk.Label(self.search_window, text="Departure Date (YYYY-MM-DD)").pack(pady=5)
        entry_departure_date = tk.Entry(self.search_window)
        entry_departure_date.pack()

        tk.Label(self.search_window, text="Return Date (YYYY-MM-DD) (Optional)").pack(pady=5)
        entry_return_date = tk.Entry(self.search_window)
        entry_return_date.pack()

        tk.Label(self.search_window, text="Number of Passengers").pack(pady=5)
        entry_passengers = tk.Entry(self.search_window)
        entry_passengers.pack()

        tk.Label(self.search_window, text="Preferred Cabin Class (Optional)").pack(pady=5)
        cabin_class_options = ['ANY', 'ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST']
        cabin_class_var = tk.StringVar(value='ANY')
        cabin_class_menu = tk.OptionMenu(self.search_window, cabin_class_var, *cabin_class_options)
        cabin_class_menu.pack()

        # Preferred Airlines
        tk.Label(self.search_window, text="Preferred Airlines (comma-separated codes, e.g., UA,F9) (Optional)").pack(pady=5)
        entry_airlines = tk.Entry(self.search_window, width=50)
        entry_airlines.pack()
        entry_airlines.insert(0, ','.join(user_prefs.get('preferred_airlines', [])))

        # Preferred Layovers
        tk.Label(self.search_window, text="Preferred Number of Layovers (e.g., 0 for non-stop) (Optional)").pack(pady=5)
        entry_layovers = tk.Entry(self.search_window, width=10)
        entry_layovers.pack()
        entry_layovers.insert(0, user_prefs.get('preferred_layovers') if user_prefs.get('preferred_layovers') is not None else '')

        # Currency Selection
        tk.Label(self.search_window, text="Preferred Currency (e.g., USD, EUR) (Optional)").pack(pady=5)
        entry_currency = tk.Entry(self.search_window, width=10)
        entry_currency.pack()
        entry_currency.insert(0, user_prefs.get('currency', 'USD'))

        # Default Origin Airport
        tk.Label(self.search_window, text="Default Origin Airport (e.g., LAX) (Optional)").pack(pady=5)
        entry_default_origin = tk.Entry(self.search_window, width=10)
        entry_default_origin.pack()
        entry_default_origin.insert(0, user_prefs.get('default_origin', ''))

        def is_valid_date(date_str):
            try:
                datetime.datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False

        def submit_flight_search():
            origin = entry_origin.get().strip().upper()
            destination = entry_destination.get().strip().upper()
            departure_date = entry_departure_date.get().strip()
            return_date = entry_return_date.get().strip()
            passengers = entry_passengers.get().strip()
            cabin_class = cabin_class_var.get()
            preferred_airlines = [code.strip().upper() for code in entry_airlines.get().split(',') if code.strip()]
            preferred_layovers = entry_layovers.get().strip()
            preferred_layovers = int(preferred_layovers) if preferred_layovers.isdigit() else None
            preferred_currency = entry_currency.get().strip().upper()
            default_origin = entry_default_origin.get().strip().upper()

            if not origin:
                messagebox.showerror("Input Error", "Origin airport is required.")
                return

            if not destination:
                messagebox.showerror("Input Error", "Destination airport is required.")
                return

            if not passengers.isdigit():
                messagebox.showerror("Input Error", "Number of Passengers must be an integer.")
                return
            passengers = int(passengers)

            if not is_valid_date(departure_date):
                messagebox.showerror("Input Error", "Invalid departure date format. Use YYYY-MM-DD.")
                return

            if return_date and not is_valid_date(return_date):
                messagebox.showerror("Input Error", "Invalid return date format. Use YYYY-MM-DD.")
                return

            search_params = {
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'return_date': return_date,
                'passengers': passengers,
                'cabin_class': cabin_class,
                'preferred_airlines': preferred_airlines,
                'preferred_layovers': preferred_layovers,
                'currency': preferred_currency,
                'default_origin': default_origin
            }

            try:
                flight_data = self.fetch_flight_data(origin, destination, departure_date, return_date, passengers, cabin_class)
                self.search_window.destroy()
                del self.search_window  # Remove the reference
                self.display_flight_results(flight_data)

                # Record search history
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.search_history_manager.add_search_entry(self.current_user_email, search_params, timestamp)

                # Update user preferences with currency and default origin
                user_prefs['currency'] = preferred_currency if preferred_currency else 'USD'
                user_prefs['default_origin'] = default_origin
                self.user_preferences_manager.set_user_preferences(self.current_user_email, user_prefs)

            except Exception as e:
                messagebox.showerror("Flight Search Error", str(e))

        tk.Button(self.search_window, text="Search Flights", command=submit_flight_search).pack(pady=20)

        # Handle the window closing event
        def on_search_window_close():
            self.search_window.destroy()
            del self.search_window  # Remove the reference

        self.search_window.protocol("WM_DELETE_WINDOW", on_search_window_close)

    def fetch_flight_data(self, origin, destination, departure_date, return_date, passengers, cabin_class):
        try:
            self.get_access_token()
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }

            params = {
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date,
                'adults': passengers,
                'currencyCode': 'USD',
                'max': 50
            }

            if return_date:
                params['returnDate'] = return_date

            if cabin_class != 'ANY':
                params['travelClass'] = cabin_class

            # Apply preferred layover filter
            user_prefs = self.user_preferences_manager.get_user_preferences(self.current_user_email)
            preferred_layovers = user_prefs.get('preferred_layovers')
            if preferred_layovers is not None:
                params['max'] = 50  # Ensured max is set appropriately

            # **Incorporate Preferred Airlines**
            preferred_airlines = user_prefs.get('preferred_airlines')
            if preferred_airlines:
                # Join the list into a comma-separated string
                params['includedAirlineCodes'] = ','.join(preferred_airlines)
            
            # **Optional: Add Debugging Statement**
            print(f"Flight Search Parameters: {params}")

            response = requests.get(
                'https://test.api.amadeus.com/v2/shopping/flight-offers',
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            flight_data = response.json()

            if 'data' in flight_data and flight_data['data']:
                # Filter by preferred layovers if set
                if preferred_layovers is not None:
                    flight_data['data'] = [
                        offer for offer in flight_data['data']
                        if len(offer['itineraries'][0]['segments']) - 1 <= preferred_layovers
                    ]
                    if not flight_data['data']:
                        raise Exception("No flights match your layover preferences.")
                return flight_data
            else:
                message = flight_data.get('errors', [{'detail': 'No flights found.'}])[0]['detail']
                raise Exception(message)
        except requests.exceptions.HTTPError as http_err:
            error_details = response.json().get('errors', [{'detail': 'Unknown error'}])[0]['detail']
            raise Exception(f"HTTP error occurred: {error_details}")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

    def get_access_token(self):
        if not self.access_token or time.time() >= self.token_expiry:
            # Obtain an access token
            try:
                auth_response = requests.post(
                    'https://test.api.amadeus.com/v1/security/oauth2/token',
                    data={
                        'grant_type': 'client_credentials',
                        'client_id': self.api_key,
                        'client_secret': self.api_secret
                    },
                    timeout=30
                )
                auth_response.raise_for_status()
                auth_data = auth_response.json()
                self.access_token = auth_data['access_token']
                self.token_expiry = time.time() + int(auth_data['expires_in'])
            except Exception as e:
                raise Exception(f"Failed to obtain access token: {e}")

    def parse_duration(self, duration_str):
        # Convert ISO 8601 duration to minutes
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?')
        match = pattern.match(duration_str)
        hours = int(match.group(1)) if match and match.group(1) else 0
        minutes = int(match.group(2)) if match and match.group(2) else 0
        return hours * 60 + minutes

    def display_flight_results(self, flight_data):
        if hasattr(self, 'results_window') and self.results_window.winfo_exists():
            self.results_window.destroy()
            del self.results_window  # Remove the reference

        preferences = self.user_preferences_manager.get_user_preferences(self.current_user_email)
        preferred_currency = preferences.get('currency', 'USD')

        self.results_window = tk.Toplevel(self.root)
        self.results_window.title("Flight Search Results")
        self.results_window.geometry("1000x600")

        columns = ('Offer ID', 'Price', 'Duration', 'Origin', 'Destination', 'Departure', 'Arrival', 'Airline', 'Layovers', 'Cabin')

        tree = ttk.Treeview(self.results_window, columns=columns, show='headings', selectmode='browse')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.pack(fill=tk.BOTH, expand=True)

        flight_offers = []
        for offer in flight_data['data']:
            offer_id = offer['id']
            price = offer['price']['total']
            currency = offer['price']['currency']
            # Convert price to preferred currency if needed
            if currency != preferred_currency:
                price_converted = self.convert_currency(float(price), currency, preferred_currency)
                price_display = f"{preferred_currency} {price_converted:.2f}"
            else:
                price_display = f"{currency} {price}"
            itineraries = offer['itineraries']
            for itinerary in itineraries:
                duration = itinerary['duration']
                segments = itinerary['segments']
                origin = segments[0]['departure']['iataCode']
                destination = segments[-1]['arrival']['iataCode']
                departure = segments[0]['departure']['at']
                arrival = segments[-1]['arrival']['at']
                airline = segments[0]['carrierCode']
                layovers = len(segments) - 1
                traveler_pricings = offer.get('travelerPricings', [])
                cabin = 'Unknown'
                if traveler_pricings:
                    fare_details = traveler_pricings[0].get('fareDetailsBySegment', [])
                    if fare_details:
                        cabin = fare_details[0].get('cabin')

                tree.insert('', tk.END, values=(offer_id, price_display, duration, origin, destination, departure, arrival, airline, layovers, cabin))
                flight_offers.append(offer)

        # Store flight offers for tracking and favorites
        self.flight_offers = {offer['id']: offer for offer in flight_data['data']}

        def treeview_sort_column(tv, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            if col == 'Price':
                l.sort(key=lambda t: float(t[0].split()[1]) if t[0] else 0, reverse=reverse)
            elif col == 'Duration':
                l.sort(key=lambda t: self.parse_duration(t[0]) if t[0] else 0, reverse=reverse)
            elif col == 'Layovers':
                l.sort(key=lambda t: int(t[0]) if t[0] else 0, reverse=reverse)
            else:
                l.sort(reverse=reverse)
            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)
            tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: treeview_sort_column(tree, c, False))

        # Add Track Flight Button
        def track_selected_flight():
            if self.current_user_email is None:
                messagebox.showerror("Access Denied", "You must be logged in to track flights.")
                return

            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Selection Error", "No flight selected.")
                return
            offer_id = tree.item(selected_item)['values'][0]
            offer_id = str(offer_id)  # Convert offer_id to string
            flight_data = self.flight_offers.get(offer_id)
            if not flight_data:
                messagebox.showerror("Error", "Selected flight data not found.")
                return

            def set_price_threshold():
                threshold = entry_threshold.get().strip()
                try:
                    threshold = float(threshold)
                except ValueError:
                    messagebox.showerror("Input Error", "Please enter a valid price.")
                    return
                message = self.flight_tracker.add_tracked_flight(self.current_user_email, flight_data, threshold)
                messagebox.showinfo("Track Flight", message)
                threshold_window.destroy()

            threshold_window = tk.Toplevel(self.results_window)
            threshold_window.title("Set Price Alert")
            threshold_window.geometry("300x150")
            tk.Label(threshold_window, text="Set Price Threshold").pack(pady=5)
            entry_threshold = tk.Entry(threshold_window)
            entry_threshold.pack(pady=5)
            tk.Button(threshold_window, text="Set Alert", command=set_price_threshold).pack(pady=10)

        # Add Add to Favorites Button
        def add_to_favorites():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Selection Error", "No flight selected.")
                return
            offer_id = tree.item(selected_item)['values'][0]
            offer_id = str(offer_id)  # Convert to string
            flight_data = self.flight_offers.get(offer_id)
            if not flight_data:
                messagebox.showerror("Error", "Selected flight data not found.")
                return
            message = self.favorites_manager.add_favorite(self.current_user_email, flight_data)
            messagebox.showinfo("Favorites", message)

        tk.Button(self.results_window, text="Track Selected Flight", command=track_selected_flight).pack(pady=5)
        tk.Button(self.results_window, text="Add to Favorites", command=add_to_favorites).pack(pady=5)

        # Handle the window closing event
        def on_results_window_close():
            self.results_window.destroy()
            del self.results_window  # Remove the reference

        self.results_window.protocol("WM_DELETE_WINDOW", on_results_window_close)

    def view_tracked_flights(self):
        if self.current_user_email is None:
            messagebox.showerror("Access Denied", "You must be logged in to view tracked flights.")
            return

        # Check if the window is already open
        if hasattr(self, 'tracked_window') and self.tracked_window.winfo_exists():
            # Bring the window to the front
            self.tracked_window.lift()
            return

        self.tracked_window = tk.Toplevel(self.root)
        self.tracked_window.title("Tracked Flights")
        self.tracked_window.geometry("1200x500")

        columns = ('Flight ID', 'Price Threshold', 'Current Price', 'Origin', 'Destination', 'Departure', 'Arrival', 'Cabin', 'Airline', 'Layovers', 'Last Refreshed')

        self.tracked_treeview = ttk.Treeview(self.tracked_window, columns=columns, show='headings')

        for col in columns:
            self.tracked_treeview.heading(col, text=col)
            self.tracked_treeview.column(col, width=100)

        self.tracked_treeview.pack(fill=tk.BOTH, expand=True)

        self.populate_tracked_flights()  # Populate initially

        # Add buttons for refreshing, editing, and removing flights
        def refresh_prices():
            self.get_access_token()
            user_tracked_flights = self.flight_tracker.get_user_tracked_flights(self.current_user_email)
            for flight in user_tracked_flights:
                flight_data = flight['flight_data']
                offer_id = flight['flight_id']

                # Reprice the flight offer
                refreshed_data = self.reprice_flight_offer(flight_data)
                if not refreshed_data:
                    messagebox.showerror("Error", f"Could not refresh price for flight {offer_id}.")
                    continue
                # Update flight data and last refreshed time
                flight['flight_data'] = refreshed_data['data']['flightOffers'][0]
                flight['last_refreshed'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.flight_tracker.save_tracked_flights()
            messagebox.showinfo("Prices Updated", "Flight prices have been refreshed.")
            self.populate_tracked_flights()  # Update the Treeview

        def edit_price_threshold():
            selected_item = self.tracked_treeview.selection()
            if not selected_item:
                messagebox.showerror("Selection Error", "No flight selected.")
                return
            offer_id = self.tracked_treeview.item(selected_item)['values'][0]
            offer_id = str(offer_id)  # Ensure offer_id is a string

            def update_threshold():
                new_threshold = entry_new_threshold.get().strip()
                try:
                    new_threshold = float(new_threshold)
                except ValueError:
                    messagebox.showerror("Input Error", "Please enter a valid price.")
                    return
                message = self.flight_tracker.update_price_threshold(self.current_user_email, offer_id, new_threshold)
                messagebox.showinfo("Update Threshold", message)
                threshold_window.destroy()
                self.populate_tracked_flights()

            threshold_window = tk.Toplevel(self.tracked_window)
            threshold_window.title("Edit Price Threshold")
            threshold_window.geometry("300x100")
            tk.Label(threshold_window, text="New Price Threshold").pack(pady=5)
            entry_new_threshold = tk.Entry(threshold_window)
            entry_new_threshold.pack(pady=5)
            tk.Button(threshold_window, text="Update", command=update_threshold).pack(pady=10)

        def remove_tracked_flight():
            selected_item = self.tracked_treeview.selection()
            if not selected_item:
                messagebox.showerror("Selection Error", "No flight selected.")
                return
            offer_id = self.tracked_treeview.item(selected_item)['values'][0]
            offer_id = str(offer_id)  # Ensure offer_id is a string
            message = self.flight_tracker.remove_tracked_flight(self.current_user_email, offer_id)
            messagebox.showinfo("Remove Flight", message)
            self.populate_tracked_flights()  # Refresh the treeview

        button_frame = tk.Frame(self.tracked_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Refresh Prices", command=refresh_prices).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit Price Threshold", command=edit_price_threshold).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove Flight", command=remove_tracked_flight).pack(side=tk.LEFT, padx=5)

        # Handle the window closing event
        def on_tracked_window_close():
            self.tracked_window.destroy()
            del self.tracked_window  # Remove the reference
            self.tracked_treeview = None  # Reset the Treeview reference

        self.tracked_window.protocol("WM_DELETE_WINDOW", on_tracked_window_close)

    # -------------------------- Preferences Window --------------------------

    def open_preferences_window(self):
        if self.current_user_email is None:
            messagebox.showerror("Access Denied", "You must be logged in to access preferences.")
            return

        preferences_window = tk.Toplevel(self.root)
        preferences_window.title("User Preferences")
        preferences_window.geometry("400x800")
    
        user_prefs = self.user_preferences_manager.get_user_preferences(self.current_user_email)
    
        # Preferred Airlines
        tk.Label(preferences_window, text="Preferred Airlines (comma-separated codes, e.g., UA,F9)").pack(pady=5)
        entry_airlines = tk.Entry(preferences_window, width=50)
        entry_airlines.pack()
        entry_airlines.insert(0, ','.join(user_prefs.get('preferred_airlines', [])))
    
        # Preferred Layovers
        tk.Label(preferences_window, text="Preferred Number of Layovers (e.g., 0 for non-stop)").pack(pady=5)
        entry_layovers = tk.Entry(preferences_window, width=10)
        entry_layovers.pack()
        entry_layovers.insert(0, user_prefs.get('preferred_layovers') if user_prefs.get('preferred_layovers') is not None else '')
    
        # Currency Selection
        tk.Label(preferences_window, text="Preferred Currency (e.g., USD, EUR)").pack(pady=5)
        entry_currency = tk.Entry(preferences_window, width=10)
        entry_currency.pack()
        entry_currency.insert(0, user_prefs.get('currency', 'USD'))
    
        # Default Origin Airport
        tk.Label(preferences_window, text="Default Origin Airport (e.g., LAX)").pack(pady=5)
        entry_default_origin = tk.Entry(preferences_window, width=10)
        entry_default_origin.pack()
        entry_default_origin.insert(0, user_prefs.get('default_origin', ''))
    
        # Save Preferences Button
        def save_preferences():
            preferred_airlines = [code.strip().upper() for code in entry_airlines.get().split(',') if code.strip()]
            preferred_layovers = entry_layovers.get().strip()
            preferred_layovers = int(preferred_layovers) if preferred_layovers.isdigit() else None
            preferred_currency = entry_currency.get().strip().upper()
            default_origin = entry_default_origin.get().strip().upper()
    
            new_preferences = {
                'preferred_airlines': preferred_airlines,
                'preferred_layovers': preferred_layovers,
                # Removed notification settings from User Preferences
                'automatic_updates': user_prefs.get('automatic_updates', True),
                'update_interval': user_prefs.get('update_interval', 1),
                'currency': preferred_currency if preferred_currency else 'USD',
                'default_origin': default_origin
            }
    
            self.user_preferences_manager.set_user_preferences(self.current_user_email, new_preferences)
            messagebox.showinfo("Preferences", "Your preferences have been saved.")
            preferences_window.destroy()

        tk.Button(preferences_window, text="Save Preferences", command=save_preferences).pack(pady=20)

    # -------------------------- Settings Window --------------------------

    def open_settings_window(self):
        if self.current_user_email is None:
            messagebox.showerror("Access Denied", "You must be logged in to access settings.")
            return

        settings_window = tk.Toplevel(self.root)
        settings_window.title("Application Settings")
        settings_window.geometry("400x600")
    
        user_prefs = self.user_preferences_manager.get_user_preferences(self.current_user_email)
    
        # Automatic Price Updates
        var_auto_update = tk.BooleanVar(value=user_prefs.get('automatic_updates', True))
        tk.Checkbutton(settings_window, text="Enable Automatic Price Updates", variable=var_auto_update).pack(pady=5)
    
        # Update Interval
        tk.Label(settings_window, text="Price Check Interval (in minutes)").pack(pady=5)
        entry_interval = tk.Entry(settings_window, width=10)
        entry_interval.pack()
        entry_interval.insert(0, user_prefs.get('update_interval', 60))
    
        # Notification Frequency
        tk.Label(settings_window, text="Notification Frequency").pack(pady=5)
        freq_options = ['Immediate', 'Daily', 'Weekly']
        current_freq = self.app_settings_manager.get_notification_frequency()
        var_frequency = tk.StringVar(value=current_freq)
        freq_menu = tk.OptionMenu(settings_window, var_frequency, *freq_options)
        freq_menu.pack()
    
        # Notification Delivery Method
        tk.Label(settings_window, text="Notification Delivery Method").pack(pady=5)
        delivery_options = ['Desktop', 'In-App']
        current_delivery = self.app_settings_manager.get_notification_delivery()
        var_delivery = tk.StringVar(value=current_delivery)
        delivery_menu = tk.OptionMenu(settings_window, var_delivery, *delivery_options)
        delivery_menu.pack()
    
        # Enable Notification Sound
        var_sound = tk.BooleanVar(value=self.app_settings_manager.get_notification_sound())
        tk.Checkbutton(settings_window, text="Enable Notification Sound", variable=var_sound).pack(pady=5)
    
        # Save Settings Button
        def save_settings():
            automatic_updates = var_auto_update.get()
            update_interval = entry_interval.get().strip()
            update_interval = int(update_interval) if update_interval.isdigit() else 60
            frequency = var_frequency.get()
            delivery_method = var_delivery.get()
            notification_sound = var_sound.get()
    
            # Update user preferences
            user_prefs['automatic_updates'] = automatic_updates
            user_prefs['update_interval'] = update_interval
            # Currency and default_origin are managed in User Preferences
    
            self.user_preferences_manager.set_user_preferences(self.current_user_email, user_prefs)
    
            # Update application settings
            self.app_settings_manager.set_notification_frequency(frequency)
            self.app_settings_manager.set_notification_delivery(delivery_method)
            self.app_settings_manager.set_notification_sound(notification_sound)
    
            messagebox.showinfo("Settings", "Your settings have been saved.")
            settings_window.destroy()

        tk.Button(settings_window, text="Save Settings", command=save_settings).pack(pady=20)

    # -------------------------- Currency Conversion --------------------------

    def convert_currency(self, amount, from_currency, to_currency):
        # Simple currency conversion using a free API
        try:
            api_key = 'bb27625af0acb11f8b20537d'  # Replace with your exchange rate API key
            url = f'https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['result'] == 'success':
                return data['conversion_result']
            else:
                return amount  # Fallback to original amount if conversion fails
        except Exception as e:
            print(f"Currency conversion error: {e}")
            return amount  # Fallback to original amount if any error occurs

    # -------------------------- Populate Tracked Flights --------------------------

    def populate_tracked_flights(self):
        if not hasattr(self, 'tracked_treeview') or self.tracked_treeview is None:
            return  # If the Treeview doesn't exist, do nothing

        # Fetch the latest tracked flights
        user_tracked_flights = self.flight_tracker.get_user_tracked_flights(self.current_user_email)
        # Clear existing entries
        for item in self.tracked_treeview.get_children():
            self.tracked_treeview.delete(item)
        for flight in user_tracked_flights:
            flight_data = flight['flight_data']
            offer_id = flight['flight_id']
            price_threshold = flight['price_threshold']
            current_price = flight_data['price']['total']
            itineraries = flight_data['itineraries']
            origin = itineraries[0]['segments'][0]['departure']['iataCode']
            destination = itineraries[0]['segments'][-1]['arrival']['iataCode']
            departure = itineraries[0]['segments'][0]['departure']['at']
            arrival = itineraries[0]['segments'][-1]['arrival']['at']
            traveler_pricings = flight_data.get('travelerPricings', [])
            cabin = 'Unknown'
            if traveler_pricings:
                fare_details = traveler_pricings[0].get('fareDetailsBySegment', [])
                if fare_details:
                    cabin = fare_details[0].get('cabin')
            airline = itineraries[0]['segments'][0]['carrierCode']
            layovers = len(itineraries[0]['segments']) - 1
            last_refreshed = flight.get('last_refreshed', 'N/A')

            self.tracked_treeview.insert('', tk.END, values=(
                offer_id, price_threshold, current_price, origin, destination, departure, arrival, cabin, airline, layovers, last_refreshed
            ))

    # -------------------------- Flight Price Check Thread --------------------------

    def start_price_check_thread(self):
        if self.price_check_thread is None or not self.price_check_thread.is_alive():
            self.stop_thread.clear()
            self.price_check_thread = threading.Thread(target=self.check_prices_periodically, daemon=True)
            self.price_check_thread.start()

    def stop_price_check_thread(self):
        self.stop_thread.set()
        if self.price_check_thread is not None:
            self.price_check_thread.join()

    def check_prices_periodically(self):
        while not self.stop_thread.is_set():
            self.refresh_tracked_flights_prices()
            # Fetch update_interval from User Preferences
            user_prefs = self.user_preferences_manager.get_user_preferences(self.current_user_email)
            update_interval = user_prefs.get('update_interval', 1)  # In minutes

            # Sleep for the specified interval, checking every second if stop is set
            for _ in range(update_interval * 60):
                if self.stop_thread.is_set():
                    break
                time.sleep(1)

    def refresh_tracked_flights_prices(self):
        # Ensure we have a valid access token
        self.get_access_token()
        user_tracked_flights = self.flight_tracker.get_user_tracked_flights(self.current_user_email)
        user_prefs = self.user_preferences_manager.get_user_preferences(self.current_user_email)
        automatic_updates = user_prefs.get('automatic_updates', True)
        update_interval = user_prefs.get('update_interval', 1)  # In minutes

        if not automatic_updates:
            return  # Do not perform updates if disabled

        # Fetch notification settings from Application Settings
        notification_frequency = self.app_settings_manager.get_notification_frequency()
        notification_delivery = self.app_settings_manager.get_notification_delivery()
        notification_sound = self.app_settings_manager.get_notification_sound()

        for flight in user_tracked_flights:
            flight_data = flight['flight_data']
            offer_id = flight['flight_id']

            # Reprice the flight offer
            refreshed_data = self.reprice_flight_offer(flight_data)
            if not refreshed_data:
                print(f"Could not refresh price for flight {offer_id}.")
                continue
            # Update flight data and last refreshed time
            flight['flight_data'] = refreshed_data['data']['flightOffers'][0]
            flight['last_refreshed'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.flight_tracker.save_tracked_flights()

            # Extract Origin and Destination
            itineraries = flight['flight_data']['itineraries']
            origin = itineraries[0]['segments'][0]['departure']['iataCode']
            destination = itineraries[0]['segments'][-1]['arrival']['iataCode']

            # Check if price has dropped below the threshold
            current_price = float(flight['flight_data']['price']['total'])
            price_threshold = float(flight['price_threshold'])
            if current_price <= price_threshold:
                # Only notify once per price drop
                if offer_id not in self.notified_flights:
                    # Determine notification delivery method
                    delivery_method = notification_delivery
                    message = f"The price for flight {offer_id} from {origin} to {destination} has dropped to {user_prefs.get('currency', 'USD')} {current_price:.2f}, which is below your threshold of {user_prefs.get('currency', 'USD')} {price_threshold:.2f}."
                    
                    if delivery_method == 'Desktop':
                        self.root.after(0, lambda msg=message: messagebox.showinfo("Price Alert", msg))
                    elif delivery_method == 'In-App':
                        # Implement in-app notification (e.g., update a label or a dedicated notification area)
                        # For simplicity, we'll use a messagebox here as a placeholder
                        self.root.after(0, lambda msg=message: messagebox.showinfo("Price Alert", msg))

                    if notification_sound:
                        # Play a notification sound
                        # Placeholder: You can integrate actual sound playback using winsound or other libraries
                        print("Notification Sound Played")

                    self.notified_flights.add(offer_id)

                    # Log the notification with origin and destination
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.notification_manager.add_notification(self.current_user_email, message, timestamp, origin, destination)
            else:
                # Remove from notified flights if price is above threshold
                if offer_id in self.notified_flights:
                    self.notified_flights.remove(offer_id)

        # Update the tracked flights window if it's open
        self.root.after(0, self.populate_tracked_flights)

    def reprice_flight_offer(self, flight_data):
        try:
            self.get_access_token()

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            # Properly structure the request payload
            request_body = {
                "data": {
                    "type": "flight-offers-pricing",
                    "flightOffers": [flight_data]
                }
            }

            response = requests.post(
                'https://test.api.amadeus.com/v1/shopping/flight-offers/pricing',
                headers=headers,
                json=request_body,
                timeout=30  # Set a timeout for the request
            )
            response.raise_for_status()
            priced_offer = response.json()
            return priced_offer
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            try:
                error_details = response.json()
                print("Error details:", json.dumps(error_details, indent=2))
            except json.JSONDecodeError:
                print("Response content:", response.text)
            return None
        except requests.exceptions.Timeout:
            print("Timeout error when re-pricing flight offer.")
            return None
        except Exception as e:
            print("Error re-pricing flight offer:", e)
            return None

    # -------------------------- Notification History --------------------------

    def view_notification_history(self):
        notifications = self.notification_manager.get_user_notifications(self.current_user_email)
        if not notifications:
            messagebox.showinfo("Notification History", "No notifications received yet.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("Notification History")
        history_window.geometry("900x500")

        columns = ('Timestamp', 'Origin', 'Destination', 'Message')

        tree = ttk.Treeview(history_window, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        tree.pack(fill=tk.BOTH, expand=True)

        for notification in notifications:
            timestamp = notification['timestamp']
            origin = notification.get('origin', 'N/A')
            destination = notification.get('destination', 'N/A')
            message = notification['message']
            tree.insert('', tk.END, values=(timestamp, origin, destination, message))

    # -------------------------- Search History Management --------------------------

    def view_search_history(self):
        history = self.search_history_manager.get_user_search_history(self.current_user_email)
        if not history:
            messagebox.showinfo("Search History", "No search history found.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("Search History")
        history_window.geometry("1000x500")

        columns = ('Timestamp', 'Origin', 'Destination', 'Departure Date', 'Return Date', 'Passengers', 'Cabin Class')

        tree = ttk.Treeview(history_window, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.pack(fill=tk.BOTH, expand=True)

        for entry in history:
            timestamp = entry['timestamp']
            params = entry['search_params']
            tree.insert('', tk.END, values=(
                timestamp,
                params.get('origin', 'N/A'),
                params.get('destination', 'N/A'),
                params.get('departure_date', 'N/A'),
                params.get('return_date', 'N/A') if params.get('return_date') else 'N/A',
                params.get('passengers', 'N/A'),
                params.get('cabin_class', 'N/A')
            ))

        def repeat_search():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Selection Error", "No search selected.")
                return
            item = tree.item(selected_item)
            values = item['values']
            params = {
                'origin': values[1],
                'destination': values[2],
                'departure_date': values[3],
                'return_date': values[4],
                'passengers': values[5],
                'cabin_class': values[6]
            }
            try:
                flight_data = self.fetch_flight_data(**params)
                history_window.destroy()
                self.display_flight_results(flight_data)

                # Record search history again
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.search_history_manager.add_search_entry(self.current_user_email, params, timestamp)

            except Exception as e:
                messagebox.showerror("Error", str(e))

        def clear_search_history():
            if messagebox.askyesno("Clear Search History", "Are you sure you want to clear your search history?"):
                self.search_history_manager.clear_user_search_history(self.current_user_email)
                messagebox.showinfo("Search History", "Your search history has been cleared.")
                history_window.destroy()

        button_frame = tk.Frame(history_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Repeat Search", command=repeat_search).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Search History", command=clear_search_history).pack(side=tk.LEFT, padx=5)

    # -------------------------- Favorites Management --------------------------

    def view_favorites(self):
        favorites = self.favorites_manager.get_user_favorites(self.current_user_email)
        if not favorites:
            messagebox.showinfo("Favorites", "No favorite flights found.")
            return

        favorites_window = tk.Toplevel(self.root)
        favorites_window.title("Favorite Flights")
        favorites_window.geometry("1000x500")

        columns = ('Flight ID', 'Price', 'Origin', 'Destination', 'Departure', 'Arrival', 'Airline', 'Layovers', 'Cabin')

        tree = ttk.Treeview(favorites_window, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.pack(fill=tk.BOTH, expand=True)

        for fav in favorites:
            flight_data = fav['flight_data']
            offer_id = fav['flight_id']
            price = flight_data['price']['total']
            itineraries = flight_data['itineraries']
            origin = itineraries[0]['segments'][0]['departure']['iataCode']
            destination = itineraries[0]['segments'][-1]['arrival']['iataCode']
            departure = itineraries[0]['segments'][0]['departure']['at']
            arrival = itineraries[0]['segments'][-1]['arrival']['at']
            airline = itineraries[0]['segments'][0]['carrierCode']
            layovers = len(itineraries[0]['segments']) - 1
            cabin = flight_data.get('travelerPricings', [{}])[0].get('fareDetailsBySegment', [{}])[0].get('cabin', 'Unknown')

            tree.insert('', tk.END, values=(
                offer_id, price, origin, destination, departure, arrival, airline, layovers, cabin
            ))

        def remove_favorite():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Selection Error", "No flight selected.")
                return
            offer_id = tree.item(selected_item)['values'][0]
            offer_id = str(offer_id)  # Ensure offer_id is a string
            message = self.favorites_manager.remove_favorite(self.current_user_email, offer_id)
            messagebox.showinfo("Favorites", message)
            favorites_window.destroy()
            self.view_favorites()  # Refresh the favorites window

        tk.Button(favorites_window, text="Remove from Favorites", command=remove_favorite).pack(pady=10)

    # -------------------------- Main Application View --------------------------

    def setup_main_application_view(self):
        self.clear_root_window()
        self.root.title("User Profile")
        self.root.geometry("300x800")

        # Display user profile information
        profile_info = self.user_manager.view_profile(self.current_user_email)
        tk.Label(self.root, text=profile_info, font=("Helvetica", 12)).pack(pady=10)

        # Update Profile
        tk.Button(self.root, text="Update Profile", command=self.show_update_fields).pack(pady=5)

        # Delete Account
        tk.Button(self.root, text="Delete Account", command=self.delete_account_action).pack(pady=5)

        # Sign Out
        tk.Button(self.root, text="Sign Out", command=self.sign_out_action).pack(pady=5)

        # Search Flights
        tk.Button(self.root, text="Search Flights", command=self.search_flights).pack(pady=20)

        # View Tracked Flights
        tk.Button(self.root, text="View Tracked Flights", command=self.view_tracked_flights).pack(pady=5)

        # View Notification History
        tk.Button(self.root, text="View Notification History", command=self.view_notification_history).pack(pady=5)

        # View Search History
        tk.Button(self.root, text="View Search History", command=self.view_search_history).pack(pady=5)

        # View Favorites
        tk.Button(self.root, text="View Favorites", command=self.view_favorites).pack(pady=5)

        # User Preferences
        tk.Button(self.root, text="User Preferences", command=self.open_preferences_window).pack(pady=20)

        # Application Settings
        tk.Button(self.root, text="Application Settings", command=self.open_settings_window).pack(pady=5)

    # -------------------------- Final Setup --------------------------

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
