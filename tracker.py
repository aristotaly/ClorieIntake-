import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import datetime
import csv
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
import os
import sys


class DataEntry:
    """Class representing a single data entry."""

    def __init__(self, date, weight, calories, picture_path=None):
        self.date = date  # Date string in '%Y-%m-%d' format
        self.weight = weight
        self.calories = calories
        self.picture_path = picture_path


class DataRepository:
    """Class handling data storage and retrieval."""

    def __init__(self, csv_file_path, json_file_path):
        self.csv_file_path = csv_file_path
        self.json_file_path = json_file_path

    def load_data(self):
        """Load data from CSV file if exists; else from JSON file and copy to CSV."""
        if os.path.exists(self.csv_file_path):
            data = self._load_from_csv()
        elif os.path.exists(self.json_file_path):
            data = self._load_from_json()
            self._save_to_csv(data)
        else:
            data = []
        return data

    def save_data(self, data):
        """Save data to CSV file."""
        self._save_to_csv(data)

    def _load_from_csv(self):
        """Load data from CSV file."""
        data = []
        with open(self.csv_file_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                date_str = self._parse_date(row["date"])
                if date_str is None:
                    continue  # Skip entries with invalid date formats
                data.append(
                    DataEntry(
                        date=date_str,
                        weight=float(row["weight"]),
                        calories=int(row["calories"]),
                        picture_path=row.get("picture_path") or None,
                    )
                )
        return data

    def _load_from_json(self):
        """Load data from JSON file."""
        data = []
        with open(self.json_file_path, "r") as file:
            json_data = json.load(file)
            for entry in json_data:
                date_str = self._parse_date(entry["date"])
                if date_str is None:
                    continue  # Skip entries with invalid date formats
                data.append(
                    DataEntry(
                        date=date_str,
                        weight=entry["weight"],
                        calories=entry["calories"],
                        picture_path=entry.get("picture_path"),
                    )
                )
        return data

    def _save_to_csv(self, data):
        """Save data to CSV file."""
        fieldnames = ["date", "weight", "calories", "picture_path"]
        with open(self.csv_file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in data:
                writer.writerow(
                    {
                        "date": entry.date,
                        "weight": entry.weight,
                        "calories": entry.calories,
                        "picture_path": entry.picture_path or "",
                    }
                )

    def _parse_date(self, date_str):
        """Parse date string and convert to '%Y-%m-%d' format."""
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                date_obj = datetime.datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        messagebox.showwarning(
            "Invalid Date Format",
            f"Date '{date_str}' does not match expected formats. Entry will be skipped.",
        )
        return None


class WeightTrackerApp:
    """Main application class for the Weight Tracker."""

    def __init__(self, data_repository):
        self.data_repository = data_repository
        self.data = self.data_repository.load_data()
        self.picture_path = None

        self.root = tk.Tk()
        self.root.title("Weight Tracker")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.create_menu()
        self.create_input_frame()
        self.create_date_range_selector()
        self.create_entries_frame()

        self.root.mainloop()

    def create_menu(self):
        """Create the menu bar."""
        menu_bar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def show_about(self):
        """Display the 'About' dialog."""
        messagebox.showinfo(
            "About",
            "Weight Tracker App\nVersion 1.0\nDeveloped by OpenAI's ChatGPT",
        )

    def create_input_frame(self):
        """Create the input frame for adding new entries."""
        input_frame = ttk.LabelFrame(self.root, text="Add New Entry")
        input_frame.pack(fill="x", padx=10, pady=5)

        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)
        input_frame.columnconfigure(3, weight=1)

        ttk.Label(input_frame, text="Date:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.date_entry = DateEntry(input_frame, date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Weight (kg):").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.weight_entry = ttk.Entry(input_frame)
        self.weight_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.weight_entry.insert(0, "0.0")

        ttk.Label(input_frame, text="Calorie Intake:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.calories_entry = ttk.Entry(input_frame)
        self.calories_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.calories_entry.insert(0, "0")

        select_picture_button = ttk.Button(
            input_frame, text="Select Picture", command=self.select_picture
        )
        select_picture_button.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        CreateToolTip(select_picture_button, "Attach a picture to this entry.")

        submit_button = ttk.Button(
            input_frame, text="Submit", command=self.submit_entry
        )
        submit_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        CreateToolTip(submit_button, "Submit the entry.")

        show_graph_button = ttk.Button(
            input_frame, text="Show Graph", command=self.show_graph
        )
        show_graph_button.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        CreateToolTip(show_graph_button, "Display the weight and calorie graph.")

    def create_date_range_selector(self):
        """Create the date range selector for filtering entries."""
        date_range_frame = ttk.Frame(self.root)
        date_range_frame.pack(fill="x", padx=10, pady=5)

        date_range_frame.columnconfigure(1, weight=1)
        date_range_frame.columnconfigure(3, weight=1)

        ttk.Label(date_range_frame, text="Start Date:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.start_date_entry = DateEntry(date_range_frame, date_pattern="yyyy-mm-dd")
        self.start_date_entry.set_date(datetime.date.today() - datetime.timedelta(days=7))
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(date_range_frame, text="End Date:").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.end_date_entry = DateEntry(date_range_frame, date_pattern="yyyy-mm-dd")
        self.end_date_entry.set_date(datetime.date.today())
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        update_button = ttk.Button(
            date_range_frame, text="Update", command=self.update_display
        )
        update_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        CreateToolTip(update_button, "Update the entries and graph based on date range.")

    def create_entries_frame(self):
        """Create the frame that displays entries."""
        self.entries_frame = ttk.LabelFrame(self.root, text="Entries")
        self.entries_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.display_entries()

    def select_picture(self):
        """Open a file dialog to select a picture."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png"), ("All Files", "*.*")]
        )
        if file_path:
            self.picture_path = file_path
            messagebox.showinfo(
                "Picture Selected", "Picture has been selected successfully."
            )

    def submit_entry(self):
        """Submit a new data entry or update an existing one."""
        try:
            date = self.date_entry.get_date().strftime("%Y-%m-%d")
            weight = float(self.weight_entry.get())
            calories = int(self.calories_entry.get())

            new_entry = DataEntry(date, weight, calories, self.picture_path)

            # Check if an entry with the same date exists
            existing_entry = next(
                (entry for entry in self.data if entry.date == date), None
            )
            if existing_entry:
                # Replace existing entry
                self.data[self.data.index(existing_entry)] = new_entry
                message = "Entry updated successfully!"
            else:
                # Add new entry
                self.data.append(new_entry)
                message = "Entry added successfully!"

            self.data_repository.save_data(self.data)

            self.weight_entry.delete(0, tk.END)
            self.calories_entry.delete(0, tk.END)
            self.weight_entry.insert(0, "0.0")
            self.calories_entry.insert(0, "0")
            self.picture_path = None

            messagebox.showinfo("Success", message)
            self.display_entries()
        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Please enter valid numbers for weight and calories."
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_entries(self):
        """Display data entries within the selected date range."""
        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        filtered_data = self.get_filtered_data()

        if not filtered_data:
            ttk.Label(self.entries_frame, text="No entries to display.").pack(pady=10)
            return

        # Sort entries by date, latest first
        filtered_data.sort(
            key=lambda x: datetime.datetime.strptime(x.date, "%Y-%m-%d"), reverse=True
        )

        for entry in filtered_data:
            frame = ttk.Frame(self.entries_frame)
            frame.pack(fill="x", pady=5)

            date_label = ttk.Label(frame, text=entry.date, width=15)
            date_label.pack(side=tk.LEFT, padx=5)

            weight_label = ttk.Label(frame, text=f"{entry.weight} kg", width=15)
            weight_label.pack(side=tk.LEFT, padx=5)

            calories_label = ttk.Label(frame, text=f"{entry.calories} cal", width=15)
            calories_label.pack(side=tk.LEFT, padx=5)

            if entry.picture_path and os.path.exists(entry.picture_path):
                image = Image.open(entry.picture_path)
                image.thumbnail((50, 50))
                photo = ImageTk.PhotoImage(image)
                picture_label = ttk.Label(frame, image=photo)
                picture_label.image = photo
                picture_label.pack(side=tk.LEFT, padx=5)
                picture_label.bind(
                    "<Button-1>",
                    lambda event, path=entry.picture_path: self.show_full_picture(
                        path
                    ),
                )
                CreateToolTip(picture_label, "Click to view full image.")

            # Edit and Delete Icons
            edit_button = ttk.Button(
                frame,
                text="⚙️",
                command=lambda e=entry: self.edit_entry(e),
                width=2,
            )
            edit_button.pack(side=tk.LEFT, padx=5)
            CreateToolTip(edit_button, "Edit this entry.")

            delete_button = ttk.Button(
                frame,
                text="🗑️",
                command=lambda e=entry: self.delete_entry(e),
                width=2,
            )
            delete_button.pack(side=tk.LEFT, padx=5)
            CreateToolTip(delete_button, "Delete this entry.")

    def get_filtered_data(self):
        """Get data filtered by the selected date range."""
        try:
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()
            if start_date > end_date:
                messagebox.showerror(
                    "Invalid Date Range", "Start date cannot be after end date."
                )
                return []
        except Exception as e:
            messagebox.showerror("Error", f"Invalid date selection: {e}")
            return []

        filtered_data = []
        for entry in self.data:
            entry_date = datetime.datetime.strptime(entry.date, "%Y-%m-%d").date()
            if start_date <= entry_date <= end_date:
                filtered_data.append(entry)

        return filtered_data

    def show_full_picture(self, path):
        """Display the full picture in a new window with comparison feature."""
        if not os.path.exists(path):
            messagebox.showerror(
                "File Not Found", "The selected image file does not exist."
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Full Picture")
        window.resizable(True, True)

        main_frame = ttk.Frame(window)
        main_frame.pack(fill="both", expand=True)

        # Left Image Viewer
        left_viewer = ImageViewer(main_frame, path)
        left_viewer.pack(side=tk.LEFT, padx=2, pady=2, expand=True, fill=tk.BOTH)

        # Split View Icon
        split_view_button = ttk.Button(
            main_frame, text="🗔", command=lambda: self.enable_split_view(window, path)
        )
        split_view_button.pack(side=tk.TOP, padx=5, pady=5)
        CreateToolTip(split_view_button, "Enable split view to compare images.")

        def on_close():
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_close)

    def enable_split_view(self, parent_window, current_image_path):
        """Enable split view to compare two images with zoom and pan."""
        comparison_window = tk.Toplevel(parent_window)
        comparison_window.title("Compare Pictures")
        comparison_window.resizable(True, True)

        main_frame = ttk.Frame(comparison_window)
        main_frame.pack(fill="both", expand=True)

        left_viewer = ImageViewer(main_frame, current_image_path)
        left_viewer.pack(side=tk.LEFT, padx=2, pady=2, expand=True, fill=tk.BOTH)

        right_viewer = ImageViewer(main_frame)
        right_viewer.pack(side=tk.RIGHT, padx=2, pady=2, expand=True, fill=tk.BOTH)

        # Thumbnail Gallery
        thumbnail_frame = ttk.Frame(comparison_window)
        thumbnail_frame.pack(fill="x", padx=5, pady=5)

        scrollbar = ttk.Scrollbar(thumbnail_frame, orient=tk.HORIZONTAL)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        canvas = tk.Canvas(
            thumbnail_frame, height=120, scrollregion=(0, 0, 1000, 120)
        )
        canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        canvas.configure(xscrollcommand=scrollbar.set)
        scrollbar.configure(command=canvas.xview)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Load Thumbnails with Date and Weight
        for entry in self.data:
            if entry.picture_path and os.path.exists(entry.picture_path):
                thumb_frame = ttk.Frame(inner_frame)
                thumb_frame.pack(side=tk.LEFT, padx=5)

                thumb_image = Image.open(entry.picture_path)
                thumb_image.thumbnail((80, 80))
                thumb_photo = ImageTk.PhotoImage(thumb_image)
                thumb_label = ttk.Label(thumb_frame, image=thumb_photo)
                thumb_label.image = thumb_photo
                thumb_label.pack()
                thumb_label.bind(
                    "<Button-1>",
                    lambda event, path=entry.picture_path: right_viewer.load_image(
                        path
                    ),
                )

                # Display date and weight below thumbnail
                info_label = ttk.Label(
                    thumb_frame, text=f"{entry.date}\n{entry.weight} kg"
                )
                info_label.pack()

                CreateToolTip(
                    thumb_label, f"Date: {entry.date}\nWeight: {entry.weight} kg"
                )

    def show_graph(self):
        """Display a consolidated graph of weight and calorie intake."""
        window = tk.Toplevel(self.root)
        window.title("Weight and Calorie Graph")
        window.geometry("900x600")
        window.resizable(True, True)

        # Date Range Selector in Graph Window
        date_range_frame = ttk.Frame(window)
        date_range_frame.pack(fill="x", padx=10, pady=5)

        date_range_frame.columnconfigure(1, weight=1)
        date_range_frame.columnconfigure(3, weight=1)

        ttk.Label(date_range_frame, text="Start Date:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        graph_start_date_entry = DateEntry(
            date_range_frame, date_pattern="yyyy-mm-dd"
        )
        graph_start_date_entry.set_date(self.start_date_entry.get_date())
        graph_start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(date_range_frame, text="End Date:").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        graph_end_date_entry = DateEntry(date_range_frame, date_pattern="yyyy-mm-dd")
        graph_end_date_entry.set_date(self.end_date_entry.get_date())
        graph_end_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        update_button = ttk.Button(
            date_range_frame, text="Update", command=lambda: update_graph()
        )
        update_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        CreateToolTip(update_button, "Update the graph based on date range.")

        # Download PDF Button
        download_pdf_button = ttk.Button(
            date_range_frame,
            text="Download PDF",
            command=lambda: self.download_pdf(fig),
        )
        download_pdf_button.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        CreateToolTip(download_pdf_button, "Download the graph as a PDF file.")

        # Figure and Canvas Setup
        fig, ax1 = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        def update_graph():
            try:
                start_date = graph_start_date_entry.get_date()
                end_date = graph_end_date_entry.get_date()
                if start_date > end_date:
                    messagebox.showerror(
                        "Invalid Date Range", "Start date cannot be after end date."
                    )
                    ax1.clear()
                    canvas.draw()
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Invalid date selection: {e}")
                ax1.clear()
                canvas.draw()
                return

            filtered_data = [
                entry
                for entry in self.data
                if start_date
                <= datetime.datetime.strptime(entry.date, "%Y-%m-%d").date()
                <= end_date
            ]

            if not filtered_data:
                messagebox.showinfo(
                    "No Data", "No data available for the selected date range."
                )
                ax1.clear()
                canvas.draw()
                return

            dates = [
                datetime.datetime.strptime(entry.date, "%Y-%m-%d")
                for entry in filtered_data
            ]
            weights = [entry.weight for entry in filtered_data]
            calories = [entry.calories for entry in filtered_data]

            # Sort data by date
            dates, weights, calories = zip(*sorted(zip(dates, weights, calories)))

            ax1.clear()
            ax1.plot(dates, weights, color="blue", marker="o", label="Weight")
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Weight (kg)", color="blue")
            ax1.tick_params(axis="y", labelcolor="blue")
            ax1.grid(True)

            ax2 = ax1.twinx()
            ax2.bar(dates, calories, color="red", alpha=0.3, width=0.8, label="Calories")
            ax2.set_ylabel("Calories", color="red")
            ax2.tick_params(axis="y", labelcolor="red")

            # Adjust x-axis date formatting
            fig.autofmt_xdate(rotation=45)
            ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax1.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))

            fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
            fig.tight_layout(rect=[0, 0, 1, 0.95])

            canvas.draw()

        def on_close():
            plt.close(fig)
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_close)

        # Initial graph rendering
        update_graph()

    def download_pdf(self, fig):
        """Download the current graph as a PDF file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Save Graph as PDF",
        )
        if file_path:
            try:
                fig.savefig(file_path, format="pdf")
                messagebox.showinfo("Success", "Graph has been saved as PDF successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {e}")

    def update_display(self):
        """Update the entries when date range changes."""
        self.display_entries()

    def edit_entry(self, entry):
        """Open a modal window to edit an existing entry, including picture."""
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Entry")
        edit_window.grab_set()

        ttk.Label(edit_window, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        date_entry = DateEntry(edit_window, date_pattern="yyyy-mm-dd")
        date_entry.set_date(datetime.datetime.strptime(entry.date, "%Y-%m-%d"))
        date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Weight (kg):").grid(
            row=1, column=0, padx=5, pady=5
        )
        weight_entry = ttk.Entry(edit_window)
        weight_entry.insert(0, str(entry.weight))
        weight_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Calorie Intake:").grid(
            row=2, column=0, padx=5, pady=5
        )
        calories_entry = ttk.Entry(edit_window)
        calories_entry.insert(0, str(entry.calories))
        calories_entry.grid(row=2, column=1, padx=5, pady=5)

        picture_frame = ttk.Frame(edit_window)
        picture_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        if entry.picture_path and os.path.exists(entry.picture_path):
            image = Image.open(entry.picture_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)
            picture_label = ttk.Label(picture_frame, image=photo)
            picture_label.image = photo
            picture_label.pack()

            def remove_picture():
                entry.picture_path = None
                picture_label.destroy()
                remove_button.destroy()

            remove_button = ttk.Button(
                picture_frame, text="Remove Picture", command=remove_picture
            )
            remove_button.pack()
        else:
            ttk.Label(picture_frame, text="No picture attached.").pack()

        def change_picture():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.jpg;*.jpeg;*.png"), ("All Files", "*.*")]
            )
            if file_path:
                entry.picture_path = file_path
                messagebox.showinfo(
                    "Picture Selected", "Picture has been selected successfully."
                )

        change_picture_button = ttk.Button(
            edit_window, text="Change Picture", command=change_picture
        )
        change_picture_button.grid(row=4, column=0, padx=5, pady=5)

        def save_changes():
            try:
                new_date = date_entry.get_date().strftime("%Y-%m-%d")
                new_weight = float(weight_entry.get())
                new_calories = int(calories_entry.get())

                # Check if date has changed and conflicts with existing entries
                if new_date != entry.date and any(
                    e.date == new_date for e in self.data if e != entry
                ):
                    messagebox.showerror(
                        "Date Conflict", "An entry with this date already exists."
                    )
                    return

                # Update entry
                entry.date = new_date
                entry.weight = new_weight
                entry.calories = new_calories

                self.data_repository.save_data(self.data)
                messagebox.showinfo("Success", "Entry updated successfully.")
                self.display_entries()
                edit_window.destroy()
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter valid numbers for weight and calories.",
                )
            except Exception as e:
                messagebox.showerror("Error", str(e))

        save_button = ttk.Button(edit_window, text="Save", command=save_changes)
        save_button.grid(row=4, column=1, padx=5, pady=5)
        cancel_button = ttk.Button(
            edit_window, text="Cancel", command=edit_window.destroy
        )
        cancel_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def delete_entry(self, entry):
        """Delete an existing entry after confirmation."""
        response = messagebox.askyesno(
            "Confirm Deletion", "Are you sure you want to delete this entry?"
        )
        if response:
            self.data.remove(entry)
            self.data_repository.save_data(self.data)
            messagebox.showinfo("Success", "Entry deleted successfully.")
            self.display_entries()

    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


