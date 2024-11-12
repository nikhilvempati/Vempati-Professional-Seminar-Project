import tkinter as tk
from tkinter import messagebox

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password  # In a real application, use password hashing

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

class App:
    def __init__(self, root):
        self.root = root
        self.user_manager = UserManager()
        self.current_user_email = None  # Keep track of the logged-in user
        self.setup_main_window()
    
    def setup_main_window(self):
        self.root.title("User Management")
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
            message = self.user_manager.login_user(email, password)
            messagebox.showinfo("Login", message)
            if message == "Login successful.":
                self.current_user_email = email
                login_window.destroy()
                self.user_profile()
    
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")
    
        tk.Label(login_window, text="Email").pack()
        entry_email = tk.Entry(login_window)
        entry_email.pack()
    
        tk.Label(login_window, text="Password").pack()
        entry_password = tk.Entry(login_window, show="*")
        entry_password.pack()
    
        tk.Button(login_window, text="Login", command=submit_login).pack()
    
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
    
        tk.Button(profile_window, text="Delete Account", command=delete_account_action).pack()
    
        # Sign Out
        def sign_out_action():
            messagebox.showinfo("Sign Out", self.user_manager.sign_out())
            profile_window.destroy()
            self.current_user_email = None
    
        tk.Button(profile_window, text="Sign Out", command=sign_out_action).pack()

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
