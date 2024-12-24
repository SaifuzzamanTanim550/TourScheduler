import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import customtkinter as ctk


class Navigator:
    def __init__(self, name):
        self.name = name
        self.availability = {}
        self.tour_count = 0
        self.assigned_tours = set()

    def add_availability(self, day, start_time, end_time):
        if day not in self.availability:
            self.availability[day] = []
        self.availability[day].append((start_time, end_time))

    def increment_tour_count(self):
        self.tour_count += 1

    def assign_tour(self, day, time):
        self.assigned_tours.add((day, time))
        self.increment_tour_count()

    def is_assigned(self, day, time):
        return (day, time) in self.assigned_tours

    def display_availability(self):
        return {day: [(start, end) for start, end in times] for day, times in self.availability.items()}

    def display_tour_count(self):
        return self.tour_count


class Schedule:
    def __init__(self):
        self.navigators = []

    def add_navigator(self, navigator):
        self.navigators.append(navigator)

    def display_all_availabilities(self):
        return {navigator.name: navigator.display_availability() for navigator in self.navigators}


class TourScheduler:
    def __init__(self, schedule):
        self.schedule = schedule
        self.tours = {day: {"10:00 AM": None, "3:00 PM": None} for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
        self.group_tours = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}

    def assign_tours(self):
        import random

        # Assign walk-in tours
        for day, slots in self.tours.items():
            for time, assigned in slots.items():
                if assigned == "Pending":
                    available_navigators = [
                        navi for navi in self.schedule.navigators
                        if self.is_available_for_one_hour(navi, day, time) and not navi.is_assigned(day, time)
                    ]
                    if available_navigators:
                        # Shuffle for fairness, then pick the navigator with the fewest tours
                        random.shuffle(available_navigators)
                        assigned_navigator = min(available_navigators, key=lambda navi: navi.tour_count)
                        self.tours[day][time] = assigned_navigator.name
                        assigned_navigator.assign_tour(day, time)

        # Assign group tours
        for day, group_tours in self.group_tours.items():
            for tour in group_tours:
                available_navigators = [
                    navi for navi in self.schedule.navigators
                    if self.is_available_for_one_hour(navi, day, tour["time"]) and not navi.is_assigned(day, tour["time"])
                ]
                if available_navigators:
                    # Shuffle and sort for fairness
                    random.shuffle(available_navigators)
                    assigned_navigators = []

                    # Assign the first navigator
                    primary_navigator = min(available_navigators, key=lambda navi: navi.tour_count)
                    assigned_navigators.append(primary_navigator.name)
                    primary_navigator.assign_tour(day, tour["time"])

                    # Assign a second navigator if the group has more than 30 students
                    if tour["students"] > 30 and len(available_navigators) > 1:
                        available_navigators.remove(primary_navigator)  # Remove the already assigned navigator
                        secondary_navigator = min(available_navigators, key=lambda navi: navi.tour_count)
                        assigned_navigators.append(secondary_navigator.name)
                        secondary_navigator.assign_tour(day, tour["time"])

                    # Update the tour's assigned navigators
                    tour["navigators"] = assigned_navigators

    def is_available_for_one_hour(self, navigator, day, time):
        """
        Check if the navigator is available for the given time and one-hour duration.
        """
        if day not in navigator.availability:
            return False

        time_obj = datetime.strptime(time, "%I:%M %p")
        one_hour_later = time_obj + timedelta(hours=1)

        for start_time, end_time in navigator.availability[day]:
            start = datetime.strptime(start_time, "%I:%M %p")
            end = datetime.strptime(end_time, "%I:%M %p")
            if start <= time_obj and one_hour_later <= end:
                return True

        return False


class Main:
    def __init__(self):
        self.schedule = Schedule()
        self.tour_scheduler = TourScheduler(self.schedule)

    def add_navigator(self, name, availability):
        navigator = Navigator(name)
        for day, times in availability.items():
            for start_time, end_time in times:
                navigator.add_availability(day, start_time, end_time)
        self.schedule.add_navigator(navigator)


