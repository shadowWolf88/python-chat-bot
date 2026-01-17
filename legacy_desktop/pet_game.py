import sqlite3
import time
import random
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime, timedelta
from audit import log_event

DB_NAME = "pet_game.db"

class PetGame:
    def __init__(self, parent, username):
        self.parent = parent
        self.username = username    
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        
        # Define species_map here so it is always available
        self.species_map = {"Dog": "🐶", "Cat": "🐱", "Rabbit": "🐰", "Fox": "🦊", "Panda": "🐼", "Penguin": "🐧"}
        
        # Schema migration and setup
        self._check_and_update_schema()
        
        # Check if pet exists
        self.cursor.execute("SELECT COUNT(*) FROM pet")
        if self.cursor.fetchone()[0] == 0:
            self.setup_complete = False
            self._run_setup_wizard()
            if not self.setup_complete: return

        self.pet = self._load_pet()
        self._apply_time_decay() # Apply stats decay based on time passed
        self.window = None
        self.show_window()

    # -------------------------
    # DATABASE & MIGRATION
    # -------------------------
    def _check_and_update_schema(self):
        """Ensures table has all new columns for Tamagotchi features."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pet'")
        if self.cursor.fetchone():
            self.cursor.execute("PRAGMA table_info(pet)")
            columns = [info[1] for info in self.cursor.fetchall()]
            # If missing new columns (coins, hygiene, xp, etc), recreate table
            required = ["coins", "hygiene", "xp", "stage", "adventure_end"]
            if any(col not in columns for col in required):
                print("Upgrading database schema...")
                self.cursor.execute("DROP TABLE pet")
                self.conn.commit()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet (
                id INTEGER PRIMARY KEY,
                name TEXT,
                species TEXT,
                gender TEXT,
                hunger INTEGER,
                happiness INTEGER,
                energy INTEGER,
                hygiene INTEGER,
                coins INTEGER,
                xp INTEGER,
                stage TEXT,
                adventure_end REAL,
                last_updated REAL,
                hat TEXT
            )
        """)
        self.conn.commit()

    def _load_pet(self):
        self.cursor.execute("SELECT * FROM pet LIMIT 1")
        row = self.cursor.fetchone()
        return {
            "id": row[0], "name": row[1], "species": row[2], "gender": row[3],
            "hunger": row[4], "happiness": row[5], "energy": row[6],
            "hygiene": row[7], "coins": row[8], "xp": row[9],
            "stage": row[10], "adventure_end": row[11],
            "last_updated": row[12], "hat": row[13] if len(row) > 13 else "None"
        }

    def _save_pet(self):
        self.cursor.execute("""
            UPDATE pet
            SET hunger=?, happiness=?, energy=?, hygiene=?, coins=?, xp=?, stage=?, adventure_end=?, last_updated=?, hat=?
            WHERE id=?
        """, (
            self.pet["hunger"], self.pet["happiness"], self.pet["energy"], 
            self.pet["hygiene"], self.pet["coins"], self.pet["xp"], 
            self.pet["stage"], self.pet["adventure_end"], time.time(), 
            self.pet.get("hat", "None"), self.pet["id"]
        ))
        self.conn.commit()

    def _apply_time_decay(self):
        """Lowers stats based on how much time passed since last open."""
        now = time.time()
        hours_passed = (now - self.pet["last_updated"]) / 3600
        
        # Slower decay for mental health context (10x slower than standard)
        if hours_passed > 1.0:
            decay = int(hours_passed * 0.5) 
            
            # Helper to ensure stat doesn't drop below 10 purely from decay
            def gentle_decay(current_val, amount):
                new_val = current_val - amount
                return max(10, new_val) # Never drop below 10 due to time

            self.pet["hunger"] = gentle_decay(self.pet["hunger"], decay)
            self.pet["energy"] = gentle_decay(self.pet["energy"], decay)
            self.pet["hygiene"] = gentle_decay(self.pet["hygiene"], int(decay/2))
            self._save_pet()

    # -------------------------
    # EVOLUTION SYSTEM (NEW)
    # -------------------------
    def _check_evolution(self):
        """Checks XP and ages the pet."""
        current_stage = self.pet["stage"]
        new_stage = current_stage
        
        if self.pet["xp"] >= 500 and current_stage == "Baby":
            new_stage = "Child"
        elif self.pet["xp"] >= 1500 and current_stage == "Child":
            new_stage = "Adult"
            
        if new_stage != current_stage:
            self.pet["stage"] = new_stage
            messagebox.showinfo("Growth!", f"🎉 Amazing! {self.pet['name']} has evolved into a {new_stage}!")

    # -------------------------
    # WIZARD
    # -------------------------
    def _run_setup_wizard(self):
        setup_win = ctk.CTkToplevel(self.parent)
        setup_win.title("Adoption Center")
        setup_win.geometry("400x600")
        setup_win.attributes('-topmost', True)
        
        ctk.CTkLabel(setup_win, text="Adopt a Companion", font=("Arial", 20, "bold")).pack(pady=20)
        
        ctk.CTkLabel(setup_win, text="Name:").pack()
        name_entry = ctk.CTkEntry(setup_win); name_entry.pack(pady=5)

        ctk.CTkLabel(setup_win, text="Species:").pack(pady=10)
        species_var = tk.StringVar(value="Dog")
        f = ctk.CTkFrame(setup_win, fg_color="transparent")
        f.pack()
        for i, (k, v) in enumerate(self.species_map.items()):
            ctk.CTkRadioButton(f, text=f"{v} {k}", variable=species_var, value=k).grid(row=i//2, column=i%2, padx=10, pady=5)

        ctk.CTkLabel(setup_win, text="Gender:").pack(pady=10)
        gender_var = tk.StringVar(value="Neutral")
        ctk.CTkSegmentedButton(setup_win, values=["Male", "Female", "Neutral"], variable=gender_var).pack()

        def finish():
            if not name_entry.get(): return
            self.cursor.execute("""
                INSERT INTO pet (name, species, gender, hunger, happiness, energy, hygiene, coins, xp, stage, adventure_end, last_updated, hat)
                VALUES (?, ?, ?, 70, 70, 70, 80, 0, 0, 'Baby', 0, ?, 'None')
            """, (name_entry.get(), species_var.get(), gender_var.get(), time.time()))
            self.conn.commit()
            self.setup_complete = True
            setup_win.destroy()

        ctk.CTkButton(setup_win, text="Adopt!", command=finish, fg_color="#2ecc71").pack(pady=30)
        self.parent.wait_window(setup_win)

    # -------------------------
    # MAIN UI
    # -------------------------
    def show_window(self):
        if self.window is None or not tk.Toplevel.winfo_exists(self.window):
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title(f"{self.pet['name']}'s Home")
            self.window.geometry("400x650")
            self.window.attributes('-topmost', True) 
            self._build_ui()
            self._refresh_ui()
        else:
            self.window.focus()

    def _build_ui(self):
        self.frame = ctk.CTkFrame(self.window)
        self.frame.pack(fill="both", expand=True, padx=15, pady=15)

        # -- HEADER: Coins & XP --
        top_bar = ctk.CTkFrame(self.frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=5)
        self.coin_label = ctk.CTkLabel(top_bar, text=f"🪙 {self.pet['coins']}", font=("Arial", 12, "bold"))
        self.coin_label.pack(side="right", padx=10)
        self.xp_label = ctk.CTkLabel(top_bar, text=f"⭐ XP: {self.pet['xp']}", font=("Arial", 12))
        self.xp_label.pack(side="left", padx=10)

        # -- PET AREA (Canvas for floating messes) --
        self.canvas = tk.Canvas(self.frame, height=200, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill="x", pady=10)
        
        # -- STATS --
        self.bars = {}
        for stat, col in [("Hunger", "#e74c3c"), ("Happiness", "#2ecc71"), ("Energy", "#f1c40f"), ("Hygiene", "#3498db")]:
            ctk.CTkLabel(self.frame, text=stat, font=("Arial", 10)).pack(anchor="w", padx=10)
            b = ctk.CTkProgressBar(self.frame, height=10, progress_color=col)
            b.pack(fill="x", padx=10, pady=(0, 5))
            self.bars[stat] = b

        self.status_label = ctk.CTkLabel(self.frame, text="...", font=("Arial", 12, "italic"))
        self.status_label.pack(pady=5)

        # -- ACTIONS --
        act_grid = ctk.CTkFrame(self.frame, fg_color="transparent")
        act_grid.pack(pady=10)
        
        ctk.CTkButton(act_grid, text="🧹 Declutter", width=100, command=self.declutter_task, fg_color="#9b59b6").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(act_grid, text="🛍️ Shop", width=100, command=self.open_shop, fg_color="#e67e22").grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(act_grid, text="🌲 Walk (30m)", width=100, command=self.go_adventure, fg_color="#27ae60").grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(act_grid, text="💤 Sleep", width=100, command=lambda: messagebox.showinfo("Sleep", "Pet sleeps automatically between 11PM and 7AM!"), fg_color="#34495e").grid(row=1, column=1, padx=5, pady=5)

    def _refresh_ui(self):
        if not self.window or not self.window.winfo_exists(): return
        
        # Update Bars
        self.bars["Hunger"].set(self.pet["hunger"] / 100)
        self.bars["Happiness"].set(self.pet["happiness"] / 100)
        self.bars["Energy"].set(self.pet["energy"] / 100)
        self.bars["Hygiene"].set(self.pet["hygiene"] / 100)
        
        self.coin_label.configure(text=f"🪙 {self.pet['coins']}")
        self.xp_label.configure(text=f"⭐ XP: {self.pet['xp']} ({self.pet['stage']})")

        # 1. SLEEP CHECK
        current_hour = datetime.now().hour
        is_asleep = (current_hour >= 23 or current_hour < 7)
        
        # 2. ADVENTURE CHECK
        is_away = False
        if self.pet["adventure_end"] > 0:
            if time.time() < self.pet["adventure_end"]:
                is_away = True
                mins_left = int((self.pet["adventure_end"] - time.time()) / 60)
                self.status_label.configure(text=f"Out exploring... Back in {mins_left} mins")
            else:
                # Returned!
                self.pet["adventure_end"] = 0
                bonus = random.randint(10, 50)
                self.pet["coins"] += bonus
                self.pet["xp"] += 20
                messagebox.showinfo("Returned!", f"{self.pet['name']} returned with {bonus} coins and a cool leaf! 🍃")
                self._save_pet()

        # 3. DRAW PET ON CANVAS
        self.canvas.delete("all")
        cw, ch = 350, 200
        
        if is_away:
            self.canvas.create_text(cw/2, ch/2, text="🌲", font=("Arial", 50))
        elif is_asleep:
            self.canvas.create_text(cw/2, ch/2, text="💤", font=("Arial", 50))
            self.status_label.configure(text=f"{self.pet['name']} is sleeping. Shh!")
        else:
            # Species Emoji (Now safe to access)
            em = self.species_map.get(self.pet["species"], "🐾")
            # Size based on Evolution
            font_size = 60 if self.pet["stage"] == "Baby" else 100
            self.canvas.create_text(cw/2, ch/2, text=em, font=("Arial", font_size))
            
            # Hat?
            if self.pet.get("hat") and self.pet["hat"] != "None":
                self.canvas.create_text(cw/2, ch/2 - 45, text=self.pet["hat"], font=("Arial", 40))

            # Mess/Dust Bunnies (Hygiene Check)
            if self.pet["hygiene"] < 50:
                for _ in range(5):
                    x, y = random.randint(20, 330), random.randint(20, 180)
                    self.canvas.create_text(x, y, text="☁️", font=("Arial", 20))
                self.status_label.configure(text=f"It's messy here! Try 'Declutter'.")
            else:
                self.status_label.configure(text=f"{self.pet['name']} is happy to see you!")

    # -------------------------
    # ACTIONS & REWARDS
    # -------------------------
    def reward(self, action, activity_type=None):
        """Called by main.py"""
        
        # Standardized Rewards: 5 Coins, 15 XP per action
        # Also ensure EVERY action boosts ALL stats slightly (Guilt-free logic)
        base_boost = 3 
        coin_gain = 5
        xp_gain = 15

        # Apply specific bonuses on top of the base boost
        hun = base_boost
        hap = base_boost
        en = base_boost
        hyg = base_boost

        if action == "diary": 
            hap += 10; en += 5
        elif action == "medication": 
            en += 20 
        elif action == "grounding": 
            hap += 10; en += 5
        elif action == "therapy": 
            hun += 10; hap += 10; en += 10; hyg += 5; coin_gain = 5; xp_gain = 30 # slightly more XP for therapy
        if activity_type == "cbt":
            self.pet["coins"] += 15
            self.pet["xp"] += 20
        elif activity_type == "clinical":
            self.pet["coins"] += 20
            self.pet["xp"] += 30
        self._save_pet()
        self._refresh_ui()        

        # Audit reward event
        try:
            log_event(self.username, "system", "pet_reward", f"action={action}, type={activity_type}, coins={self.pet['coins']}, xp={self.pet['xp']}")
        except: pass

        self._mod(hun=hun, hap=hap, en=en, hyg=hyg, coin=coin_gain, xp=xp_gain)
        
        self._check_evolution()
        self._save_pet()
        self._refresh_ui()

    def _mod(self, hun=0, hap=0, en=0, hyg=0, coin=0, xp=0):
        self.pet["hunger"] = max(0, min(100, self.pet["hunger"] + hun))
        self.pet["happiness"] = max(0, min(100, self.pet["happiness"] + hap))
        self.pet["energy"] = max(0, min(100, self.pet["energy"] + en))
        self.pet["hygiene"] = max(0, min(100, self.pet["hygiene"] + hyg))
        self.pet["coins"] += coin
        self.pet["xp"] += xp

    def declutter_task(self):
        d_win = ctk.CTkToplevel(self.window)
        d_win.title("Declutter The Mind")
        d_win.geometry("300x400")
        
        ctk.CTkLabel(d_win, text="Throw away 3 worries to clean the room:", wraplength=250).pack(pady=10)
        e1 = ctk.CTkEntry(d_win, placeholder_text="Worry 1..."); e1.pack(pady=5)
        e2 = ctk.CTkEntry(d_win, placeholder_text="Worry 2..."); e2.pack(pady=5)
        e3 = ctk.CTkEntry(d_win, placeholder_text="Worry 3..."); e3.pack(pady=5)
        
        def toss():
            if e1.get() or e2.get() or e3.get():
                self._mod(hyg=40, hap=5, xp=15, coin=5) # 5 coins reward
                self._save_pet()
                self._refresh_ui()
                messagebox.showinfo("Cleaned!", "The room (and your mind) is clearer. (+5 Coins)")
                d_win.destroy()
        
        ctk.CTkButton(d_win, text="🗑️ Throw Away", command=toss, fg_color="#e74c3c").pack(pady=20)

    def open_shop(self):
        s_win = ctk.CTkToplevel(self.window)
        s_win.title("Wellness Shop")
        s_win.geometry("300x400")
        
        ctk.CTkLabel(s_win, text=f"Your Coins: 🪙 {self.pet['coins']}", font=("Arial", 14, "bold")).pack(pady=10)
        
        items = [
            ("🍎 Apple (+20 Hunger)", 10, lambda: self._buy_food(20)),
            ("🧁 Cupcake (+40 Hun/Hap)", 25, lambda: self._buy_food(40, 10)),
            ("🎩 Top Hat (Cosmetic)", 100, lambda: self._set_hat("🎩")),
            ("🎀 Bow (Cosmetic)", 100, lambda: self._set_hat("🎀")),
            ("👑 Crown (Cosmetic)", 500, lambda: self._set_hat("👑")),
        ]
        
        for txt, price, cmd in items:
            btn_txt = f"{txt} - 🪙{price}"
            ctk.CTkButton(s_win, text=btn_txt, command=lambda c=cmd, p=price: self._purchase(p, c)).pack(pady=5)

    def _purchase(self, cost, effect_func):
        if self.pet["coins"] >= cost:
            self.pet["coins"] -= cost
            effect_func()
            self._save_pet()
            self._refresh_ui()
            # Close shop to refresh coin display or just update
            messagebox.showinfo("Bought!", "Item purchased successfully.")
        else:
            messagebox.showerror("Funds", "Not enough mindfulness coins!")

    def _buy_food(self, hun_gain, hap_gain=0):
        self._mod(hun=hun_gain, hap=hap_gain)

    def _set_hat(self, icon):
        self.pet["hat"] = icon

    def go_adventure(self):
        if self.pet["energy"] < 20:
            messagebox.showwarning("Tired", "Pet is too tired for a walk!")
            return
        
        confirm = messagebox.askyesno("Adventure", "Send pet on a 30 min walk?\n(You won't be able to interact for a bit)")
        if confirm:
            self.pet["adventure_end"] = time.time() + (30 * 60) # 30 mins
            self.pet["energy"] -= 20
            self._save_pet()
            self._refresh_ui()