class ImageViewer(tk.Canvas):
    """Canvas widget for displaying images with zoom and pan functionality."""

    def __init__(self, parent, image_path=None):
        super().__init__(parent, background="black", highlightthickness=0)
        self.parent = parent
        self.bind("<ButtonPress-1>", self.move_start)
        self.bind("<B1-Motion>", self.move_move)
        self.bind("<MouseWheel>", self.zoom)
        self.bind("<Button-4>", self.zoom)  # For Linux with wheel up
        self.bind("<Button-5>", self.zoom)  # For Linux with wheel down
        self.image = None
        self.tk_image = None
        self.scale = 1.0
        self.translate_x = 0
        self.translate_y = 0
        if image_path:
            self.load_image(image_path)

    def load_image(self, image_path):
        """Load and display the image."""
        pil_image = Image.open(image_path)
        self.image = pil_image
        self.scale = 1.0
        self.translate_x = 0
        self.translate_y = 0
        self.redraw()

    def move_start(self, event):
        """Remember previous coordinates for scrolling with the mouse."""
        self.scan_mark(event.x, event.y)

    def move_move(self, event):
        """Drag (move) canvas to the new position."""
        self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event):
        """Zoom in/out with mouse wheel."""
        # Respond to Linux or Windows wheel event
        if event.num == 4 or event.delta > 0:
            factor = 1.1
        elif event.num == 5 or event.delta < 0:
            factor = 0.9
        else:
            factor = 1.0

        self.scale *= factor
        self.redraw()

    def redraw(self):
        """Redraw the image on the canvas."""
        self.delete("all")
        width, height = self.image.size
        scaled_width = int(width * self.scale)
        scaled_height = int(height * self.scale)
        resized_image = self.image.resize((scaled_width, scaled_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)
        self.create_image(self.translate_x, self.translate_y, anchor="nw", image=self.tk_image)
        self.configure(scrollregion=self.bbox("all"))


class CreateToolTip:
    """Create a tooltip for a given widget."""

    def __init__(self, widget, text="widget info"):
        self.waittime = 500  # milliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.id = None
        self.top = None

    def enter(self, _=None):
        self.schedule()

    def leave(self, _=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        _id = self.id
        self.id = None
        if _id:
            self.widget.after_cancel(_id)

    def showtip(self, _=None):
        x = y = 0
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.top = tk.Toplevel(self.widget)
        self.top.wm_overrideredirect(True)
        self.top.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(
            self.top,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            wraplength=self.wraplength,
        )
        label.pack(ipadx=1)

    def hidetip(self):
        top = self.top
        self.top = None
        if top:
            top.destroy()


if __name__ == "__main__":
    csv_file = "weight_data.csv"
    json_file = "weight_data.json"
    data_repository = DataRepository(csv_file, json_file)
    WeightTrackerApp(data_repository)
