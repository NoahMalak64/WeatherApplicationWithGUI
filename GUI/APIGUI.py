import tkinter as tk
from tkinter import messagebox
import ApiKeyHandler as handler
import PasswordHash as hasher
from pathlib import Path
import sys, os
from datetime import date
import DisplayApiData as display

# need this when running from file instead of running from root--this will be a big fix later 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from API.FetchAPIJson import api_contents
from Graphs import GenerateGraph as graph
from PIL import Image, ImageTk
"""
MAIN RUN FILE

***IMPORTANT NOTE***
MUST be in /GUI to run this file:
---python APIGUI.py--- 
"""
try:
    from Switcher import WindowSwitcher
except Exception:
    WindowSwitcher = None

class main_window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snow Fall Data Collector")
        self.root.geometry("450x500")

        # store up to 4 locations
        self.locations = ["", "", "", ""]

        self.current_location_index = 0
        self.location_views = []      # one frame per location
        self.location_header_label = None
        self.content_container = None

        # 1) Login first
        self.login()

        # 2) After successful login, route based on API key validity
        self.route_after_login()

        self.root.mainloop()  # blocking loop


    def clear_window(self): # declares type of tk and returns None. 
        """
        Destroys all objects in the window
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    # -------------------------
    # Routing after login
    # -------------------------
    def route_after_login(self):
        key = self.load_api_key()
        is_valid = False
        if key and hasattr(handler.ApiHandler, "validate_key"):
            try:
                is_valid = handler.ApiHandler.validate_key(key) #returns true if key is valid
            except Exception:
                is_valid = False

        if is_valid:
            self.locations = self.load_locations()
            if any(self.locations):
                self.go_to_dashboard()
            else:
                self.init_location_prompt() #only go here if there are NO locations
        else:
            # Show the isolated API validation window so the user can enter a valid key if no locations present 
            self.init_api_prompt()

    # -------------------------
    # API validation / key setup (isolated window)
    # -------------------------
    def init_api_prompt(self):
        # Clear previous content if any (e.g. when returning to this UI)
        self.clear_root()

        has_file = self.check_for_key_file()
        status = "Found" if has_file else "Missing"
        
        api_key = handler.ApiHandler.load_api_key()
        if not (handler.ApiHandler.validate_key(api_key)):
            api_status = "invalid Key"
        
        self.init_api_win = tk.Frame(self.root, width=450, height=500)
        self.init_api_win.pack(pady=10, padx=10, fill="both", expand=True)

        tk.Label(self.init_api_win, text="API Key Setup", font=("Arial", 14, "bold")).pack(pady=6)
        status_label = tk.Label(self.init_api_win, text=f"Key file status: {status}")
        status_label.pack(pady=5)
        status_label = tk.Label(self.init_api_win, text=f"API Key status: {api_status}")
        status_label.pack(pady=5)

        tk.Label(self.init_api_win, text="Enter API Key:").pack(pady=4)
        key_input = tk.Entry(self.init_api_win, width=40)
        key_input.pack(pady=4)

        save_api_button = tk.Button(
            self.init_api_win,
            text="Save API Key",
            command=lambda: self.validate_save_and_go(key_input, status_label)
        )
        save_api_button.pack(pady=8)

        tk.Label(
            self.init_api_win,
            text="Don't have an API Key? Click the link below:"
        ).pack(pady=4)

        import webbrowser

        link = tk.Label(
            self.init_api_win,
            text="https://www.visualcrossing.com/sign-up/",
            fg="#4da3ff",
            cursor="hand2",
            font=("Arial", 16, "underline")
        )
        link.pack(pady=4)

        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.visualcrossing.com/sign-up/"))




    def validate_save_and_go(self, input_field, status_label):
        """Validate the entered key by calling ApiHandler.validate_key.
        If valid, save and go straight to dashboard.
        """
        key = input_field.get().strip()
        if not key:
            messagebox.showerror("Error", "API key cannot be empty.")
            return

        is_valid = False
        if hasattr(handler.ApiHandler, "validate_key"):
            try:
                is_valid = handler.ApiHandler.validate_key(key)
            except Exception:
                is_valid = False

        if not is_valid:
            status_label.config(text="Key status: Invalid", fg="red")
            messagebox.showerror("API Key", "Invalid or expired API key. Please try again.")
            return

        # Save only if valid
        if hasattr(handler.ApiHandler, "save_api_key"):
            handler.ApiHandler.save_api_key(key)
        else:
            Path("Storage/KeyStorage.env").write_text(f"MY_API_KEY={key}")

        status_label.config(text="Key status: Valid", fg="green")
        messagebox.showinfo("API Key", "API key saved and validated.")
        # proceed to dashboard
        try:
            self.init_api_win.destroy()
        except Exception:
            pass
        self.init_location_prompt()



    # -------------------------
    # Location setup
    # -------------------------
    def init_location_prompt(self):
        #Ask user to enter up to 4 locations, then go to dashboard. This is the GUI code
        self.clear_root()

        self.location_win = tk.Frame(self.root, width=360, height=460)
        self.location_win.pack(pady=10, padx=10, fill="both", expand=True)
        tk.Label(
            self.location_win,
            text="Location Setup",
            font=("Arial", 14, "bold")
        ).pack(pady=6)

        tk.Label(
            self.location_win,
            text="Enter up to 4 locations (city, ZIP, etc.):"
        ).pack(pady=4)

        # load existing locations (if any) to pre-fill
        existing = self.load_locations()
        if not existing or len(existing) < 4:
            existing = (existing or []) + [""] * (4 - len(existing))

        self.location_entries = []
        for i in range(4):
            tk.Label(
                self.location_win,
                text=f"Location {i+1}:"
            ).pack(pady=(6 if i == 0 else 2), anchor="w", padx=10)

            e = tk.Entry(self.location_win, width=40)
            e.pack(pady=2)
            if existing[i]:
                e.insert(0, existing[i])
            self.location_entries.append(e)

        tk.Button(
            self.location_win,
            text="Save Locations",
            command=self.validate_locations_and_go
        ).pack(pady=12)

    def validate_locations_and_go(self):
        locs = [e.get().strip() for e in self.location_entries]

        # Require at least one location
        if not (locs[0] or locs[1] or locs[2] or locs[3]):
            messagebox.showerror(
                "Locations",
                "Please enter at least Location 1."
            )
            return
        
        # Validate each non-empty location
        for location in locs:
            # Skip blank slots (Locations 2–4 can be empty)
            if not location:
                continue

            req_url = api_contents(date.today(), date.today(), location, handler.ApiHandler.load_api_key(), 1)
            if not handler.ApiHandler.validate_location(req_url):
                messagebox.showerror("Invalid Location", f"Invalid Location: {location}")
                return
            
                                         
        # make sure to store 4 values
        while len(locs) < 4:
            locs.append("")

        self.locations = locs
        self.save_locations(locs)

        try:
            self.location_win.destroy()
        except Exception:
            pass

        self.go_to_dashboard()


    def save_locations(self, locations):
    # Save locations to a small env file
        path = Path("../Storage/locations.env")
        lines = []
        for i, loc in enumerate(locations[:4]):
            lines.append(f"LOC{i+1}={loc}\n")
        path.write_text("".join(lines), encoding="utf-8")
    
    def load_locations(self):
        # Load up to 4 locations from locations.env
        path = Path("../Storage/locations.env")
        if not path.exists():
            return ["", "", "", ""]
        
        locs = ["", "", "", ""]
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("LOC1="):
                    locs[0] = line.split("LOC1=", 1)[1].strip()
                elif line.startswith("LOC2="):
                    locs[1] = line.split("LOC2=", 1)[1].strip()
                elif line.startswith("LOC3="):
                    locs[2] = line.split("LOC3=", 1)[1].strip()
                elif line.startswith("LOC4="):
                    locs[3] = line.split("LOC4=", 1)[1].strip()
        except Exception:
            pass

        return locs
    

    # -------------------------
    # Dashboard navigation
    # -------------------------
    def go_to_dashboard(self):
        self.clear_window()
        self.root.deiconify()
        self.root.geometry("1080x650")

        # Make sure we have locations loaded
        if not any(self.locations):
            self.locations = self.load_locations()

        # fallback labels if empty
        labels = [
            self.locations[0] or "Location 1",
            self.locations[1] or "Location 2",
            self.locations[2] or "Location 3",
            self.locations[3] or "Location 4",
        ]

        # Root grid config
        for i in range(12):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(8):
            self.root.grid_rowconfigure(i, weight=1)

        # --- Top navigation buttons (switch location views) ---
        for i in range(4):
            tk.Button(
                self.root,
                text=labels[i],
                command=lambda idx=i: self.show_location(idx)
            ).grid(
                row=0,
                column=i * 3,
                columnspan=3,
                pady=10,
                padx=2,
                sticky="ew"
            )

        # --- Content container for all dashboards (area under the buttons) ---
        self.content_container = tk.Frame(self.root, borderwidth=0)
        self.content_container.grid(
            row=1,
            column=0,
            columnspan=12,
            rowspan=7,
            padx=10,
            pady=10,
            sticky="nsew",
        )
        self.content_container.grid_rowconfigure(0, weight=0)  # header row
        self.content_container.grid_rowconfigure(1, weight=1)  # page row
        self.content_container.grid_columnconfigure(0, weight=1)

        # Header: shows which location window we're in
        self.location_header_label = tk.Label(
            self.content_container,
            text="",
            font=("Arial", 14, "bold")
        )
        self.location_header_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # --- Create one page per location, each with the grid layout ---
        self.location_views = []

        for i in range(4):
            frame = tk.Frame(self.content_container, borderwidth=0)
            frame.grid(row=1, column=0, sticky="nsew")

            # Internal grid inside each location frame
            for c in range(12):
                frame.grid_columnconfigure(c, weight=1)
            for r in range(8):
                frame.grid_rowconfigure(r, weight=1)

            # LEFT text frame (current text_frame)
            text_frame = tk.Frame(
                frame,
                # borderwidth=1,
                # highlightbackground="black",
                # relief="solid",
                # highlightcolor="red",
                height=486
            )
            text_frame.grid(
                column=0,
                row=0,
                columnspan=2,
                rowspan=8,
                padx=10,
                pady=10,
                sticky="nsew"
            )
            text_frame.columnconfigure(0, weight=1)

            # ----------API data fetch part-----------------------------------------------------
            # Put API calls to data here to display relevant data for each windpow
            # this will display for all windows, find a way to determine which data to display on each window
            day_summary = display.displayApiData(self.locations[i])

            if day_summary is None:
                # Safe defaults when no data / invalid location
                date_display        = "No data"
                tempmax_display     = "-"
                tempmin_display     = "-"
                snowfall_display    = "-"
                description_display = "No weather data available."
            else:
                date_display        = day_summary["date"]
                tempmax_display     = day_summary["tempmax"]
                tempmin_display     = day_summary["tempmin"]
                snowfall_display    = day_summary["snow"]
                description_display = day_summary["description"]
            #-------------------------------------------------------------------------

            tk.Label(text_frame, text=date_display).grid(column=0, sticky="n")
            tk.Label(
                text_frame,
                text=f"High: {tempmax_display}\nLow: {tempmin_display}",
                font=("TkDefaultFont", 24)
            ).grid(column=0, sticky="n")
            tk.Label(text_frame, text=f"Snowfall: {snowfall_display}").grid(column=0, sticky="n")
            tk.Label(
                text_frame,
                text=f"{description_display}",
                wraplength=150
            ).grid(column=0, sticky="n")

            # TOP center frame
            frame.top_frame = tk.Frame(
                frame,
                # borderwidth=1,
                # highlightbackground="black",
                # relief="solid",
                # highlightcolor="red",
                height=162
            )
            frame.top_frame.grid(
                row=0,
                column=2,
                columnspan=10,
                padx=10,
                sticky="ew"
            )

            # MIDDLE left frame
            frame.middle_left = tk.Frame(
                frame,
                # borderwidth=1,
                # highlightbackground="black",
                # relief="solid",
                # highlightcolor="red",
                height=324
            )
            frame.middle_left.grid(
                row=1,
                column=2,
                columnspan=5,
                rowspan=8,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # MIDDLE right frame
            frame.middle_right = tk.Frame(
                frame,
                # borderwidth=1,
                # highlightbackground="black",
                # relief="solid",
                # highlightcolor="red",
                height=324
            )
            frame.middle_right.grid(
                row=1,
                column=7,
                columnspan=5,
                rowspan=8,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # Later you can stash references to these per-location frames if needed
            self.location_views.append(frame)

        # Start on the first location
        self.show_location(0)




    def show_location(self, index: int):
        """Raise the dashboard for the given location index (0–3)."""
        if not self.location_views:
            return

        # Clamp index to valid range
        index = max(0, min(len(self.location_views) - 1, index))
        self.current_location_index = index

        label = self.locations[index] or f"Location {index + 1}"

        # Update header text
        if self.location_header_label is not None:
            self.location_header_label.config(
                text=f"{label}"
            )

        # Generate the graphs for this page
        graph.snowfall_grid(self.locations[index])
        graph.temperature_week(self.locations[index])
        graph.snowfall_week(self.locations[index])

        self.add_image_to_frame(self.location_views[index].top_frame, "../Graphs/52WeekPlot.png")
        self.add_image_to_frame(self.location_views[index].middle_right, "../Graphs/SnowfallWeekGraph.png")
        self.add_image_to_frame(self.location_views[index].middle_left, "../Graphs/TemperatureWeekGraph.png")
        # Raise the frame for this location
        frame = self.location_views[index]
        frame.tkraise()

    def add_image_to_frame(self, frame, path):
        if not hasattr(frame, "_image_label"):
            frame._image_label = tk.Label(frame)
            frame._image_label.grid(row=0, column=0, sticky="nsew")

        def on_resize(event):
            # if frame._resize_count <5:
            #     frame._resize_count += 1
            #     frame.update_idletasks() 

            fwidth, fheight = frame.winfo_width(), frame.winfo_height()
            
            img = Image.open(path)

            # calculate scale to fit frame size while keeping aspect ratio 
            imgwidth, imgheight = img.size
            scale = min(fwidth/imgwidth, fheight/imgheight)
            new_size = (int(imgwidth*scale), int(imgheight*scale))
            # resize image
            img_resized = img.resize(new_size, Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img_resized)

            frame._image_label.config(image=tk_img)
            frame._image_label.image = tk_img
            # label = tk.Label(frame, image=tk_img) 
            # label.image = tk_img
            # label.grid(row=0, column=0, sticky="nsew")
            # else:
            #     # after 5 resizes, stop listening
            #     frame.unbind("<Configure>")
        frame.bind("<Configure>", on_resize)

    # -------------------------
    # Key/file helpers
    # -------------------------
    def generate_key_file(self):
        if hasattr(handler.ApiHandler, "generateKeyFile"):
            handler.ApiHandler.generateKeyFile()
            messagebox.showinfo("File", "KeyStorage.env created (or already exists).")
        else:
            env_path = Path("../Storage/KeyStorage.env")
            if not env_path.exists():
                env_path.write_text("")
            messagebox.showinfo("File", "KeyStorage.env created (or already exists).")

    def check_for_key_file(self):
        if hasattr(handler.ApiHandler, "check_for_file"):
            return handler.ApiHandler.check_for_file()
        return Path("../Storage/KeyStorage.env").exists()

    def load_api_key(self):
        env_path = Path("../Storage/KeyStorage.env")
        if not env_path.exists():
            return ""
        try:
            for line in env_path.read_text().splitlines():
                if line.startswith("MY_API_KEY="):
                    return line.split("MY_API_KEY=", 1)[1].strip()
        except Exception:
            pass
        return ""

    # -------------------------
    # Login / password
    # -------------------------
    def initial_login(self):
        def create_password():
            hasher.main(password_box.get(), "SALT")
            initial_login_window.destroy()

        initial_login_window = tk.Frame(self.root, width=360, height=460)
        initial_login_window.place(x=0, y=0)
        initial_login_window.pack(pady=10)

        tk.Label(initial_login_window, text="First time login detected").pack()
        tk.Label(initial_login_window, text="Please create a password").pack(pady=5)

        password_box = tk.Entry(initial_login_window, show="*")
        password_box.pack(pady=5)

        tk.Button(initial_login_window, text="Create Password", command=create_password).pack()
        initial_login_window.wait_window()

    def login(self):
        def submit_login():
            password = password_box.get()
            if (hasher.main(password, "SALT")):
                messagebox.showinfo("Login Successful", "Welcome")
                login_window.destroy()
            else:
                tk.Label(login_window, text="Incorrect Password").pack(pady=5)

        if (hasher.file_setup() == False):
            self.initial_login()

        login_window = tk.Frame(self.root, width=360, height=460)
        login_window.place(x=0, y=0)
        login_window.pack(pady=10)

        tk.Label(login_window, text="Password:").pack(pady=5)
        password_box = tk.Entry(login_window, show="*")
        password_box.pack(pady=5)

        tk.Button(login_window, text="Login", command=submit_login).pack(pady=10)
        login_window.wait_window()

    # -------------------------
    # Utilities
    # -------------------------
    def clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

# Run
if __name__ == "__main__":
    w = main_window()
