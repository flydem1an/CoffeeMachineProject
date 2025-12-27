import customtkinter as ctk
from tkinter import messagebox
import requests
import time
import threading
import json
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
SERVER_URL = "http://localhost:8080"
PRESETS_FILE = "user_presets.json"

class CoffeeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Barista: Queue & Builder")
        self.geometry("950x700")
        self.resizable(False, False)

        self.order_queue = [] 
        self.is_processing = False 
        self.custom_presets = self.load_presets() 

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(self.left_frame, text="☕ Order Panel", font=("Roboto", 24, "bold")).pack(pady=(0, 15))

        self.sugar_frame = ctk.CTkFrame(self.left_frame)
        self.sugar_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        self.label_sugar = ctk.CTkLabel(self.sugar_frame, text="Sugar: 1 spoon 🍬")
        self.label_sugar.pack(pady=(5,0))
        
        self.sugar_slider = ctk.CTkSlider(self.sugar_frame, from_=0, to=5, number_of_steps=5, command=self.update_sugar)
        self.sugar_slider.set(1)
        self.sugar_slider.pack(pady=10, fill="x", padx=10)

        self.mode_tabs = ctk.CTkTabview(self.left_frame, width=400)
        self.mode_tabs.pack(side="top", fill="both", expand=True)
        
        self.tab_menu = self.mode_tabs.add(" Standard Menu ")
        self.tab_custom = self.mode_tabs.add(" Custom Builder ")

        self.setup_standard_menu()
        self.setup_custom_builder()

        self.right_frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(self.right_frame, text="📋 Order Queue", font=("Roboto", 20, "bold")).pack(pady=20)
        
        self.queue_box = ctk.CTkTextbox(self.right_frame, font=("Consolas", 14))
        self.queue_box.pack(padx=20, fill="both", expand=True)
        self.queue_box.insert("0.0", "Queue is empty.\n")
        self.queue_box.configure(state="disabled")

        self.right_bottom_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.right_bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        ctk.CTkLabel(self.right_bottom_frame, text="Machine Status:", anchor="w").pack(fill="x")
        self.status_label = ctk.CTkLabel(self.right_bottom_frame, text="IDLE", font=("Roboto", 16, "bold"), text_color="gray")
        self.status_label.pack(pady=5)
        
        self.progressbar = ctk.CTkProgressBar(self.right_bottom_frame, orientation="horizontal", mode="determinate")
        self.progressbar.pack(fill="x", pady=5)
        self.progressbar.set(0)

        self.res_label = ctk.CTkLabel(self.right_bottom_frame, text="Loading...", font=("Consolas", 12), justify="left")
        self.res_label.pack(pady=10, anchor="w")

        self.service_frame = ctk.CTkFrame(self.right_bottom_frame, fg_color="transparent")
        self.service_frame.pack(fill="x", pady=(10, 0))
        
        self.service_frame.grid_columnconfigure(0, weight=1)
        self.service_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(self.service_frame, text="Refill", command=self.refill, fg_color="#555").grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(self.service_frame, text="Clean", command=self.clean, fg_color="#555").grid(row=0, column=1, padx=5, sticky="ew")

        self.update_status_loop()


    def setup_standard_menu(self):
        self.menu_scroll = ctk.CTkScrollableFrame(self.tab_menu, fg_color="transparent")
        self.menu_scroll.pack(fill="both", expand=True)

        self.btn_conf = {"height": 50, "font": ("Roboto", 15, "bold"), "fg_color": "#6F4E37", "hover_color": "#4A3B32"}
        
        ctk.CTkLabel(self.menu_scroll, text="--- STANDARD MENU ---", text_color="gray", font=("Arial", 10, "bold")).pack(pady=(5, 10))

        ctk.CTkButton(self.menu_scroll, text="Espresso (30ml) - 30₴", command=lambda: self.add_to_queue("espresso"), **self.btn_conf).pack(pady=5, fill="x")
        ctk.CTkButton(self.menu_scroll, text="Americano (150ml) - 35₴", command=lambda: self.add_to_queue("americano"), **self.btn_conf).pack(pady=5, fill="x")
        ctk.CTkButton(self.menu_scroll, text="Cappuccino (150ml) - 45₴", command=lambda: self.add_to_queue("cappuccino"), **self.btn_conf).pack(pady=5, fill="x")
        ctk.CTkButton(self.menu_scroll, text="Latte (200ml) - 50₴", command=lambda: self.add_to_queue("latte"), **self.btn_conf).pack(pady=5, fill="x")
        ctk.CTkButton(self.menu_scroll, text="Raf Coffee (230ml) - 55₴", command=lambda: self.add_to_queue("raf"), **self.btn_conf).pack(pady=5, fill="x")

        self.preset_separator = ctk.CTkLabel(self.menu_scroll, text="--- MY PRESETS ---", text_color="gray", font=("Arial", 10, "bold"))
        self.preset_separator.pack(pady=(20, 5))

        self.presets_container = ctk.CTkFrame(self.menu_scroll, fg_color="transparent")
        self.presets_container.pack(fill="x")

        for preset in self.custom_presets:
            self.create_preset_button(preset)

    def setup_custom_builder(self):
        ctk.CTkLabel(self.tab_custom, text="Recipe Name:", anchor="w").pack(pady=(10, 0), padx=10, fill="x")
        self.entry_name = ctk.CTkEntry(self.tab_custom, placeholder_text="e.g. Morning Bomb")
        self.entry_name.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.tab_custom, text="Ingredients (60₴):", font=("Roboto", 14)).pack(pady=10)
        
        self.c_water = self.create_slider("Water (ml)", 20, 300, 100)
        self.c_coffee = self.create_slider("Coffee (g)", 5, 30, 15)
        self.c_milk = self.create_slider("Milk (ml)", 0, 300, 50)

        btn_frame = ctk.CTkFrame(self.tab_custom, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x")

        ctk.CTkButton(btn_frame, text="ADD TO QUEUE ➤", fg_color="#27AE60", hover_color="#1E8449", width=140,
                      command=lambda: self.add_custom_to_queue(save=False)).pack(side="left", padx=10, expand=True)

        ctk.CTkButton(btn_frame, text="SAVE PRESET 💾", fg_color="#2980B9", hover_color="#1A5276", width=140,
                      command=self.save_preset).pack(side="right", padx=10, expand=True)

    def create_slider(self, text, min_v, max_v, def_v):
        frame = ctk.CTkFrame(self.tab_custom, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        label = ctk.CTkLabel(frame, text=f"{text}: {def_v}")
        label.pack(anchor="w")
        slider = ctk.CTkSlider(frame, from_=min_v, to=max_v, number_of_steps=(max_v-min_v)/5)
        slider.set(def_v)
        slider.configure(command=lambda v: label.configure(text=f"{text}: {int(v)}"))
        slider.pack(fill="x")
        return slider

    def create_preset_button(self, preset_data):
        """Створює рядок з кнопкою замовлення І кнопкою видалення"""
        name = preset_data["name"]
        
        row_frame = ctk.CTkFrame(self.presets_container, fg_color="transparent")
        row_frame.pack(pady=5, fill="x")

        ctk.CTkButton(row_frame, 
                      text=f"{name} - 60₴", 
                      fg_color="#5B2C6F", hover_color="#4A235A",
                      height=50, font=("Roboto", 15, "bold"),
                      command=lambda: self.add_to_queue("custom", preset_data)
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(row_frame,
                      text="❌",
                      width=40, height=50,
                      fg_color="#C0392B", hover_color="#922B21",
                      font=("Arial", 14),
                      command=lambda: self.delete_preset(name, row_frame)
        ).pack(side="right")


    def load_presets(self):
        if os.path.exists(PRESETS_FILE):
            try:
                with open(PRESETS_FILE, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_presets_to_file(self):
        try:
            with open(PRESETS_FILE, "w") as f:
                json.dump(self.custom_presets, f, indent=4)
        except Exception as e:
            print(f"Error saving presets: {e}")

    def delete_preset(self, name_to_delete, widget_frame):
        """Видаляє рецепт зі списку і з екрану"""
        self.custom_presets = [p for p in self.custom_presets if p["name"] != name_to_delete]
        
        self.save_presets_to_file()
        
        widget_frame.destroy()
        
    def update_sugar(self, val):
        self.label_sugar.configure(text=f"Sugar: {int(val)} spoon 🍬")

    def save_preset(self):
        name = self.entry_name.get()
        if not name:
            messagebox.showwarning("Info", "Please enter a recipe name!")
            return

        for p in self.custom_presets:
            if p["name"] == name:
                messagebox.showerror("Error", "Name already exists! Choose another.")
                return

        preset_data = {
            "name": name,
            "water": int(self.c_water.get()),
            "coffee": int(self.c_coffee.get()),
            "milk": int(self.c_milk.get())
        }
        
        self.custom_presets.append(preset_data)
        self.save_presets_to_file()
        self.create_preset_button(preset_data)

        messagebox.showinfo("Saved", f"Recipe '{name}' saved permanently!")
        self.entry_name.delete(0, "end")

    def add_to_queue(self, type_code, custom_data=None):
        sugar = int(self.sugar_slider.get())
        
        display_name = type_code.title()
        if custom_data and "name" in custom_data:
            display_name = custom_data["name"]
        elif type_code == "custom":
            display_name = "Custom Mix"

        order = {
            "type": type_code, 
            "sugar": sugar,
            "display": display_name
        }
        if custom_data:
            order.update(custom_data)
            
        self.order_queue.append(order)
        self.refresh_queue_display()
        
        if not self.is_processing:
            threading.Thread(target=self.process_queue).start()

    def add_custom_to_queue(self, save=False):
        data = {
            "name": "Custom Mix",
            "water": int(self.c_water.get()),
            "coffee": int(self.c_coffee.get()),
            "milk": int(self.c_milk.get())
        }
        self.add_to_queue("custom", data)

    def refresh_queue_display(self):
        self.queue_box.configure(state="normal")
        self.queue_box.delete("0.0", "end")
        if not self.order_queue:
            self.queue_box.insert("0.0", "Queue is empty.")
        else:
            for i, item in enumerate(self.order_queue):
                status = "⏳ Pending"
                if i == 0 and self.is_processing: status = "⚙️ Brewing..."
                self.queue_box.insert("end", f"{i+1}. {item['display']} (Sugar: {item['sugar']}) - {status}\n")
        self.queue_box.configure(state="disabled")

    def process_queue(self):
        self.is_processing = True
        
        while self.order_queue:
            current_order = self.order_queue[0]
            self.refresh_queue_display()
            
            self.status_label.configure(text=f"Brewing: {current_order['display']}", text_color="#E67E22")
            for i in range(101):
                time.sleep(0.03) 
                self.progressbar.set(i / 100)
            
            try:
                response = requests.post(f"{SERVER_URL}/make", json=current_order)
                res_data = response.json()
                
                if res_data.get("status") == "success":
                    self.status_label.configure(text="DONE!", text_color="#27AE60")
                else:
                    self.status_label.configure(text="ERROR", text_color="red")
                    self.order_queue.clear() 
                    break
            except:
                self.status_label.configure(text="SERVER ERROR", text_color="red")
                break

            time.sleep(1) 
            if self.order_queue: self.order_queue.pop(0) 
            self.progressbar.set(0)
            
        self.is_processing = False
        self.status_label.configure(text="IDLE", text_color="gray")
        self.refresh_queue_display()
        self.update_resources()

    def update_resources(self):
        try:
            r = requests.get(f"{SERVER_URL}/status")
            if r.status_code == 200:
                d = r.json()
                t = (f"Water: {d['water']}ml | Coffee: {d['coffee']}g\n"
                     f"Milk: {d['milk']}ml  | Sugar: {d['sugar']}g\n"
                     f"Cups: {d['cups']}/{d['max_cups']} | Revenue: {d['revenue']}₴")
                self.res_label.configure(text=t)
        except: pass

    def update_status_loop(self):
        self.update_resources()
        self.after(3000, self.update_status_loop)

    def refill(self):
        try: requests.post(f"{SERVER_URL}/refill") 
        except: pass
        self.update_resources()

    def clean(self):
        try: requests.post(f"{SERVER_URL}/clean") 
        except: pass
        self.update_resources()

if __name__ == "__main__":
    app = CoffeeApp()
    app.mainloop()