class TourSchedulerGUI:
    def __init__(self, root, main):
        self.root = root
        self.main = main
        self.root.title("Tour Scheduler")
        self.setup_ui()

    def setup_ui(self):
        # Set a larger initial size and make the window resizable
        self.root.geometry("600x550")
        self.root.minsize(600, 400)

        # Main frame with Maroon background
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg="#800000")  # Maroon color
        main_frame.pack(fill="both", expand=True)

        # Title Label
        title_label = tk.Label(
            main_frame,
            text="BC Navigators Tour Scheduler",
            font=("Arial", 22, "bold"),
            bg="#800000",  # Maroon background
            fg="white",  # White text for contrast
        )
        title_label.pack(pady=10)

        # Buttons Section
        button_frame = tk.Frame(main_frame, bg="#800000")  # Maroon background
        button_frame.pack(fill="x", pady=10)

        # Button Styling
        button_width = 200  # Set uniform width for all buttons
        button_height = 45  # Adjust button height
        button_font = ("Arial", 16)  # Larger font size

        # Change Schedule Button
        ctk.CTkButton(
            button_frame,
            text="Change Schedule",
            width=button_width,
            height=button_height,
            corner_radius=20,  # Rounded corners
            fg_color="#F5F5DC",  # Warm white background
            hover_color="#D3D3D3",  # Light gray when hovering
            text_color="black",  # Black text
            font=button_font,
            command=self.change_schedule_window,  # Open change schedule window
        ).pack(pady=3)

        ctk.CTkButton(
            button_frame,
            text="View Availabilities",
            width=button_width,
            height=button_height,
            corner_radius=20,
            fg_color="#F5F5DC",
            hover_color="#D3D3D3",
            text_color="black",
            font=button_font,
            command=self.view_availabilities,
        ).pack(pady=3)

        ctk.CTkButton(
            button_frame,
            text="Input Walk-In Tours",
            width=button_width,
            height=button_height,
            corner_radius=20,
            fg_color="#F5F5DC",
            hover_color="#D3D3D3",
            text_color="black",
            font=button_font,
            command=self.input_walk_in_tours_window,
        ).pack(pady=3)

        ctk.CTkButton(
            button_frame,
            text="Input Group Tours",
            width=button_width,
            height=button_height,
            corner_radius=20,
            fg_color="#F5F5DC",
            hover_color="#D3D3D3",
            text_color="black",
            font=button_font,
            command=self.input_group_tours_window,
        ).pack(pady=3)

        ctk.CTkButton(
            button_frame,
            text="Assign Tours",
            width=button_width,
            height=button_height,
            corner_radius=20,
            fg_color="#F5F5DC",
            hover_color="#D3D3D3",
            text_color="black",
            font=button_font,
            command=self.assign_tours,
        ).pack(pady=3)

        ctk.CTkButton(
            button_frame,
            text="View Weekly Tours",
            width=button_width,
            height=button_height,
            corner_radius=20,
            fg_color="#F5F5DC",
            hover_color="#D3D3D3",
            text_color="black",
            font=button_font,
            command=self.view_weekly_tours,
        ).pack(pady=3)

        ctk.CTkButton(
            button_frame,
            text="View Tour Counts",
            width=button_width,
            height=button_height,
            corner_radius=20,
            fg_color="#F5F5DC",
            hover_color="#D3D3D3",
            text_color="black",
            font=button_font,
            command=self.view_tour_counts,
        ).pack(pady=3)

        # Footer
        footer_label = tk.Label(
            main_frame,
            text="Designed by Saifuzzaman Tanim",
            font=("Arial", 10, "italic"),
            bg="#800000",  # Maroon background
            fg="white",  # White text
        )
        footer_label.pack(side="bottom", pady=10)

    def change_schedule_window(self):
        window = tk.Toplevel(self.root)
        window.title("Change Navigator Schedule")
        window.geometry("400x450")
        window.resizable(False, False)

        tk.Label(window, text="Change Schedule for Navigator", font=("Arial", 14, "bold")).pack(pady=10)

        # Dropdown to select navigator
        frame_navigator = tk.Frame(window, pady=5)
        frame_navigator.pack(fill="x", padx=10)
        tk.Label(frame_navigator, text="Select Navigator:", font=("Arial", 12)).pack(anchor="w")
        navigator_names = [navigator.name for navigator in self.main.schedule.navigators]
        navigator_var = tk.StringVar()
        navigator_dropdown = ttk.Combobox(frame_navigator, textvariable=navigator_var, values=navigator_names,
                                          state="readonly")
        navigator_dropdown.pack(fill="x", pady=5)

        # Dropdown to select day
        frame_day = tk.Frame(window, pady=5)
        frame_day.pack(fill="x", padx=10)
        tk.Label(frame_day, text="Select Day:", font=("Arial", 12)).pack(anchor="w")
        day_var = tk.StringVar()
        day_dropdown = ttk.Combobox(frame_day, textvariable=day_var,
                                    values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], state="readonly")
        day_dropdown.pack(fill="x", pady=5)

        # "Take Off" Checkbox
        frame_take_off = tk.Frame(window, pady=5)
        frame_take_off.pack(fill="x", padx=10)
        take_off_var = tk.BooleanVar()
        take_off_checkbox = tk.Checkbutton(frame_take_off, text="Take Off for the Day", variable=take_off_var,
                                           font=("Arial", 12))
        take_off_checkbox.pack(anchor="w")

        # Start and End Time Inputs
        frame_time = tk.Frame(window, pady=5)
        frame_time.pack(fill="x", padx=10)
        tk.Label(frame_time, text="Start Time (HH:MM AM/PM):", font=("Arial", 12)).pack(anchor="w")
        start_time_entry = tk.Entry(frame_time, state="normal")
        start_time_entry.pack(fill="x", pady=5)

        tk.Label(frame_time, text="End Time (HH:MM AM/PM):", font=("Arial", 12)).pack(anchor="w")
        end_time_entry = tk.Entry(frame_time, state="normal")
        end_time_entry.pack(fill="x", pady=5)

        # Toggle time fields based on "Take Off" selection
        def toggle_time_fields():
            if take_off_var.get():
                start_time_entry.config(state="disabled")
                end_time_entry.config(state="disabled")
            else:
                start_time_entry.config(state="normal")
                end_time_entry.config(state="normal")

        take_off_var.trace_add("write", lambda *args: toggle_time_fields())

        # Update Button
        def update_availability():
            navigator_name = navigator_var.get()
            day = day_var.get()
            take_off = take_off_var.get()
            start_time = start_time_entry.get()
            end_time = end_time_entry.get()

            if not navigator_name or not day:
                messagebox.showerror("Error", "Please select a navigator and a day.")
                return

            for navigator in self.main.schedule.navigators:
                if navigator.name == navigator_name:
                    if take_off:
                        navigator.availability[day] = []
                        messagebox.showinfo("Success", f"{navigator_name} is marked as unavailable on {day}.")
                    else:
                        if not start_time or not end_time:
                            messagebox.showerror("Error", "Please provide valid start and end times.")
                            return
                        navigator.availability[day] = [(start_time, end_time)]
                        messagebox.showinfo("Success",
                                            f"{navigator_name}'s availability updated for {day}:\n{start_time} - {end_time}")
                    break

            window.destroy()

        tk.Button(window, text="Update Schedule", font=("Arial", 12), command=update_availability).pack(pady=20)

    def add_navigator_window(self):
        window = tk.Toplevel(self.root)
        window.title("Add Navigator")

        tk.Label(window, text="Navigator Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(window)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(window, text="Availability (day,start,end):").grid(row=1, column=0, padx=5, pady=5)
        availability_entry = tk.Entry(window)
        availability_entry.grid(row=1, column=1, padx=5, pady=5)

        def add_navigator():
            name = name_entry.get().strip()
            availability_str = availability_entry.get().strip()

            if not name or not availability_str:
                messagebox.showerror("Error", "All fields are required!")
                return

            availability = {}
            try:
                for entry in availability_str.split(";"):
                    day, start, end = entry.split(",")
                    if day not in availability:
                        availability[day] = []
                    availability[day].append((start.strip(), end.strip()))
            except ValueError:
                messagebox.showerror("Error", "Invalid availability format!")
                return

            self.main.add_navigator(name, availability)
            messagebox.showinfo("Success", f"Navigator '{name}' added successfully!")
            window.destroy()

        tk.Button(window, text="Add", command=add_navigator).grid(row=2, column=0, columnspan=2, pady=10)

    def view_availabilities(self):
        window = tk.Toplevel(self.root)
        window.title("Navigator Availabilities")
        window.geometry("600x400")  # Set a reasonable window size

        # Add a label for the title
        tk.Label(
            window,
            text="Navigator Availabilities",
            font=("Arial", 16, "bold"),
            pady=10
        ).pack()

        # Scrollable Text Area
        text_frame = tk.Frame(window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(text_frame)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling
        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")

        # Bind to both canvas and frame for cross-platform compatibility
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # For Windows and Linux
        canvas.bind_all("<Button-4>", on_mouse_wheel)  # For Linux (alternative scroll up)
        canvas.bind_all("<Button-5>", on_mouse_wheel)  # For Linux (alternative scroll down)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display navigator availabilities
        availabilities = self.main.schedule.display_all_availabilities()
        for name, days in availabilities.items():
            # Navigator Name
            navigator_label = tk.Label(
                scrollable_frame,
                text=f"{name}:",
                font=("Arial", 14, "bold"),
                anchor="w",
                justify="left"
            )
            navigator_label.pack(fill="x", pady=(10, 0))  # Add spacing above each navigator's name

            # Day and Time
            for day, times in days.items():
                times_text = ", ".join([f"{start} to {end}" for start, end in times]) if times else "Unavailable"
                day_label = tk.Label(
                    scrollable_frame,
                    text=f"  {day}: {times_text}",
                    font=("Arial", 12),
                    anchor="w",
                    justify="left"
                )
                day_label.pack(fill="x", padx=10)  # Add indentation for the days

    def input_walk_in_tours_window(self):
        window = tk.Toplevel(self.root)
        window.title("Input Walk-In Tours")

        tk.Label(window, text="Input Walk-In Tours for Each Day", font=("Arial", 14, "bold")).pack(pady=10)

        tour_inputs = {}
        for day in self.main.tour_scheduler.tours:
            day_frame = tk.Frame(window, pady=5)
            day_frame.pack(fill="x", padx=10)

            tk.Label(day_frame, text=f"{day}:", font=("Arial", 12)).pack(side="left", padx=5)
            tour_inputs[day] = {}

            for time in self.main.tour_scheduler.tours[day]:
                time_frame = tk.Frame(day_frame, padx=5)
                time_frame.pack(side="left")

                tk.Label(time_frame, text=f"{time}:", font=("Arial", 10)).pack(side="left")
                combo = ttk.Combobox(time_frame, values=["yes", "no"], width=5)
                combo.set("yes")  # Default value set to "yes"
                combo.pack(side="left", padx=5)
                tour_inputs[day][time] = combo

        def save_walk_in_tours():
            for day, times in tour_inputs.items():
                for time, combo in times.items():
                    user_input = combo.get().strip().lower()
                    if user_input == "yes":
                        self.main.tour_scheduler.tours[day][time] = "Pending"
                    elif user_input == "no":
                        self.main.tour_scheduler.tours[day][time] = None
                    else:
                        messagebox.showerror("Error", f"Invalid input for {day} at {time}")
                        return

            messagebox.showinfo("Success", "Walk-In Tours saved successfully!")
            window.destroy()

        tk.Button(window, text="Save Walk-In Tours", command=save_walk_in_tours).pack(pady=10)

    def input_group_tours_window(self):
        window = tk.Toplevel(self.root)
        window.title("Input Group Tours")
        window.geometry("600x500")  # Set a reasonable window size

        # Add a title label
        tk.Label(
            window,
            text="Input Group Tours for Each Day",
            font=("Arial", 16, "bold"),
            pady=10
        ).pack()

        # Scrollable Frame Setup
        frame_container = tk.Frame(window)
        frame_container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame_container)
        scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling
        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")

        # Bind for cross-platform compatibility
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # For Windows and Linux
        canvas.bind_all("<Button-4>", on_mouse_wheel)  # Alternative scroll up for Linux
        canvas.bind_all("<Button-5>", on_mouse_wheel)  # Alternative scroll down for Linux

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add group tour input fields for each day
        group_tour_inputs = {}
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            day_frame = tk.Frame(scrollable_frame, pady=10)
            day_frame.pack(fill="both", padx=10)

            # Day Label
            tk.Label(
                day_frame,
                text=f"{day}",
                font=("Arial", 14, "bold"),
                pady=5
            ).pack(anchor="w")

            group_tour_inputs[day] = []

            # Input fields for up to 2 group tours per day
            for i in range(2):  # Assuming up to 2 group tours per day
                group_frame = tk.Frame(day_frame, padx=10, pady=5, relief="ridge", borderwidth=2)
                group_frame.pack(fill="x", pady=5)

                # Group Tour Header
                tk.Label(
                    group_frame,
                    text=f"Group Tour {i + 1}:",
                    font=("Arial", 12, "bold"),
                    pady=5
                ).grid(row=0, column=0, columnspan=2, sticky="w")

                # School Name
                tk.Label(group_frame, text="School Name:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
                school_entry = tk.Entry(group_frame, width=30)
                school_entry.grid(row=1, column=1, padx=5, pady=2)

                # Time
                tk.Label(group_frame, text="Time (e.g., 2:00 PM):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
                time_entry = tk.Entry(group_frame, width=30)
                time_entry.grid(row=2, column=1, padx=5, pady=2)

                # Number of Students
                tk.Label(group_frame, text="Number of Students:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
                students_entry = tk.Entry(group_frame, width=30)
                students_entry.grid(row=3, column=1, padx=5, pady=2)

                group_tour_inputs[day].append((school_entry, time_entry, students_entry))

        # Save Button
        def save_group_tours():
            for day, tours in group_tour_inputs.items():
                for school_entry, time_entry, students_entry in tours:
                    school = school_entry.get().strip()
                    time = time_entry.get().strip()
                    students = students_entry.get().strip()

                    if school and time and students.isdigit():
                        self.main.tour_scheduler.group_tours[day].append({
                            "school": school,
                            "time": time,
                            "students": int(students),
                            "navigators": []  # Assigned later
                        })
                    elif school or time or students:  # Partial input
                        messagebox.showerror("Error", f"Invalid data for group tour on {day}")
                        return

            messagebox.showinfo("Success", "Group Tours saved successfully!")
            window.destroy()

        tk.Button(
            window,
            text="Save Group Tours",
            font=("Arial", 12),
            command=save_group_tours
        ).pack(pady=10)

    def assign_tours(self):
        self.main.tour_scheduler.assign_tours()
        messagebox.showinfo("Success", "Tours assigned successfully!")

    def view_weekly_tours(self):
        window = tk.Toplevel(self.root)
        window.title("Weekly Tours Schedule")
        window.geometry("700x500")  # Set a reasonable initial size

        # Add a title label
        tk.Label(
            window,
            text="Weekly Tours Schedule",
            font=("Arial", 16, "bold"),
            pady=10
        ).pack()

        # Scrollable Frame Setup
        frame_container = tk.Frame(window)
        frame_container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame_container)
        scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling
        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")

        # Bind for cross-platform compatibility
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # For Windows and Linux
        canvas.bind_all("<Button-4>", on_mouse_wheel)  # Alternative scroll up for Linux
        canvas.bind_all("<Button-5>", on_mouse_wheel)  # Alternative scroll down for Linux

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display weekly tours
        weekly_tours = self.main.tour_scheduler.tours
        group_tours = self.main.tour_scheduler.group_tours

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            # Day Header
            day_label = tk.Label(
                scrollable_frame,
                text=f"{day}:",
                font=("Arial", 14, "bold"),
                pady=5
            )
            day_label.pack(anchor="w")

            # Collect all tours for the day (walk-in and group tours)
            daily_tours = []

            # Add walk-in tours
            for time, navigator in weekly_tours[day].items():
                if navigator:
                    daily_tours.append((time, f"{time}: {navigator}"))
                else:
                    daily_tours.append((time, f"{time}: Unassigned"))

            # Add group tours
            for group in group_tours[day]:
                navigators = ", ".join(group["navigators"]) if group["navigators"] else "Unassigned"
                daily_tours.append((group["time"],
                                    f"{group['time']}: {group['school']} with {group['students']} students (Navigators: {navigators})"))

            # Sort all tours by time
            daily_tours.sort(key=lambda x: datetime.strptime(x[0], "%I:%M %p"))

            # Display sorted tours
            for _, description in daily_tours:
                tour_label = tk.Label(
                    scrollable_frame,
                    text=f"    {description}",
                    font=("Arial", 12),
                    anchor="w",
                    justify="left"
                )
                tour_label.pack(anchor="w", padx=20)  # Indented for clarity

            # Add spacing between days
            tk.Label(scrollable_frame, text="").pack()  # Blank line for spacing

        # Make text read-only
        def disable_scrolling(event):
            pass  # No text area to disable here, just for compatibility if needed.

    def view_tour_counts(self):
        window = tk.Toplevel(self.root)
        window.title("Tour Counts")
        window.geometry("500x400")  # Increased default window size for better readability

        # Add a title label
        tk.Label(
            window,
            text="Tour Counts for Navigators",
            font=("Arial", 16, "bold"),
            pady=10
        ).pack()

        # Add a frame to display tour counts
        count_frame = tk.Frame(window, padx=10, pady=10)
        count_frame.pack(fill="both", expand=True)

        # Display navigator tour counts
        for navigator in self.main.schedule.navigators:
            count_label = tk.Label(
                count_frame,
                text=f"{navigator.name}: {navigator.tour_count} tours assigned",
                font=("Arial", 12),
                anchor="w",
                pady=5
            )
            count_label.pack(anchor="w", padx=10)  # Indented for clarity


if __name__ == "__main__":
    main = Main()

    # Add some sample navigators
    main.add_navigator("Sanaa", {
        "Monday": [("9:00 AM", "5:00 PM")],
        "Tuesday": [("9:00 AM", "12:00 PM")],
        "Wednesday": [("3:00 PM", "5:00 PM")],
        "Thursday": [("9:00 AM", "5:00 PM")]
    })

    main.add_navigator("Damir", {
        "Wednesday": [("9:00 AM", "5:00 PM")],
        "Thursday": [("9:00 AM", "12:00 PM")],
        "Friday": [("9:00 AM", "5:00 PM")]
    })

    main.add_navigator("Emily", {
        "Monday": [("9:00 AM", "12:00 PM")],
        "Wednesday": [("9:00 AM", "5:00 PM")],
        "Friday": [("9:00 AM", "5:00 PM")]
    })

    main.add_navigator("Tanim", {
        "Thursday": [("9:00 AM", "5:00 PM")],
        "Friday": [("9:00 AM", "5:00 PM")]
    })

    main.add_navigator("Donara", {
        "Monday": [("10:30 AM", "5:00 PM")],
        "Wednesday": [("10:00 AM", "5:00 PM")]
    })

    main.add_navigator("Mousa", {
        "Monday": [("9:00 AM", "11:00 AM")],
        "Tuesday": [("9:00 AM", "11:00 AM")],
        "Wednesday": [("9:00 AM", "11:00 AM")],
        "Thursday": [("9:00 AM", "11:00 AM")]
    })

    main.add_navigator("Dior", {
        "Tuesday": [("9:30 AM", "3:00 PM")],
        "Friday": [("10:00 AM", "3:00 PM")]
    })

    main.add_navigator("Mike", {
        "Tuesday": [("12:00 PM", "5:00 PM")]
    })

    root = tk.Tk()
    app = TourSchedulerGUI(root, main)
    root.mainloop()
