import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Import your existing services and models
from alphasignal.services.service import (
    create_wallet,
    fund,
    get_swap_quote,
    get_token_value,
    get_wallet_value,
    add_coin_command,
    remove_coin_command,
    process_coins,
    swap_tokens,
)
from dotenv import load_dotenv


def async_run(coroutine):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(coroutine)
    else:
        loop.run_until_complete(coroutine)


class TokenManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AlphaSignal Token Manager")
        self.geometry("800x600")
        self.configure(bg="#1e1e2e")

        self.wallet = None

        # Styling
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure(
            "TLabel", font=("Helvetica", 12), foreground="white", background="#1e1e2e"
        )
        style.configure("TEntry", font=("Helvetica", 12))

        self.create_widgets()

    def create_widgets(self):
        # Wallet Management Section
        wallet_frame = ttk.LabelFrame(self, text="Wallet Management", padding=20)
        wallet_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ttk.Label(wallet_frame, text="Wallet Public Key:").grid(
            row=0, column=0, sticky="w"
        )
        self.wallet_key_var = tk.StringVar()
        self.wallet_key_entry = ttk.Entry(
            wallet_frame, textvariable=self.wallet_key_var, width=50, state="readonly"
        )
        self.wallet_key_entry.grid(row=0, column=1, pady=10)

        create_wallet_btn = ttk.Button(
            wallet_frame, text="Create Wallet", command=self.create_wallet
        )
        create_wallet_btn.grid(row=1, column=0, pady=10, sticky="w")

        fund_wallet_btn = ttk.Button(
            wallet_frame, text="Fund Wallet", command=self.fund_wallet
        )
        fund_wallet_btn.grid(row=1, column=1, pady=10, sticky="w")

        ttk.Button(
            wallet_frame, text="Get Wallet Value", command=self.get_wallet_value
        ).grid(row=2, column=0, pady=10, sticky="w")

        # Token Management Section
        token_frame = ttk.LabelFrame(self, text="Token Management", padding=20)
        token_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        ttk.Label(token_frame, text="Token Mint Address:").grid(
            row=0, column=0, sticky="w"
        )
        self.token_mint_var = tk.StringVar()
        self.token_mint_entry = ttk.Entry(
            token_frame, textvariable=self.token_mint_var, width=50
        )
        self.token_mint_entry.grid(row=0, column=1, pady=10)

        get_value_btn = ttk.Button(
            token_frame, text="Get Token Value", command=self.get_token_value
        )
        get_value_btn.grid(row=1, column=0, pady=10, sticky="w")

        add_token_btn = ttk.Button(
            token_frame, text="Add Token", command=self.add_token
        )
        add_token_btn.grid(row=1, column=1, pady=10, sticky="w")

        # Swap Section
        swap_frame = ttk.LabelFrame(self, text="Token Swap", padding=20)
        swap_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        ttk.Label(swap_frame, text="From Token Mint:").grid(row=0, column=0, sticky="w")
        self.from_token_var = tk.StringVar()
        self.from_token_entry = ttk.Entry(
            swap_frame, textvariable=self.from_token_var, width=50
        )
        self.from_token_entry.grid(row=0, column=1, pady=10)

        ttk.Label(swap_frame, text="To Token Mint:").grid(row=1, column=0, sticky="w")
        self.to_token_var = tk.StringVar()
        self.to_token_entry = ttk.Entry(
            swap_frame, textvariable=self.to_token_var, width=50
        )
        self.to_token_entry.grid(row=1, column=1, pady=10)

        ttk.Label(swap_frame, text="Amount:").grid(row=2, column=0, sticky="w")
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(
            swap_frame, textvariable=self.amount_var, width=50
        )
        self.amount_entry.grid(row=2, column=1, pady=10)

        swap_btn = ttk.Button(swap_frame, text="Swap Tokens", command=self.swap_tokens)
        swap_btn.grid(row=3, column=0, pady=10, sticky="w")

        get_quote_btn = ttk.Button(swap_frame, text="Get Quote", command=self.get_quote)
        get_quote_btn.grid(row=3, column=1, pady=10, sticky="w")

    def create_wallet(self):
        try:
            self.wallet = create_wallet()
            self.wallet_key_var.set(self.wallet.wallet.public_key)
            messagebox.showinfo("Success", "Wallet created successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create wallet: {e}")

    def fund_wallet(self):
        if not self.wallet:
            messagebox.showwarning(
                "Warning", "No wallet found. Please create a wallet first."
            )
            return

        amount = simpledialog.askfloat("Fund Wallet", "Enter amount to fund:")
        if amount:
            async_run(fund(amount, self.wallet))
            messagebox.showinfo("Success", "Wallet funded successfully!")

    def get_wallet_value(self):
        if not self.wallet:
            messagebox.showwarning(
                "Warning", "No wallet found. Please create a wallet first."
            )
            return

        async_run(self.fetch_wallet_value())

    async def fetch_wallet_value(self):
        try:
            wallet_value = await get_wallet_value(self.wallet)
            tokens_info = "\n".join(
                [
                    f"{token.token_name or 'Unknown'}: {token.balance} tokens (${token.value:.2f})"
                    for token in (wallet_value.wallet_tokens or [])
                ]
            )
            messagebox.showinfo(
                "Wallet Value",
                f"Total Value: ${wallet_value.total_value:.2f}\n{tokens_info}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch wallet value: {e}")

    def get_token_value(self):
        mint_address = self.token_mint_var.get()
        if not mint_address:
            messagebox.showwarning("Warning", "Please enter a token mint address.")
            return

        async_run(self.fetch_token_value(mint_address))

    async def fetch_token_value(self, mint_address):
        try:
            token_value = await get_token_value(mint_address)
            messagebox.showinfo("Token Value", f"Token Price: ${token_value.price}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch token value: {e}")

    def get_quote(self):
        from_token = self.from_token_var.get()
        to_token = self.to_token_var.get()
        amount = float(self.amount_var.get())

        if not (from_token and to_token and amount):
            messagebox.showwarning(
                "Warning", "Please fill out all fields to get a quote."
            )
            return

        async_run(self.fetch_quote(from_token, to_token, amount))

    async def fetch_quote(self, from_token, to_token, amount):
        try:
            quote = await get_swap_quote(from_token, to_token, float(amount))
            messagebox.showinfo(
                "Swap Quote",
                f"Input: {quote.from_token_amt} tokens (~${quote.from_token_amt_usd:.2f})\n"
                f"Output: {quote.to_token_amt} tokens (~${quote.to_token_amt_usd:.2f})\n"
                f"Conversion Rate: {quote.conversion_rate} tokens per input token\n"
                f"Price Impact: {quote.price_impact * 100:.2f}%",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch swap quote: {e}")

    def add_token(self):
        async_run(add_coin_command())

    def swap_tokens(self):
        from_token = self.from_token_var.get()
        to_token = self.to_token_var.get()
        amount = self.amount_var.get()

        if not (from_token and to_token and amount):
            messagebox.showwarning(
                "Warning", "Please fill out all fields for the swap."
            )
            return

        try:
            async_run(swap_tokens(from_token, to_token, float(amount), self.wallet))
            messagebox.showinfo("Success", "Tokens swapped successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Swap failed: {e}")


if __name__ == "__main__":
    load_dotenv()
    app = TokenManagerApp()
    app.mainloop()
