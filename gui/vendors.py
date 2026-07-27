import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from database.vendors import (
    add_vendor,
    delete_vendor,
    get_all_vendors,
    search_vendors,
    update_vendor,
)


class VendorsPage(ctk.CTkFrame):
    """
    Vendor Management page.

    Allows the user to:
    - View vendors
    - Search vendors
    - Add vendors
    - Edit vendors
    - Delete vendors
    """

    def __init__(
        self,
        parent,
        status_callback=None,
        dashboard_callback=None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.status_callback = status_callback
        self.dashboard_callback = dashboard_callback
        self.selected_vendor_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.create_title_section()
        self.create_form_section()
        self.create_search_section()
        self.create_table_section()

        self.load_vendors()

    # ---------------------------------------------------------
    # PAGE LAYOUT
    # ---------------------------------------------------------

    def create_title_section(self):
        title_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        title_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(10, 5),
        )

        title_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            title_frame,
            text="Vendor Management",
            font=ctk.CTkFont(
                family="Arial",
                size=26,
                weight="bold",
            ),
            anchor="w",
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text=(
                "Add, update, search, and manage dining service vendors."
            ),
            font=ctk.CTkFont(
                family="Arial",
                size=13,
            ),
            text_color="gray60",
            anchor="w",
        )
        subtitle_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(2, 0),
        )

    def create_form_section(self):
        form_card = ctk.CTkFrame(
            self,
            corner_radius=12,
        )
        form_card.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10,
            pady=10,
        )

        for column in range(4):
            form_card.grid_columnconfigure(column, weight=1)

        form_title = ctk.CTkLabel(
            form_card,
            text="Vendor Information",
            font=ctk.CTkFont(
                family="Arial",
                size=18,
                weight="bold",
            ),
        )
        form_title.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=20,
            pady=(15, 10),
        )

        vendor_name_label = ctk.CTkLabel(
            form_card,
            text="Vendor Name *",
            anchor="w",
        )
        vendor_name_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(20, 10),
            pady=(5, 2),
        )

        contact_name_label = ctk.CTkLabel(
            form_card,
            text="Contact Name",
            anchor="w",
        )
        contact_name_label.grid(
            row=1,
            column=1,
            sticky="w",
            padx=10,
            pady=(5, 2),
        )

        phone_label = ctk.CTkLabel(
            form_card,
            text="Phone Number",
            anchor="w",
        )
        phone_label.grid(
            row=1,
            column=2,
            sticky="w",
            padx=10,
            pady=(5, 2),
        )

        email_label = ctk.CTkLabel(
            form_card,
            text="Email Address",
            anchor="w",
        )
        email_label.grid(
            row=1,
            column=3,
            sticky="w",
            padx=(10, 20),
            pady=(5, 2),
        )

        self.vendor_name_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Example: Fresh Foods Co.",
            height=38,
        )
        self.vendor_name_entry.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=(20, 10),
            pady=(0, 10),
        )

        self.contact_name_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Contact person's name",
            height=38,
        )
        self.contact_name_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=10,
            pady=(0, 10),
        )

        self.phone_number_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="334-555-0000",
            height=38,
        )
        self.phone_number_entry.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=10,
            pady=(0, 10),
        )

        self.email_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="vendor@example.com",
            height=38,
        )
        self.email_entry.grid(
            row=2,
            column=3,
            sticky="ew",
            padx=(10, 20),
            pady=(0, 10),
        )

        button_frame = ctk.CTkFrame(
            form_card,
            fg_color="transparent",
        )
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
            text="Add Vendor",
            width=130,
            height=38,
            command=self.handle_add_vendor,
        )
        self.add_button.pack(
            side="left",
            padx=(0, 8),
        )

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update Vendor",
            width=130,
            height=38,
            state="disabled",
            command=self.handle_update_vendor,
        )
        self.update_button.pack(
            side="left",
            padx=8,
        )

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Form",
            width=110,
            height=38,
            fg_color="gray45",
            hover_color="gray35",
            command=self.clear_form,
        )
        self.clear_button.pack(
            side="left",
            padx=8,
        )

        self.delete_button = ctk.CTkButton(
            button_frame,
            text="Delete Vendor",
            width=130,
            height=38,
            fg_color="#B3261E",
            hover_color="#8C1D18",
            state="disabled",
            command=self.handle_delete_vendor,
        )
        self.delete_button.pack(
            side="right",
        )

    def create_search_section(self):
        search_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
        )
        search_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 10),
        )

        search_frame.grid_columnconfigure(1, weight=1)

        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Vendors",
            font=ctk.CTkFont(
                family="Arial",
                size=15,
                weight="bold",
            ),
        )
        search_label.grid(
            row=0,
            column=0,
            padx=(18, 10),
            pady=15,
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=(
                "Search by vendor, contact, phone, or email..."
            ),
            height=38,
        )
        self.search_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10,
            pady=15,
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.handle_live_search,
        )

        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            command=self.handle_search,
        )
        search_button.grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
        )

        show_all_button = ctk.CTkButton(
            search_frame,
            text="Show All",
            width=90,
            height=38,
            fg_color="gray45",
            hover_color="gray35",
            command=self.show_all_vendors,
        )
        show_all_button.grid(
            row=0,
            column=3,
            padx=(5, 18),
            pady=15,
        )

    def create_table_section(self):
        table_card = ctk.CTkFrame(
            self,
            corner_radius=12,
        )
        table_card.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10),
        )

        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(1, weight=1)

        table_header = ctk.CTkFrame(
            table_card,
            fg_color="transparent",
        )
        table_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=18,
            pady=(15, 8),
        )

        table_header.grid_columnconfigure(0, weight=1)

        table_title = ctk.CTkLabel(
            table_header,
            text="Current Vendors",
            font=ctk.CTkFont(
                family="Arial",
                size=18,
                weight="bold",
            ),
        )
        table_title.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.vendor_count_label = ctk.CTkLabel(
            table_header,
            text="0 vendors",
            text_color="gray60",
        )
        self.vendor_count_label.grid(
            row=0,
            column=1,
            sticky="e",
        )

        table_container = tk.Frame(
            table_card,
            bg="#2B2B2B",
        )
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
            "vendor_id",
            "vendor_name",
            "contact_name",
            "phone_number",
            "email",
        )

        self.vendor_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Vendor.Treeview",
        )

        self.vendor_table.heading(
            "vendor_id",
            text="ID",
        )
        self.vendor_table.heading(
            "vendor_name",
            text="Vendor Name",
        )
        self.vendor_table.heading(
            "contact_name",
            text="Contact Name",
        )
        self.vendor_table.heading(
            "phone_number",
            text="Phone Number",
        )
        self.vendor_table.heading(
            "email",
            text="Email Address",
        )

        self.vendor_table.column(
            "vendor_id",
            width=55,
            minwidth=45,
            anchor="center",
            stretch=False,
        )
        self.vendor_table.column(
            "vendor_name",
            width=200,
            minwidth=150,
            anchor="w",
        )
        self.vendor_table.column(
            "contact_name",
            width=170,
            minwidth=130,
            anchor="w",
        )
        self.vendor_table.column(
            "phone_number",
            width=135,
            minwidth=110,
            anchor="center",
        )
        self.vendor_table.column(
            "email",
            width=220,
            minwidth=160,
            anchor="w",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.vendor_table.yview,
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=self.vendor_table.xview,
        )

        self.vendor_table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.vendor_table.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        self.vendor_table.bind(
            "<<TreeviewSelect>>",
            self.handle_table_selection,
        )

        self.vendor_table.bind(
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
            "Vendor.Treeview",
            background="#FFFFFF",
            foreground="#1F1F1F",
            fieldbackground="#FFFFFF",
            rowheight=34,
            borderwidth=0,
            font=("Arial", 12),
        )

        style.configure(
            "Vendor.Treeview.Heading",
            background="#1F6AA5",
            foreground="#FFFFFF",
            relief="flat",
            font=("Arial", 12, "bold"),
            padding=(8, 8),
        )

        style.map(
            "Vendor.Treeview",
            background=[
                ("selected", "#3B8ED0"),
            ],
            foreground=[
                ("selected", "#FFFFFF"),
            ],
        )

        style.map(
            "Vendor.Treeview.Heading",
            background=[
                ("active", "#175A8C"),
            ],
        )

        style.layout(
            "Vendor.Treeview",
            [
                (
                    "Vendor.Treeview.treearea",
                    {
                        "sticky": "nswe",
                    },
                )
            ],
        )

        self.option_add(
            "*Vendor.Treeview*font",
            ("Arial", 12),
        )

    # ---------------------------------------------------------
    # DATABASE AND TABLE FUNCTIONS
    # ---------------------------------------------------------

    def load_vendors(self, vendors=None):
        try:
            if vendors is None:
                vendors = get_all_vendors()

            self.clear_table()

            for vendor in vendors:
                vendor_id = vendor[0]
                vendor_name = vendor[1] or ""
                contact_name = vendor[2] or ""
                phone_number = vendor[3] or ""
                email = vendor[4] or ""

                self.vendor_table.insert(
                    "",
                    "end",
                    values=(
                        vendor_id,
                        vendor_name,
                        contact_name,
                        phone_number,
                        email,
                    ),
                )

            total = len(vendors)
            label_text = (
                f"{total} vendor"
                if total == 1
                else f"{total} vendors"
            )

            self.vendor_count_label.configure(
                text=label_text,
            )

        except Exception as error:
            messagebox.showerror(
                "Vendor Error",
                f"Unable to load vendors.\n\n{error}",
            )

            self.update_status(
                "Unable to load vendor records."
            )

    def clear_table(self):
        for item in self.vendor_table.get_children():
            self.vendor_table.delete(item)

    def refresh_vendor_page(self):
        self.load_vendors()
        self.refresh_dashboard()
        self.update_status(
            "Vendor records refreshed."
        )

    # ---------------------------------------------------------
    # ADD, UPDATE, DELETE
    # ---------------------------------------------------------

    def handle_add_vendor(self):
        vendor_name = self.vendor_name_entry.get()
        contact_name = self.contact_name_entry.get()
        phone_number = self.phone_number_entry.get()
        email = self.email_entry.get()

        success, message = add_vendor(
            vendor_name,
            contact_name,
            phone_number,
            email,
        )

        if success:
            messagebox.showinfo(
                "Vendor Added",
                message,
            )

            self.clear_form()
            self.load_vendors()
            self.refresh_dashboard()

            self.update_status(
                "Vendor added successfully."
            )

        else:
            messagebox.showwarning(
                "Unable to Add Vendor",
                message,
            )

            self.update_status(
                "Vendor was not added."
            )

    def handle_update_vendor(self):
        if self.selected_vendor_id is None:
            messagebox.showwarning(
                "No Vendor Selected",
                "Select a vendor from the table first.",
            )
            return

        vendor_name = self.vendor_name_entry.get()
        contact_name = self.contact_name_entry.get()
        phone_number = self.phone_number_entry.get()
        email = self.email_entry.get()

        success, message = update_vendor(
            self.selected_vendor_id,
            vendor_name,
            contact_name,
            phone_number,
            email,
        )

        if success:
            messagebox.showinfo(
                "Vendor Updated",
                message,
            )

            self.clear_form()
            self.load_vendors()
            self.refresh_dashboard()

            self.update_status(
                "Vendor updated successfully."
            )

        else:
            messagebox.showwarning(
                "Unable to Update Vendor",
                message,
            )

            self.update_status(
                "Vendor was not updated."
            )

    def handle_delete_vendor(self):
        if self.selected_vendor_id is None:
            messagebox.showwarning(
                "No Vendor Selected",
                "Select a vendor from the table first.",
            )
            return

        vendor_name = self.vendor_name_entry.get().strip()

        confirmation = messagebox.askyesno(
            "Delete Vendor",
            (
                f"Are you sure you want to delete "
                f"'{vendor_name}'?\n\n"
                "This action cannot be undone."
            ),
        )

        if not confirmation:
            self.update_status(
                "Vendor deletion canceled."
            )
            return

        success, message = delete_vendor(
            self.selected_vendor_id
        )

        if success:
            messagebox.showinfo(
                "Vendor Deleted",
                message,
            )

            self.clear_form()
            self.load_vendors()
            self.refresh_dashboard()

            self.update_status(
                "Vendor deleted successfully."
            )

        else:
            messagebox.showwarning(
                "Unable to Delete Vendor",
                message,
            )

            self.update_status(
                "Vendor was not deleted."
            )

    # ---------------------------------------------------------
    # SEARCH FUNCTIONS
    # ---------------------------------------------------------

    def handle_search(self):
        keyword = self.search_entry.get()

        try:
            vendors = search_vendors(keyword)
            self.load_vendors(vendors)

            if keyword.strip():
                self.update_status(
                    f"Vendor search completed for '{keyword.strip()}'."
                )
            else:
                self.update_status(
                    "All vendor records displayed."
                )

        except Exception as error:
            messagebox.showerror(
                "Search Error",
                f"Unable to search vendors.\n\n{error}",
            )

    def handle_live_search(self, event=None):
        keyword = self.search_entry.get()

        try:
            vendors = search_vendors(keyword)
            self.load_vendors(vendors)

        except Exception:
            pass

    def show_all_vendors(self):
        self.search_entry.delete(0, "end")
        self.load_vendors()

        self.update_status(
            "All vendor records displayed."
        )

    # ---------------------------------------------------------
    # TABLE SELECTION
    # ---------------------------------------------------------

    def handle_table_selection(self, event=None):
        selected_items = self.vendor_table.selection()

        if not selected_items:
            return

        selected_item = selected_items[0]
        values = self.vendor_table.item(
            selected_item,
            "values",
        )

        if not values:
            return

        self.selected_vendor_id = int(values[0])

        self.vendor_name_entry.delete(0, "end")
        self.vendor_name_entry.insert(0, values[1])

        self.contact_name_entry.delete(0, "end")
        self.contact_name_entry.insert(0, values[2])

        self.phone_number_entry.delete(0, "end")
        self.phone_number_entry.insert(0, values[3])

        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, values[4])

        self.add_button.configure(
            state="disabled"
        )
        self.update_button.configure(
            state="normal"
        )
        self.delete_button.configure(
            state="normal"
        )

        self.update_status(
            f"Vendor selected: {values[1]}"
        )

    def handle_table_double_click(self, event=None):
        self.handle_table_selection()

        self.vendor_name_entry.focus_set()

    # ---------------------------------------------------------
    # FORM UTILITIES
    # ---------------------------------------------------------

    def clear_form(self):
        self.selected_vendor_id = None

        self.vendor_name_entry.delete(0, "end")
        self.contact_name_entry.delete(0, "end")
        self.phone_number_entry.delete(0, "end")
        self.email_entry.delete(0, "end")

        for item in self.vendor_table.selection():
            self.vendor_table.selection_remove(item)

        self.add_button.configure(
            state="normal"
        )
        self.update_button.configure(
            state="disabled"
        )
        self.delete_button.configure(
            state="disabled"
        )

        self.vendor_name_entry.focus_set()

        self.update_status(
            "Vendor form cleared."
        )

    # ---------------------------------------------------------
    # CALLBACKS TO MAIN APPLICATION
    # ---------------------------------------------------------

    def update_status(self, message):
        if callable(self.status_callback):
            self.status_callback(message)

    def refresh_dashboard(self):
        if callable(self.dashboard_callback):
            self.dashboard_callback()