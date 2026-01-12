import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List


class CurrencyAPI:
    """Class to handle all API interactions with FreeCurrencyAPI"""
    
    BASE_URL = "https://api.freecurrencyapi.com/v1"
    
    def __init__(self, api_key: str):
        """Initialize the API handler with an API key"""
        self.api_key = api_key
        self.headers = {"apikey": api_key}
    
    def get_latest_rates(self, base_currency: str = "USD", 
                        currencies: Optional[List[str]] = None) -> Optional[Dict]:
        """Fetch the latest exchange rates"""
        try:
            url = f"{self.BASE_URL}/latest"
            params = {"base_currency": base_currency}
            
            if currencies:
                params["currencies"] = ",".join(currencies)
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("Rate limit exceeded")
                return None
            else:
                print(f"API Error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    
    def get_historical_rates(self, date: str, base_currency: str = "USD",
                            currencies: Optional[List[str]] = None) -> Optional[Dict]:
        """Fetch historical exchange rates for a specific date"""
        try:
            url = f"{self.BASE_URL}/historical"
            params = {
                "date": date,
                "base_currency": base_currency
            }
            
            if currencies:
                params["currencies"] = ",".join(currencies)
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    
    def get_supported_currencies(self) -> Optional[Dict]:
        """Fetch list of all supported currencies"""
        try:
            url = f"{self.BASE_URL}/currencies"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    
    def get_status(self) -> Optional[Dict]:
        """Check API status and quota"""
        try:
            url = f"{self.BASE_URL}/status"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None


class Currency:
    """Class to represent a currency with its properties"""
    
    def __init__(self, code: str, name: str, symbol: Optional[str] = None):
        """Initialize Currency object"""
        self.code = code
        self.name = name
        self.symbol = symbol if symbol else code
    
    def __str__(self):
        """String representation of currency"""
        return f"{self.code} - {self.name}"
    
    def get_display_name(self):
        """Get formatted display name"""
        return f"{self.code} ({self.symbol}) - {self.name}"


class CurrencyConverter:
    """Class to handle currency conversion calculations"""
    
    def __init__(self, exchange_rates: Dict[str, float], base_currency: str):
        """Initialize converter with exchange rates"""
        self.exchange_rates = exchange_rates
        self.base_currency = base_currency
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        # Convert to base currency first, then to target
        if from_currency != self.base_currency:
            if from_currency in self.exchange_rates:
                amount = amount / self.exchange_rates[from_currency]
            else:
                raise ValueError(f"Rate not available for {from_currency}")
        
        # Convert from base to target currency
        if to_currency != self.base_currency:
            if to_currency in self.exchange_rates:
                amount = amount * self.exchange_rates[to_currency]
            else:
                raise ValueError(f"Rate not available for {to_currency}")
        
        return amount
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get exchange rate between two currencies
        Args:
            from_currency (str): Source currency
            to_currency (str): Target currency
        Returns:
            float: Exchange rate
        """
        return self.convert(1.0, from_currency, to_currency)


class CurrencyConverterGUI:
    """Main GUI application class for Currency Converter"""
    
    def __init__(self, root, api_key: str):
        """
        Initialize the GUI application
        Args:
            root: Tkinter root window
            api_key (str): Free Currency API key
        """
        self.root = root
        self.root.title("Currency Converter Pro")
        self.root.geometry("950x750")
        self.root.configure(bg="#f5f5f5")
        
        # Initialize API handler
        self.api = CurrencyAPI(api_key)
        
        # Data storage
        self.currencies: Dict[str, Currency] = {}
        self.exchange_rates: Dict[str, float] = {}
        self.converter: Optional[CurrencyConverter] = None
        self.base_currency = "USD"
        self.conversion_history: List[str] = []
        
        # Color scheme
        self.colors = {
            'primary': '#2E7D32',
            'secondary': '#1976D2',
            'accent': '#FF6F00',
            'bg': '#f5f5f5',
            'card': 'white',
            'text': '#212121',
            'success': '#4CAF50',
            'warning': '#FFC107'
        }
        
        self.setup_ui()
        self.load_currencies()
    
    def setup_ui(self):
        """Set up the user interface components"""
        # Header Frame
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=90)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="💱 Currency Converter Pro",
            font=("Arial", 26, "bold"),
            bg=self.colors['primary'],
            fg="white"
        )
        title_label.pack(pady=25)
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Currency Converter
        self.converter_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.converter_tab, text="  Convert  ")
        self.setup_converter_tab()
        
        # Tab 2: Exchange Rates
        self.rates_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.rates_tab, text="  Exchange Rates  ")
        self.setup_rates_tab()
        
        # Tab 3: Historical Data
        self.history_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.history_tab, text="  Historical  ")
        self.setup_history_tab()
        
        # Tab 4: Conversion History
        self.log_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.log_tab, text="  History Log  ")
        self.setup_log_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready | Loading currencies...")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#e0e0e0",
            font=("Arial", 9),
            padx=5
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_converter_tab(self):
        """Set up the main currency converter tab"""
        # Converter card
        converter_card = tk.Frame(
            self.converter_tab,
            bg=self.colors['card'],
            relief=tk.RAISED,
            bd=2
        )
        converter_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            converter_card,
            text="Convert Currency",
            font=("Arial", 18, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        title.pack(pady=20)
        
        # Amount input frame
        amount_frame = tk.Frame(converter_card, bg=self.colors['card'])
        amount_frame.pack(pady=10)
        
        amount_label = tk.Label(
            amount_frame,
            text="Amount:",
            font=("Arial", 12, "bold"),
            bg=self.colors['card']
        )
        amount_label.pack(side=tk.LEFT, padx=10)
        
        self.amount_var = tk.StringVar(value="1.00")
        amount_entry = tk.Entry(
            amount_frame,
            textvariable=self.amount_var,
            font=("Arial", 14),
            width=20,
            justify=tk.CENTER
        )
        amount_entry.pack(side=tk.LEFT, padx=10)
        amount_entry.bind('<Return>', lambda e: self.perform_conversion())
        
        # From currency frame
        from_frame = tk.Frame(converter_card, bg=self.colors['card'])
        from_frame.pack(pady=15)
        
        from_label = tk.Label(
            from_frame,
            text="From:",
            font=("Arial", 12, "bold"),
            bg=self.colors['card'],
            width=8,
            anchor=tk.E
        )
        from_label.pack(side=tk.LEFT, padx=10)
        
        self.from_currency_var = tk.StringVar()
        self.from_currency_combo = ttk.Combobox(
            from_frame,
            textvariable=self.from_currency_var,
            font=("Arial", 11),
            width=35,
            state="readonly"
        )
        self.from_currency_combo.pack(side=tk.LEFT, padx=10)
        
        # Swap button
        swap_frame = tk.Frame(converter_card, bg=self.colors['card'])
        swap_frame.pack(pady=5)
        
        swap_btn = tk.Button(
            swap_frame,
            text="⇅ Swap",
            command=self.swap_currencies,
            bg=self.colors['secondary'],
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        swap_btn.pack()
        
        # To currency frame
        to_frame = tk.Frame(converter_card, bg=self.colors['card'])
        to_frame.pack(pady=15)
        
        to_label = tk.Label(
            to_frame,
            text="To:",
            font=("Arial", 12, "bold"),
            bg=self.colors['card'],
            width=8,
            anchor=tk.E
        )
        to_label.pack(side=tk.LEFT, padx=10)
        
        self.to_currency_var = tk.StringVar()
        self.to_currency_combo = ttk.Combobox(
            to_frame,
            textvariable=self.to_currency_var,
            font=("Arial", 11),
            width=35,
            state="readonly"
        )
        self.to_currency_combo.pack(side=tk.LEFT, padx=10)
        
        # Convert button
        convert_btn = tk.Button(
            converter_card,
            text="Convert",
            command=self.perform_conversion,
            bg=self.colors['primary'],
            fg="white",
            font=("Arial", 14, "bold"),
            relief=tk.FLAT,
            padx=40,
            pady=10,
            cursor="hand2"
        )
        convert_btn.pack(pady=20)
        
        # Result frame
        result_frame = tk.Frame(
            converter_card,
            bg="#E8F5E9",
            relief=tk.SOLID,
            bd=2
        )
        result_frame.pack(fill=tk.X, padx=40, pady=20)
        
        self.result_var = tk.StringVar(value="Enter amount and select currencies")
        result_label = tk.Label(
            result_frame,
            textvariable=self.result_var,
            font=("Arial", 16, "bold"),
            bg="#E8F5E9",
            fg=self.colors['primary'],
            pady=20
        )
        result_label.pack()
        
        # Exchange rate info
        self.rate_info_var = tk.StringVar(value="")
        rate_info_label = tk.Label(
            converter_card,
            textvariable=self.rate_info_var,
            font=("Arial", 10),
            bg=self.colors['card'],
            fg="#666666"
        )
        rate_info_label.pack(pady=5)
    
    def setup_rates_tab(self):
        """Set up the exchange rates display tab"""
        # Controls frame
        controls_frame = tk.Frame(self.rates_tab, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        controls_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Base currency selection
        base_label = tk.Label(
            controls_frame,
            text="Base Currency:",
            font=("Arial", 11, "bold"),
            bg=self.colors['card']
        )
        base_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.base_currency_var = tk.StringVar(value="USD")
        base_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.base_currency_var,
            font=("Arial", 10),
            width=30,
            state="readonly"
        )
        base_combo.pack(side=tk.LEFT, padx=5, pady=10)
        self.base_combo = base_combo
        
        refresh_btn = tk.Button(
            controls_frame,
            text="🔄 Refresh Rates",
            command=self.load_exchange_rates,
            bg=self.colors['secondary'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Rates display
        rates_frame = tk.Frame(self.rates_tab, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        rates_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for rates
        columns = ('Currency', 'Code', 'Rate', 'Inverse')
        self.rates_tree = ttk.Treeview(rates_frame, columns=columns, show='headings', height=20)
        
        self.rates_tree.heading('Currency', text='Currency Name')
        self.rates_tree.heading('Code', text='Code')
        self.rates_tree.heading('Rate', text=f'Rate (1 USD =)')
        self.rates_tree.heading('Inverse', text='Inverse')
        
        self.rates_tree.column('Currency', width=250)
        self.rates_tree.column('Code', width=80)
        self.rates_tree.column('Rate', width=120)
        self.rates_tree.column('Inverse', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(rates_frame, orient=tk.VERTICAL, command=self.rates_tree.yview)
        self.rates_tree.configure(yscroll=scrollbar.set)
        
        self.rates_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def setup_history_tab(self):
        """Set up the historical data tab"""
        # Date selection frame
        date_frame = tk.Frame(self.history_tab, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        date_frame.pack(fill=tk.X, padx=20, pady=20)
        
        date_label = tk.Label(
            date_frame,
            text="Select Date:",
            font=("Arial", 11, "bold"),
            bg=self.colors['card']
        )
        date_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.hist_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(
            date_frame,
            textvariable=self.hist_date_var,
            font=("Arial", 10),
            width=12
        )
        date_entry.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Quick date buttons
        today_btn = tk.Button(
            date_frame,
            text="Today",
            command=lambda: self.set_date(0),
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        today_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        week_btn = tk.Button(
            date_frame,
            text="1 Week Ago",
            command=lambda: self.set_date(7),
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        week_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        month_btn = tk.Button(
            date_frame,
            text="1 Month Ago",
            command=lambda: self.set_date(30),
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        month_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        # Currency selection for historical data
        hist_from_label = tk.Label(
            date_frame,
            text="From:",
            font=("Arial", 10),
            bg=self.colors['card']
        )
        hist_from_label.pack(side=tk.LEFT, padx=(20, 5), pady=10)
        
        self.hist_from_var = tk.StringVar()
        hist_from_combo = ttk.Combobox(
            date_frame,
            textvariable=self.hist_from_var,
            font=("Arial", 9),
            width=12,
            state="readonly"
        )
        hist_from_combo.pack(side=tk.LEFT, padx=2, pady=10)
        self.hist_from_combo = hist_from_combo
        
        hist_to_label = tk.Label(
            date_frame,
            text="To:",
            font=("Arial", 10),
            bg=self.colors['card']
        )
        hist_to_label.pack(side=tk.LEFT, padx=5, pady=10)
        
        self.hist_to_var = tk.StringVar()
        hist_to_combo = ttk.Combobox(
            date_frame,
            textvariable=self.hist_to_var,
            font=("Arial", 9),
            width=12,
            state="readonly"
        )
        hist_to_combo.pack(side=tk.LEFT, padx=2, pady=10)
        self.hist_to_combo = hist_to_combo
        
        fetch_btn = tk.Button(
            date_frame,
            text="Fetch Historical Data",
            command=self.fetch_historical_data,
            bg=self.colors['primary'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        fetch_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Results display
        result_frame = tk.Frame(self.history_tab, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.hist_result_text = scrolledtext.ScrolledText(
            result_frame,
            font=("Courier", 10),
            height=20,
            state=tk.DISABLED,
            bg="#fafafa",
            padx=15,
            pady=15
        )
        self.hist_result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_log_tab(self):
        """Set up the conversion history log tab"""
        # Controls
        controls_frame = tk.Frame(self.log_tab, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        controls_frame.pack(fill=tk.X, padx=20, pady=20)
        
        log_label = tk.Label(
            controls_frame,
            text="Conversion History",
            font=("Arial", 14, "bold"),
            bg=self.colors['card']
        )
        log_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        clear_btn = tk.Button(
            controls_frame,
            text="Clear History",
            command=self.clear_history,
            bg=self.colors['warning'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Log display
        log_frame = tk.Frame(self.log_tab, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Courier", 10),
            height=25,
            state=tk.DISABLED,
            bg="#fafafa",
            padx=15,
            pady=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_currencies(self):
        """Load supported currencies from API"""
        self.status_var.set("Loading currencies...")
        self.root.update()
        
        data = self.api.get_supported_currencies()
        
        if data and 'data' in data:
            currency_data = data['data']
            
            for code, info in currency_data.items():
                name = info.get('name', code)
                symbol = info.get('symbol', code)
                self.currencies[code] = Currency(code, name, symbol)
            
            # Populate comboboxes
            currency_list = [f"{code} - {curr.name}" for code, curr in sorted(self.currencies.items())]
            
            self.from_currency_combo['values'] = currency_list
            self.to_currency_combo['values'] = currency_list
            self.base_combo['values'] = currency_list
            self.hist_from_combo['values'] = [code for code in sorted(self.currencies.keys())]
            self.hist_to_combo['values'] = [code for code in sorted(self.currencies.keys())]
            
            # Set defaults
            if 'USD' in self.currencies:
                self.from_currency_combo.set(f"USD - {self.currencies['USD'].name}")
                self.hist_from_var.set("USD")
            if 'EUR' in self.currencies:
                self.to_currency_combo.set(f"EUR - {self.currencies['EUR'].name}")
                self.hist_to_var.set("EUR")
            
            self.base_combo.set(f"USD - {self.currencies.get('USD', Currency('USD', 'US Dollar')).name}")
            
            self.status_var.set(f"Loaded {len(self.currencies)} currencies | Ready")
            
            # Load initial exchange rates
            self.load_exchange_rates()
        else:
            messagebox.showerror("Error", "Failed to load currencies from API")
            self.status_var.set("Error loading currencies")
    
    def load_exchange_rates(self):
        """Load current exchange rates"""
        base = self.base_currency_var.get().split(' - ')[0] if ' - ' in self.base_currency_var.get() else "USD"
        
        self.status_var.set(f"Loading exchange rates (base: {base})...")
        self.root.update()
        
        data = self.api.get_latest_rates(base_currency=base)
        
        if data and 'data' in data:
            self.exchange_rates = data['data']
            self.base_currency = base
            self.converter = CurrencyConverter(self.exchange_rates, self.base_currency)
            
            # Update rates treeview
            self.rates_tree.delete(*self.rates_tree.get_children())
            
            for code, rate in sorted(self.exchange_rates.items()):
                if code in self.currencies:
                    currency_name = self.currencies[code].name
                    inverse = 1 / rate if rate != 0 else 0
                    self.rates_tree.insert('', tk.END, values=(
                        currency_name,
                        code,
                        f"{rate:.6f}",
                        f"{inverse:.6f}"
                    ))
            
            # Update rate heading
            self.rates_tree.heading('Rate', text=f'Rate (1 {base} =)')
            
            self.status_var.set(f"Loaded {len(self.exchange_rates)} exchange rates | Base: {base}")
        else:
            messagebox.showerror("Error", "Failed to load exchange rates")
            self.status_var.set("Error loading rates")
    
    def perform_conversion(self):
        """Perform currency conversion"""
        try:
            # Get amount
            amount = float(self.amount_var.get())
            
            # Get currency codes
            from_text = self.from_currency_var.get()
            to_text = self.to_currency_var.get()
            
            if not from_text or not to_text:
                messagebox.showwarning("Input Required", "Please select both currencies")
                return
            
            from_code = from_text.split(' - ')[0]
            to_code = to_text.split(' - ')[0]
            
            if not self.converter:
                messagebox.showerror("Error", "Exchange rates not loaded")
                return
            
            # Perform conversion
            result = self.converter.convert(amount, from_code, to_code)
            rate = self.converter.get_exchange_rate(from_code, to_code)
            
            # Display result
            from_symbol = self.currencies[from_code].symbol
            to_symbol = self.currencies[to_code].symbol
            
            self.result_var.set(f"{from_symbol} {amount:,.2f} = {to_symbol} {result:,.2f}")
            self.rate_info_var.set(f"1 {from_code} = {rate:.6f} {to_code}")
            
            # Add to history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_entry = f"[{timestamp}] {amount:,.2f} {from_code} → {result:,.2f} {to_code} (Rate: {rate:.6f})"
            self.conversion_history.append(history_entry)
            self.update_history_log()
            
            self.status_var.set(f"Converted {from_code} to {to_code}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
    
    def swap_currencies(self):
        """Swap from and to currencies"""
        from_val = self.from_currency_var.get()
        to_val = self.to_currency_var.get()
        
        self.from_currency_var.set(to_val)
        self.to_currency_var.set(from_val)
    
    def set_date(self, days_ago: int):
        """
        Set historical date
        Args:
            days_ago (int): Number of days before today
        """
        date = datetime.now() - timedelta(days=days_ago)
        self.hist_date_var.set(date.strftime("%Y-%m-%d"))
    
    def fetch_historical_data(self):
        """Fetch and display historical exchange rate data"""
        date = self.hist_date_var.get()
        from_code = self.hist_from_var.get()
        to_code = self.hist_to_var.get()
        
        if not from_code or not to_code:
            messagebox.showwarning("Input Required", "Please select both currencies")
            return
        
        self.status_var.set(f"Fetching historical data for {date}...")
        self.root.update()
        
        data = self.api.get_historical_rates(date, base_currency=from_code, currencies=[to_code])
        
        if data and 'data' in data:
            rates = data['data']
            
            self.hist_result_text.config(state=tk.NORMAL)
            self.hist_result_text.delete(1.0, tk.END)
            
            result = f"Historical Exchange Rates\n"
            result += f"{'='*60}\n\n"
            result += f"Date: {date}\n"
            result += f"Base Currency: {from_code} - {self.currencies[from_code].name}\n"
            result += f"Target Currency: {to_code} - {self.currencies[to_code].name}\n\n"
            result += f"{'='*60}\n\n"
            
            if to_code in rates:
                rate = rates[to_code]
                result += f"Exchange Rate:\n"
                result += f"  1 {from_code} = {rate:.6f} {to_code}\n"
                result += f"  1 {to_code} = {(1/rate):.6f} {from_code}\n\n"
                
                # Show conversion examples
                result += f"Conversion Examples:\n"
                result += f"-" * 40 + "\n"
                for amount in [1, 10, 100, 1000, 10000]:
                    converted = amount * rate
                    result += f"  {amount:>8,} {from_code} = {converted:>15,.2f} {to_code}\n"
                
                # Compare with current rate if available
                if self.converter and from_code in self.exchange_rates and to_code in self.exchange_rates:
                    current_rate = self.converter.get_exchange_rate(from_code, to_code)
                    difference = ((current_rate - rate) / rate) * 100
                    
                    result += f"\n{'='*60}\n\n"
                    result += f"Comparison with Current Rate:\n"
                    result += f"  Historical Rate: {rate:.6f}\n"
                    result += f"  Current Rate: {current_rate:.6f}\n"
                    result += f"  Change: {difference:+.2f}%\n"
                    
                    if difference > 0:
                        result += f"\n  → {to_code} has strengthened against {from_code}\n"
                    elif difference < 0:
                        result += f"\n  → {to_code} has weakened against {from_code}\n"
                    else:
                        result += f"\n  → No change in exchange rate\n"
            else:
                result += "Rate data not available for selected currencies.\n"
            
            self.hist_result_text.insert(1.0, result)
            self.hist_result_text.config(state=tk.DISABLED)
            
            self.status_var.set(f"Historical data loaded for {date}")
        else:
            messagebox.showerror("Error", "Failed to fetch historical data")
            self.status_var.set("Error fetching historical data")
    
    def update_history_log(self):
        """Update the conversion history log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        if self.conversion_history:
            header = "CONVERSION HISTORY\n"
            header += "=" * 80 + "\n\n"
            self.log_text.insert(tk.END, header)
            
            for entry in reversed(self.conversion_history):
                self.log_text.insert(tk.END, entry + "\n")
        else:
            self.log_text.insert(tk.END, "No conversions yet. Start converting to see history here.")
        
        self.log_text.config(state=tk.DISABLED)
    
    def clear_history(self):
        """Clear conversion history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all conversion history?"):
            self.conversion_history.clear()
            self.update_history_log()
            self.status_var.set("History cleared")


def main():
    """Main function to run the application"""
    # API key included for assessment demonstration purposes
    API_KEY = "fca_live_oOM3yXeel5gKT8iEKQWrv8Bo7Gq7qdSGDpcLlIqt"

    if not API_KEY.strip():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "API Key Required",
            "Please insert your Free Currency API key.\n\n"
            "Get your free API key at:\nhttps://freecurrencyapi.com/"
        )
        return

    root = tk.Tk()
    app = CurrencyConverterGUI(root, API_KEY)
    root.mainloop()



if __name__ == "__main__":
    main()