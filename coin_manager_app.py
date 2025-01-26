import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from alphasignal.models.enums import SellMode, SellType
from alphasignal.services.coin_manager import CoinManager
from alphasignal.services.service import (
    get_tracked_coins_command,
    load_wallet,
    get_wallet_value,
)

# Load environment variables
load_dotenv()

# Global wallet manager
wallet = load_wallet()
coin_manager = CoinManager()


class AddCoinDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🎃 Add Coin 🎃")
        self.geometry("500x600")
        self.configure(bg="#1a1a1a")

        self.parent = parent
        self.selected_token = None
        self.tracking_balance = 0
        self.sell_mode = None
        self.sell_value = 0
        self.sell_type = None

        # Step 1: Display available tokens
        self.create_token_selection_section()

    async def load_tokens(self):
        self.tokens = await wallet.get_tokens()

        if not self.tokens:
            tk.messagebox.showerror("Error", "No tokens found in the wallet.")
            self.destroy()
            return

        # Populate tokens in the dropdown
        token_names = [
            f"{token.token_name or 'Unknown'} (Balance: {token.balance})"
            for token in self.tokens
        ]
        self.token_dropdown["values"] = token_names

    def create_token_selection_section(self):
        tk.Label(
            self,
            text="Select a Token",
            font=("Chiller", 18),
            fg="#ff7518",
            bg="#1a1a1a",
        ).pack(pady=10)

        self.token_dropdown = ttk.Combobox(self, state="readonly", width=40)
        self.token_dropdown.pack(pady=10)

        tk.Button(
            self,
            text="Next",
            command=self.on_token_selected,
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=10)

        self.after(100, lambda: asyncio.create_task(self.load_tokens()))

    def on_token_selected(self):
        selected_index = self.token_dropdown.current()
        if selected_index == -1:
            tk.messagebox.showerror("Error", "Please select a token.")
            return

        self.selected_token = self.tokens[selected_index]
        self.display_remaining_balance_section()

    def display_remaining_balance_section(self):
        # Clear previous widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Fetch remaining balance
        remaining_balance = coin_manager.get_remaining_trackable_balance(
            self.selected_token.mint_address, self.selected_token.balance
        )

        if remaining_balance <= 0:
            tk.messagebox.showerror("Error", "No balance available for tracking.")
            self.destroy()
            return

        tk.Label(
            self,
            text=f"Remaining Balance: {remaining_balance}",
            font=("Chiller", 18),
            fg="#ff7518",
            bg="#1a1a1a",
        ).pack(pady=10)

        tk.Label(
            self,
            text="Enter Tracking Amount",
            font=("Chiller", 18),
            fg="#ff7518",
            bg="#1a1a1a",
        ).pack(pady=10)

        tk.Button(
            self,
            text="Enter Percentage",
            command=lambda: self.enter_tracking_amount(remaining_balance, True),
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=5)

        tk.Button(
            self,
            text="Enter Custom Amount",
            command=lambda: self.enter_tracking_amount(remaining_balance, False),
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=5)

    def enter_tracking_amount(self, remaining_balance, is_percentage):
        # Clear previous widgets
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(
            self,
            text="Enter Tracking Amount",
            font=("Chiller", 18),
            fg="#ff7518",
            bg="#1a1a1a",
        ).pack(pady=10)

        amount_entry = tk.Entry(self, font=("Chiller", 14))
        amount_entry.pack(pady=10)

        def on_submit():
            try:
                amount = float(amount_entry.get())
                if is_percentage:
                    amount = (amount / 100) * remaining_balance
                if amount > remaining_balance:
                    raise ValueError("Exceeds remaining balance.")
                self.tracking_balance = amount
                self.display_sell_mode_section()
            except ValueError as e:
                tk.messagebox.showerror("Error", str(e))

        tk.Button(
            self,
            text="Submit",
            command=on_submit,
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=10)

    def display_sell_mode_section(self):
        # Clear previous widgets
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(
            self,
            text="Select Sell Mode",
            font=("Chiller", 18),
            fg="#ff7518",
            bg="#1a1a1a",
        ).pack(pady=10)

        tk.Button(
            self,
            text="Time-Based",
            command=lambda: self.enter_sell_value(SellMode.TIME_BASED),
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=5)

        tk.Button(
            self,
            text="Stop-Loss",
            command=lambda: self.enter_sell_value(SellMode.STOP_LOSS),
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=5)

    def enter_sell_value(self, sell_mode):
        self.sell_mode = sell_mode

        # Clear previous widgets
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(
            self,
            text="Enter Sell Value",
            font=("Chiller", 18),
            fg="#ff7518",
            bg="#1a1a1a",
        ).pack(pady=10)

        value_entry = tk.Entry(self, font=("Chiller", 14))
        value_entry.pack(pady=10)

        def on_submit():
            try:
                value = float(value_entry.get())
                self.sell_value = value
                self.display_sell_type_section()
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid value entered.")

        tk.Button(
            self,
            text="Submit",
            command=on_submit,
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=10)

    def display_sell_type_section(self):
        # Clear previous widgets
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(
            self,
            text="Select Sell Type",
            font=("Chiller", 18),
            fg="#ff7518",
            bg="#1a1a1a",
        ).pack(pady=10)

        tk.Button(
            self,
            text="USDC",
            command=lambda: self.finalize_add_coin(SellType.USDC),
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=5)

        tk.Button(
            self,
            text="SOL",
            command=lambda: self.finalize_add_coin(SellType.SOL),
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
        ).pack(pady=5)

    def finalize_add_coin(self, sell_type):
        self.sell_type = sell_type

        coin_manager.add_coin(
            mint_address=self.selected_token.mint_address,
            sell_mode=self.sell_mode,
            sell_value=self.sell_value,
            sell_type=self.sell_type,
            balance=self.tracking_balance,
            tokens=self.tokens,
        )

        tk.messagebox.showinfo("Success", "Coin added successfully!")
        self.destroy()


class WalletApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎃 Spooky Wallet Tracker 🎃")
        self.geometry("1000x600")
        self.configure(bg="#1a1a1a")  # Black background for Halloween

        # Halloween header
        self.header_label = tk.Label(
            self,
            text="🎃 Halloween Wallet & Tracked Coins 🎃",
            font=("Chiller", 24, "bold"),
            fg="#ff7518",  # Pumpkin orange
            bg="#1a1a1a",
        )
        self.header_label.pack(pady=10)

        # Wallet summary table
        self.create_wallet_table()
        self.total_label = tk.Label(
            self,
            text="Total Wallet Value: $0.00",
            font=("Chiller", 18, "bold"),
            fg="#ff7518",
            bg="#1a1a1a",
        )
        self.total_label.pack(pady=10)

        # Tracked coins table
        self.create_tracked_coins_table()

        # Start the asyncio loop for updating data
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.refresh_data())

    def create_wallet_table(self):
        """Creates the wallet summary table."""
        self.wallet_table_frame = tk.Frame(self, bg="#1a1a1a")
        self.wallet_table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#2e2e2e",
            foreground="white",
            fieldbackground="#2e2e2e",
            rowheight=25,
            font=("Comic Sans MS", 10),
        )
        style.configure(
            "Treeview.Heading",
            font=("Chiller", 14, "bold"),
            foreground="#ff7518",
            background="#2e2e2e",
        )

        self.wallet_tree = ttk.Treeview(
            self.wallet_table_frame,
            columns=("Token Name", "Mint Address", "Balance", "Value"),
            show="headings",
        )
        self.wallet_tree.heading("Token Name", text="👻 Token Name 👻")
        self.wallet_tree.heading("Mint Address", text="🕸 Mint Address 🕸")
        self.wallet_tree.heading("Balance", text="🦇 Balance 🦇")
        self.wallet_tree.heading("Value", text="💀 Value (USD) 💀")

        self.wallet_tree.column("Token Name", width=150, anchor="center")
        self.wallet_tree.column("Mint Address", width=250, anchor="center")
        self.wallet_tree.column("Balance", width=100, anchor="center")
        self.wallet_tree.column("Value", width=100, anchor="center")

        self.wallet_tree.pack(fill="both", expand=True)

    def create_tracked_coins_table(self):
        """Creates the tracked coins table."""
        self.tracked_table_frame = tk.Frame(self, bg="#1a1a1a")
        self.tracked_table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tracked_tree = ttk.Treeview(
            self.tracked_table_frame,
            columns=(
                "Mint Address",
                "Balance",
                "Sell Mode",
                "Sell Trigger Value",
                "Sell Type",
                "Last Max",
                "Remove",
            ),
            show="headings",
        )
        self.tracked_tree.heading("Mint Address", text="🕷 Mint Address 🕷")
        self.tracked_tree.heading("Balance", text="🎃 Balance 🎃")
        self.tracked_tree.heading("Sell Mode", text="🦇 Sell Mode 🦇")
        self.tracked_tree.heading("Sell Trigger Value", text="👻 Sell Trigger Value 👻")
        self.tracked_tree.heading("Sell Type", text="💀 Sell Type 💀")
        self.tracked_tree.heading("Last Max", text="🕸 Last Max 🕸")
        self.tracked_tree.heading("Remove", text="❌ Remove ❌")

        self.tracked_tree.column("Mint Address", width=200, anchor="center")
        self.tracked_tree.column("Balance", width=100, anchor="center")
        self.tracked_tree.column("Sell Mode", width=150, anchor="center")
        self.tracked_tree.column("Sell Trigger Value", width=150, anchor="center")
        self.tracked_tree.column("Sell Type", width=100, anchor="center")
        self.tracked_tree.column("Last Max", width=100, anchor="center")
        self.tracked_tree.column("Remove", width=100, anchor="center")

        self.tracked_tree.pack(fill="both", expand=True)

        # Add a button below the Tracked Coins table
        add_coin_button = tk.Button(
            self,
            text="Add Coin 🎃",
            command=lambda: AddCoinDialog(self),
            bg="#ff7518",
            fg="#1a1a1a",
            font=("Chiller", 14),
            relief="raised",
        )
        add_coin_button.pack(pady=10)

    async def update_wallet_data(self):
        """Fetch and display the latest wallet data."""
        wallet_value = await get_wallet_value(wallet)
        total_value = wallet_value.total_value
        wallet_tokens = wallet_value.wallet_tokens or []

        # Clear the wallet table
        for row in self.wallet_tree.get_children():
            self.wallet_tree.delete(row)

        # Populate the wallet table
        for token in wallet_tokens:
            self.wallet_tree.insert(
                "",
                "end",
                values=(
                    token.token_name or "Unknown",
                    token.mint_address,
                    f"{token.balance:.2f}",
                    f"${token.value:.2f}",
                ),
            )

        # Update the total value label
        self.total_label.config(text=f"Total Wallet Value: ${total_value:.2f}")

    async def update_tracked_coins_data(self):
        """Fetch and display the latest tracked coins data."""
        tracked_coins = get_tracked_coins_command()

        # Clear the tracked coins table
        for row in self.tracked_tree.get_children():
            self.tracked_tree.delete(row)

        # Populate the tracked coins table
        for coin in tracked_coins:
            self.tracked_tree.insert(
                "",
                "end",
                values=(
                    coin.mint_address,
                    f"{coin.balance:.2f}",
                    coin.sell_mode.value,
                    f"{coin.sell_value:.2f}",
                    coin.sell_type.value,
                    f"{coin.last_price_max:.2f}",
                    "❌ Remove",
                ),
                tags=(coin.id,),  # Tag row with the coin ID
            )

        # Bind click events to handle the remove button
        self.tracked_tree.bind("<Button-1>", self.handle_remove_click)

    def handle_remove_click(self, event):
        """Handle clicks on the 'Remove' column."""
        # Identify which column and row were clicked
        region = self.tracked_tree.identify("region", event.x, event.y)
        column = self.tracked_tree.identify_column(event.x)
        row_id = self.tracked_tree.identify_row(event.y)

        # Check if the click was in the "Remove" column
        if region == "cell" and column == "#7" and row_id:
            # Get the coin ID from the row tags
            coin_id = self.tracked_tree.item(row_id, "tags")[0]
            self.remove_tracked_coin(coin_id)

    def remove_tracked_coin(self, coin_id: str):
        """Remove a tracked coin and refresh the table."""
        try:
            coin_manager.remove_coin(coin_id)
            messagebox.showinfo("Success", "Coin removed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove coin: {e}")

    async def refresh_data(self):
        """Refresh wallet and tracked coins data every 30 seconds."""
        while True:
            await self.update_wallet_data()
            await self.update_tracked_coins_data()
            await asyncio.sleep(10)

    def run(self):
        """Run the Tkinter main loop and asyncio event loop together."""
        self.loop.run_until_complete(self._tk_loop())

    async def _tk_loop(self):
        """A coroutine to keep updating the Tkinter UI."""
        while True:
            self.update()
            await asyncio.sleep(0.01)


def main():
    # Start the event loop
    app = WalletApp()
    app.run()


if __name__ == "__main__":
    main()
