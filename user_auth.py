
def register_user(username, email, password):
    with open('users.txt', 'a+') as file:
        file.seek(0)
        for line in file:
            if email in line:
                return "Email already registered."
        file.write(f"{username},{email},{password}\n")
    return "Registration successful."

def login_user(email, password):
    with open('users.txt', 'r') as file:
        for line in file:
            username, stored_email, stored_password_hash = line.strip().split(',')
            if stored_email == email:
                if password == stored_password_hash:
                    return "Login successful."
                else:
                    return "Incorrect password."
    return "Email not registered."

def sign_out():
    # Clear session or token
    return "Signed out successfully."

def reset_password(email, new_password):
    lines = []
    with open('users.txt', 'r') as file:
        lines = file.readlines()
    with open('users.txt', 'w') as file:
        for line in lines:
            username, stored_email, stored_password_hash = line.strip().split(',')
            if stored_email == email:
                file.write(f"{username},{email},{new_password}\n")
            else:
                file.write(line)
    return "Password reset successful."

def view_profile(email):
    with open('users.txt', 'r') as file:
        for line in file:
            username, stored_email, _ = line.strip().split(',')
            if stored_email == email:
                return f"Username: {username}, Email: {stored_email}"
    return "User not found."

def edit_profile(email, new_username=None, new_password=None):
    lines = []
    with open('users.txt', 'r') as file:
        lines = file.readlines()
    with open('users.txt', 'w') as file:
        for line in lines:
            username, stored_email, stored_password_hash = line.strip().split(',')
            if stored_email == email:
                if new_username:
                    username = new_username
                if new_password:
                    stored_password_hash = new_password
                file.write(f"{username},{email},{stored_password_hash}\n")
            else:
                file.write(line)
    return "Profile updated successfully."

def delete_account(email):
    lines = []
    with open('users.txt', 'r') as file:
        lines = file.readlines()
    with open('users.txt', 'w') as file:
        for line in lines:
            _, stored_email, _ = line.strip().split(',')
            if stored_email != email:
                file.write(line)
    return "Account deleted successfully."
import tkinter as tk
from tkinter import messagebox
from tkinter import messagebox
import tkinter as tk
from tkinter import messagebox

def register():
    def submit_registration():
        username = entry_username.get()
        email = entry_email.get()
        password = entry_password.get()
        message = register_user(username, email, password)
        messagebox.showinfo("Registration", message)

    register_window = tk.Toplevel()
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

def login():
    def submit_login():
        email = entry_email.get()
        password = entry_password.get()
        message = login_user(email, password)
        messagebox.showinfo("Login", message)
        login_window.destroy()
        user_profile(email)

    login_window = tk.Toplevel()
    login_window.title("Login")

    tk.Label(login_window, text="Email").pack()
    entry_email = tk.Entry(login_window)
    entry_email.pack()

    tk.Label(login_window, text="Password").pack()
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack()

    tk.Button(login_window, text="Login", command=submit_login).pack()

def user_profile(email):
    profile_window = tk.Toplevel()
    profile_window.title("User Profile")

    # Display user profile information
    profile_info = view_profile(email)
    tk.Label(profile_window, text=profile_info).pack()

    # Button to show update profile fields
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
            message = edit_profile(email, new_username, new_password)
            messagebox.showinfo("Profile Update", message)
            update_window.destroy()

        tk.Button(update_window, text="Submit", command=update_profile).pack()

    tk.Button(profile_window, text="Update Profile", command=show_update_fields).pack()

    # Delete account section
    def delete_account_action():
        if messagebox.askyesno("Delete Account", "Are you sure you want to delete your account?"):
            message = delete_account(email)
            messagebox.showinfo("Delete Account", message)
            profile_window.destroy()

    tk.Button(profile_window, text="Delete Account", command=delete_account_action).pack()

    # Sign out section
    def sign_out_action():
        messagebox.showinfo("Sign Out", sign_out())
        profile_window.destroy()

    tk.Button(profile_window, text="Sign Out", command=sign_out_action).pack()


def main():
    root = tk.Tk()
    root.title("User Management")
    root.geometry("300x400")

    tk.Button(root, text="Register", command=register).pack(pady=10)
    tk.Button(root, text="Login", command=login).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
