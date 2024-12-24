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
        window.geometry("400x400")

        tk.Label(window, text="Change Schedule for Navigator", font=("Arial", 14, "bold")).pack(pady=10)

        # Dropdown to select navigator
        tk.Label(window, text="Select Navigator:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        navigator_names = [navigator.name for navigator in self.main.schedule.navigators]
        navigator_var = tk.StringVar()
        navigator_dropdown = ttk.Combobox(window, textvariable=navigator_var, values=navigator_names, state="readonly")
        navigator_dropdown.pack(fill="x", padx=10, pady=5)

        # Dropdown to select day
        tk.Label(window, text="Select Day:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        day_var = tk.StringVar()
        day_dropdown = ttk.Combobox(window, textvariable=day_var,
                                    values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], state="readonly")
        day_dropdown.pack(fill="x", padx=10, pady=5)

        # "Take Off" Checkbox
        take_off_var = tk.BooleanVar()
        take_off_checkbox = tk.Checkbutton(window, text="Take Off for the Day", variable=take_off_var,
                                           font=("Arial", 12))
        take_off_checkbox.pack(anchor="w", padx=10, pady=5)

        # Start and End Time Inputs
        tk.Label(window, text="Start Time (HH:MM AM/PM):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        start_time_entry = tk.Entry(window, state="normal")
        start_time_entry.pack(fill="x", padx=10, pady=5)

        tk.Label(window, text="End Time (HH:MM AM/PM):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        end_time_entry = tk.Entry(window, state="normal")
        end_time_entry.pack(fill="x", padx=10, pady=5)

        # Disable/Enable Time Inputs Based on "Take Off"
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
                        # Mark navigator as unavailable
                        navigator.availability[day] = []
                        messagebox.showinfo("Success", f"{navigator_name} is marked as unavailable on {day}.")
                    else:
                        if not start_time or not end_time:
                            messagebox.showerror("Error", "Please provide valid start and end times.")
                            return
                        # Update availability
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

        text_area = tk.Text(window, wrap="word", width=60, height=20)
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        availabilities = self.main.schedule.display_all_availabilities()
        for name, days in availabilities.items():
            text_area.insert("end", f"{name}:\n")
            for day, times in days.items():
                time_str = ", ".join([f"{start} to {end}" for start, end in times])
                text_area.insert("end", f"  {day}: {time_str}\n")
            text_area.insert("end", "\n")

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

        tk.Label(window, text="Input Group Tours for Each Day", font=("Arial", 14, "bold")).pack(pady=10)

        group_tour_inputs = {}
        canvas = tk.Canvas(window)
        scroll_y = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)

        frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            day_frame = tk.Frame(frame, pady=10)
            day_frame.pack(fill="both", padx=10)

            tk.Label(day_frame, text=f"{day}", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
            group_tour_inputs[day] = []

            for i in range(2):  # Assuming up to 2 group tours per day
                group_frame = tk.Frame(day_frame, padx=10, pady=5, relief="ridge", borderwidth=2)
                group_frame.pack(fill="x", pady=5)

                tk.Label(group_frame, text=f"Group Tour {i + 1}:", font=("Arial", 10, "bold")).grid(row=0, column=0,
                                                                                                    columnspan=2,
                                                                                                    sticky="w", pady=5)

                tk.Label(group_frame, text="School Name:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
                school_entry = tk.Entry(group_frame, width=30)
                school_entry.grid(row=1, column=1, padx=5, pady=2)

                tk.Label(group_frame, text="Time (e.g., 2:00 PM):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
                time_entry = tk.Entry(group_frame, width=30)
                time_entry.grid(row=2, column=1, padx=5, pady=2)

                tk.Label(group_frame, text="Number of Students:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
                students_entry = tk.Entry(group_frame, width=30)
                students_entry.grid(row=3, column=1, padx=5, pady=2)

                group_tour_inputs[day].append((school_entry, time_entry, students_entry))

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

        tk.Button(window, text="Save Group Tours", command=save_group_tours).pack(pady=10)

    def assign_tours(self):
        self.main.tour_scheduler.assign_tours()
        messagebox.showinfo("Success", "Tours assigned successfully!")

    def view_weekly_tours(self):
        window = tk.Toplevel(self.root)
        window.title("Weekly Tours Schedule")

        text_area = tk.Text(window, wrap="word", width=80, height=30)
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        weekly_tours = self.main.tour_scheduler.tours
        group_tours = self.main.tour_scheduler.group_tours

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            text_area.insert("end", f"{day}:\n")

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
                text_area.insert("end", f"    {description}\n")

            # Add a blank line for spacing between days
            text_area.insert("end", "\n")

        # Make text read-only
        text_area.configure(state="disabled")

    def view_tour_counts(self):
        window = tk.Toplevel(self.root)
        window.title("Tour Counts")

        text_area = tk.Text(window, wrap="word", width=40, height=20)
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        for navigator in self.main.schedule.navigators:
            text_area.insert("end", f"{navigator.name}: {navigator.tour_count} tours assigned\n")


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
