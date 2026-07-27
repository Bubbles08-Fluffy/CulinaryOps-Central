import customtkinter as ctk


class BaseCrudPage(ctk.CTkFrame):
    """
    Base page used by all CRUD management screens.
    Child classes (Vendors, Employees, etc.) add their own
    form fields, tables, and database logic.
    """

    def __init__(self, parent, title, description):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.create_header(title, description)

    def create_header(self, title, description):
        """Creates the page title and description."""

        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(15, 10),
        )

        header.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        description_label = ctk.CTkLabel(
            header,
            text=description,
            text_color="gray60",
            font=ctk.CTkFont(size=14),
        )
        description_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(4, 0),
        )