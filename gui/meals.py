import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from database.meals import (
    add_meal,
    delete_meal,
    get_all_meals,
    search_meals,
    update_meal,
)
from gui.base_crud_page import BaseCrudPage


class MealsPage(BaseCrudPage):
    """Meal Count Management page."""

    def __init__(
        self,
        parent,
        status_callback=None,
        dashboard_callback=None,
    ):
        super().__init__(
            parent,
            title="Meal Count Management",
            description="Add, update, search, and manage daily meal totals.",
        )

        self.status_callback = status_callback
        self.dashboard_callback = dashboard_callback
        self.selected_meal_id = None

        self.create_form_section()
        self.create_search_section()
        self.create_table_section()
        self.load_meals()

    # ---------------------------------------------------------
    # FORM SECTION
    # ---------------------------------------------------------

    def create_form_section(self):
        form_card = ctk.CTkFrame(self, corner_radius=12)
        form_card.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=15,
            pady=(0, 10),
        )

        for column in range(4):
            form_card.grid_columnconfigure(column, weight=1)

        ctk.CTkLabel(
            form_card,
            text="Daily Meal Information",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=20,
            pady=(15, 10),
        )

        labels = (
            "Meal Date *",
            "Breakfast Count *",
            "Lunch Count *",
            "Dinner Count *",
        )

        for column, label_text in enumerate(labels):
            ctk.CTkLabel(
                form_card,
                text=label_text,
                anchor="w",
            ).grid(
                row=1,
                column=column,
                sticky="w",
                padx=(20 if column == 0 else 10, 20 if column == 3 else 10),
                pady=(5, 2),
            )

        self.meal_date_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="YYYY-MM-DD",
            height=38,
        )
        self.breakfast_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Example: 120",
            height=38,
        )
        self.lunch_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Example: 250",
            height=38,
        )
        self.dinner_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Example: 180",
            height=38,
        )

        entries = (
            self.meal_date_entry,
            self.breakfast_entry,
            self.lunch_entry,
            self.dinner_entry,
        )

        for column, entry in enumerate(entries):
            entry.grid(
                row=2,
                column=column,
                sticky="ew",
                padx=(20 if column == 0 else 10, 20 if column == 3 else 10),
                pady=(0, 10),
            )

        button_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        button_frame.grid(
            row=3,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=20,
            pady=(5, 18),
        )

        self.add_button = ctk.CTkButton(
            button_frame,
            text="Add Meal Count",
            width=140,
            height=38,
            command=self.handle_add_meal,
        )
        self.add_button.pack(side="left", padx=(0, 8))

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update Meal Count",
            width=155,
            height=38,
            state="disabled",
            command=self.handle_update_meal,
        )
        self.update_button.pack(side="left", padx=8)

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Form",
            width=110,
            height=38,
            fg_color="gray45",
            hover_color="gray35",
            command=self.clear_form,
        )
        self.clear_button.pack(side="left", padx=8)

        self.delete_button = ctk.CTkButton(
            button_frame,
            text="Delete Meal Count",
            width=155,
            height=38,
            fg_color="#B3261E",
            hover_color="#8C1D18",
            state="disabled",
            command=self.handle_delete_meal,
        )
        self.delete_button.pack(side="right")

    # ---------------------------------------------------------
    # SEARCH SECTION
    # ---------------------------------------------------------

    def create_search_section(self):
        search_frame = ctk.CTkFrame(self, corner_radius=12)
        search_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=15,
            pady=(0, 10),
        )
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_frame,
            text="Search Meal Counts",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(
            row=0,
            column=0,
            padx=(18, 10),
            pady=15,
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by date, count, or meal record ID...",
            height=38,
        )
        self.search_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10,
            pady=15,
        )
        self.search_entry.bind("<KeyRelease>", self.handle_live_search)

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            command=self.handle_search,
        ).grid(row=0, column=2, padx=5, pady=15)

        ctk.CTkButton(
            search_frame,
            text="Show All",
            width=90,
            height=38,
            fg_color="gray45",
            hover_color="gray35",
            command=self.show_all_meals,
        ).grid(row=0, column=3, padx=(5, 18), pady=15)

    # ---------------------------------------------------------
    # TABLE SECTION
    # ---------------------------------------------------------

    def create_table_section(self):
        table_card = ctk.CTkFrame(self, corner_radius=12)
        table_card.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 15),
        )
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(1, weight=1)

        table_header = ctk.CTkFrame(table_card, fg_color="transparent")
        table_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=18,
            pady=(15, 8),
        )
        table_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            table_header,
            text="Current Meal Counts",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.meal_count_label = ctk.CTkLabel(
            table_header,
            text="0 records",
            text_color="gray60",
        )
        self.meal_count_label.grid(row=0, column=1, sticky="e")

        table_container = tk.Frame(table_card, bg="#2B2B2B")
        table_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(0, 18),
        )
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        self.configure_table_style()

        columns = (
            "meal_id",
            "meal_date",
            "breakfast_count",
            "lunch_count",
            "dinner_count",
            "total_count",
        )

        self.meal_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Meal.Treeview",
        )

        headings = {
            "meal_id": "ID",
            "meal_date": "Meal Date",
            "breakfast_count": "Breakfast",
            "lunch_count": "Lunch",
            "dinner_count": "Dinner",
            "total_count": "Daily Total",
        }

        for column_name, heading_text in headings.items():
            self.meal_table.heading(column_name, text=heading_text)

        self.meal_table.column(
            "meal_id",
            width=60,
            minwidth=50,
            anchor="center",
            stretch=False,
        )
        self.meal_table.column(
            "meal_date",
            width=150,
            minwidth=120,
            anchor="center",
        )
        self.meal_table.column(
            "breakfast_count",
            width=140,
            minwidth=110,
            anchor="center",
        )
        self.meal_table.column(
            "lunch_count",
            width=140,
            minwidth=110,
            anchor="center",
        )
        self.meal_table.column(
            "dinner_count",
            width=140,
            minwidth=110,
            anchor="center",
        )
        self.meal_table.column(
            "total_count",
            width=145,
            minwidth=115,
            anchor="center",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.meal_table.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=self.meal_table.xview,
        )

        self.meal_table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.meal_table.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.meal_table.bind(
            "<<TreeviewSelect>>",
            self.handle_table_selection,
        )
        self.meal_table.bind(
            "<Double-1>",
            self.handle_table_double_click,
        )

    def configure_table_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Meal.Treeview",
            background="#FFFFFF",
            foreground="#1F1F1F",
            fieldbackground="#FFFFFF",
            rowheight=34,
            borderwidth=0,
            font=("Arial", 12),
        )
        style.configure(
            "Meal.Treeview.Heading",
            background="#1F6AA5",
            foreground="#FFFFFF",
            relief="flat",
            font=("Arial", 12, "bold"),
            padding=(8, 8),
        )
        style.map(
            "Meal.Treeview",
            background=[("selected", "#3B8ED0")],
            foreground=[("selected", "#FFFFFF")],
        )
        style.map(
            "Meal.Treeview.Heading",
            background=[("active", "#175A8C")],
        )

    # ---------------------------------------------------------
    # DATABASE AND TABLE FUNCTIONS
    # ---------------------------------------------------------

    def load_meals(self, meals=None):
        try:
            if meals is None:
                meals = get_all_meals()

            self.clear_table()

            for meal in meals:
                breakfast = int(meal[2] or 0)
                lunch = int(meal[3] or 0)
                dinner = int(meal[4] or 0)

                self.meal_table.insert(
                    "",
                    "end",
                    values=(
                        meal[0],
                        meal[1] or "",
                        breakfast,
                        lunch,
                        dinner,
                        breakfast + lunch + dinner,
                    ),
                )

            total = len(meals)
            self.meal_count_label.configure(
                text=f"{total} record" if total == 1 else f"{total} records"
            )

        except Exception as error:
            messagebox.showerror(
                "Meal Count Error",
                f"Unable to load meal count records.\n\n{error}",
            )
            self.update_status("Unable to load meal count records.")

    def clear_table(self):
        for item in self.meal_table.get_children():
            self.meal_table.delete(item)

    # ---------------------------------------------------------
    # ADD, UPDATE, DELETE
    # ---------------------------------------------------------

    def handle_add_meal(self):
        meal_id = add_meal(
            self.meal_date_entry.get(),
            self.breakfast_entry.get(),
            self.lunch_entry.get(),
            self.dinner_entry.get(),
        )

        if meal_id:
            messagebox.showinfo("Meal Count Added", "Meal count added successfully.")
            self.clear_form()
            self.load_meals()
            self.refresh_dashboard()
        else:
            messagebox.showwarning("Unable to Add Meal Count", "Unable to Add Meal Count")

    def handle_update_meal(self):
        if self.selected_meal_id is None:
            messagebox.showwarning(
                "No Meal Count Selected",
                "Select a meal count record from the table first.",
            )
            return

        success = update_meal(
            self.selected_meal_id,
            self.meal_date_entry.get(),
            self.breakfast_entry.get(),
            self.lunch_entry.get(),
            self.dinner_entry.get(),
        )

        if success:
            messagebox.showinfo("Meal Count Updated", "Meal count updated successfully.")
            self.clear_form()
            self.load_meals()
            self.refresh_dashboard()
        else:
            messagebox.showwarning("Unable to Update Meal Count", "Unable to update meal count.")

    def handle_delete_meal(self):
        if self.selected_meal_id is None:
            messagebox.showwarning(
                "No Meal Count Selected",
                "Select a meal count record from the table first.",
            )
            return

        confirmed = messagebox.askyesno(
            "Delete Meal Count",
            "Are you sure you want to delete this meal count record?",
        )

        if not confirmed:
            return

        success = delete_meal(self.selected_meal_id)

        if success:
            messagebox.showinfo("Meal Count Deleted", "Meal count deleted successfully.")
            self.clear_form()
            self.load_meals()
            self.refresh_dashboard()
            self.update_status("Meal count record deleted successfully.")
        else:
            messagebox.showwarning("Unable to Delete Meal Count", "Unable to Delete Meal Count")

    # ---------------------------------------------------------
    # SEARCH FUNCTIONS
    # ---------------------------------------------------------

    def handle_search(self):
        keyword = self.search_entry.get().strip()
        meals = search_meals(keyword)
        self.load_meals(meals)

        if keyword:
            self.update_status(f'Meal count search completed for "{keyword}".')
        else:
            self.update_status("All meal count records displayed.")

    def handle_live_search(self, event=None):
        self.handle_search()

    def show_all_meals(self):
        self.search_entry.delete(0, "end")
        self.load_meals()
        self.update_status("All meal count records displayed.")

    # ---------------------------------------------------------
    # TABLE SELECTION
    # ---------------------------------------------------------

    def handle_table_selection(self, event=None):
        selected_items = self.meal_table.selection()
        if not selected_items:
            return

        values = self.meal_table.item(selected_items[0], "values")
        if not values:
            return

        self.selected_meal_id = int(values[0])

        entries_and_values = (
            (self.meal_date_entry, values[1]),
            (self.breakfast_entry, values[2]),
            (self.lunch_entry, values[3]),
            (self.dinner_entry, values[4]),
        )

        for entry, value in entries_and_values:
            entry.delete(0, "end")
            entry.insert(0, value)

        self.add_button.configure(state="disabled")
        self.update_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        self.update_status(f"Meal count selected for {values[1]}.")

    def handle_table_double_click(self, event=None):
        self.handle_table_selection()
        self.meal_date_entry.focus_set()

    # ---------------------------------------------------------
    # FORM UTILITIES
    # ---------------------------------------------------------

    def clear_form(self):
        self.selected_meal_id = None

        for entry in (
            self.meal_date_entry,
            self.breakfast_entry,
            self.lunch_entry,
            self.dinner_entry,
        ):
            entry.delete(0, "end")

        for item in self.meal_table.selection():
            self.meal_table.selection_remove(item)

        self.add_button.configure(state="normal")
        self.update_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        self.meal_date_entry.focus_set()
        self.update_status("Meal count form cleared.")

    # ---------------------------------------------------------
    # CALLBACKS TO MAIN APPLICATION
    # ---------------------------------------------------------

    def update_status(self, message):
        if callable(self.status_callback):
            self.status_callback(message)

    def refresh_dashboard(self):
        if callable(self.dashboard_callback):
            self.dashboard_callback()
