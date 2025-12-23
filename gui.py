import customtkinter as ctk
from tkinter import messagebox
import requests

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

SERVER_URL = "http://localhost:8080"

class CoffeeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Coffee Machine")
        self.geometry("400x700")
        self.resizable(False, False)

        self.COLOR_ACCENT = "#6F4E37"
        self.COLOR_HOVER = "#4A3B32"
        self.COLOR_DANGER = "#C0392B"
        self.COLOR_GRAY = "#333333"

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(30, 10))
        
        self.label_title = ctk.CTkLabel(self.header_frame, text="Smart Barista", 
                                      font=("Roboto", 28, "bold"))
        self.label_title.pack()

        self.label_subtitle = ctk.CTkLabel(self.header_frame, text="Automated Brewing System", 
                                      font=("Roboto", 12), text_color="gray")
        self.label_subtitle.pack()

        self.status_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=15, border_width=1, border_color="#444")
        self.status_frame.pack(pady=15, padx=20, fill="x")

        self.label_status_header = ctk.CTkLabel(self.status_frame, text="SYSTEM STATUS", 
                                              font=("Arial", 10, "bold"), text_color="#666")
        self.label_status_header.pack(pady=(10, 0), anchor="w", padx=15)

        self.label_status = ctk.CTkLabel(self.status_frame, text="Connecting to server...", 
                                       font=("Consolas", 14), justify="left", text_color="#d1d1d1")
        self.label_status.pack(pady=10, padx=15, anchor="w")

        self.sugar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sugar_frame.pack(pady=10)
        
        self.label_sugar = ctk.CTkLabel(self.sugar_frame, text="Sugar: 1 spoon", font=("Roboto", 14))
        self.label_sugar.pack()
        
        self.sugar_slider = ctk.CTkSlider(self.sugar_frame, from_=0, to=5, number_of_steps=5, 
                                        width=250, button_color=self.COLOR_ACCENT, progress_color=self.COLOR_ACCENT,
                                        command=self.update_sugar_label)
        self.sugar_slider.set(1)
        self.sugar_slider.pack(pady=5)

        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.pack(pady=10, fill="x", padx=40)

        self.create_coffee_btn("Espresso (30ml)", "espresso").pack(pady=8, fill="x")
        self.create_coffee_btn("Cappuccino (150ml)", "cappuccino").pack(pady=8, fill="x")
        self.create_coffee_btn("Latte (200ml)", "latte").pack(pady=8, fill="x")

        self.service_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.service_frame.pack(side="bottom", pady=40)

        ctk.CTkButton(self.service_frame, text="Refill Resources", width=140, height=40,
                      fg_color=self.COLOR_GRAY, hover_color="#444", 
                      font=("Roboto", 12, "bold"),
                      command=self.refill).pack(side="left", padx=10)
        
        ctk.CTkButton(self.service_frame, text="Clean Machine", width=140, height=40,
                      fg_color=self.COLOR_GRAY, hover_color="#444", 
                      font=("Roboto", 12, "bold"),
                      command=self.clean).pack(side="left", padx=10)

        self.update_loop()

    def create_coffee_btn(self, text, type_code):
        return ctk.CTkButton(self.menu_frame, text=text, height=50, corner_radius=10,
                             font=("Roboto", 16, "bold"),
                             fg_color=self.COLOR_ACCENT, hover_color=self.COLOR_HOVER,
                             command=lambda: self.order(type_code))

    def update_sugar_label(self, value):
        spoons = int(value)
        self.label_sugar.configure(text=f"Sugar: {spoons} spoon(s)")

    def update_loop(self):
        self.update_status()
        self.after(2000, self.update_loop)

    def update_status(self):
        try:
            response = requests.get(f"{SERVER_URL}/status", timeout=0.5)
            if response.status_code == 200:
                data = response.json()
                
                text = (f"Water:  {data['water']} ml\n"
                        f"Beans:  {data['coffee']} g\n"
                        f"Milk:   {data['milk']} ml\n"
                        f"Sugar:  {data['sugar']} g\n"
                        f"Cups:   {data['cups']} / {data['max_cups']}")
                
                self.label_status.configure(text=text, text_color="#d1d1d1")

                if data['is_blocked']:
                    self.label_status.configure(text=text + "\n\nMAINTENANCE REQUIRED!", text_color=self.COLOR_DANGER)
            else:
                self.label_status.configure(text="Server Error (500)", text_color=self.COLOR_DANGER)
        except:
            self.label_status.configure(text="Offline\nEnsure ./coffee_server is running", text_color=self.COLOR_DANGER)

    def order(self, coffee_type):
        sugar = int(self.sugar_slider.get())
        payload = {"type": coffee_type, "sugar": sugar}
        try:
            response = requests.post(f"{SERVER_URL}/make", json=payload)
            data = response.json()
            if data.get("status") == "success":
                messagebox.showinfo("Success", data["message"])
            else:
                messagebox.showwarning("Warning", data.get("message", "Error"))
            self.update_status()
        except:
            messagebox.showerror("Network Error", "Could not connect to server")

    def refill(self):
        try: requests.post(f"{SERVER_URL}/refill") 
        except: pass
        self.update_status()

    def clean(self):
        try: requests.post(f"{SERVER_URL}/clean") 
        except: pass
        self.update_status()

if __name__ == "__main__":
    app = CoffeeApp()
    app.mainloop()