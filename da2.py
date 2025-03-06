import os
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# --------------------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------------------

def load_or_create_csv(file_path, columns):
    """
    Check if the CSV file exists. If not, create an empty DataFrame with the provided columns
    and export it to the file_path.
    """
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
        console.print(Panel(
            f"File '{file_path}' not found.\nCreated a new file with empty dataframe.",
            title="Info"
        ))
        return df
    else:
        return pd.read_csv(file_path)

def admin_flow(inventory: pd.DataFrame, sales: pd.DataFrame) -> None:
    """
    The admin menu flow, allowing the admin to:
      1) Check expired products
      2) View products with quantity < 20
      3) View entire database or a specific product
      4) Update any specific product
      0) Exit to main login menu
    """
    while True:
        console.print(Panel(
            "Admin Menu:\n"
            "1) Check expired products\n"
            "2) Check products with quantity < 20\n"
            "3) View database or a specific product\n"
            "4) Update a specific product\n"
            "0) Exit to login screen\n",
            title="Admin Options",
            style="bold magenta"
        ))
        
        choice = input("Enter your choice: ").strip()
        if choice.lower() == "exit" or choice == "0":
            # Exit admin menu to main login
            return
        
        if choice == "1":
            check_expired_products(inventory)
        elif choice == "2":
            check_low_quantity_products(inventory)
        elif choice == "3":
            access_database(inventory)
        elif choice == "4":
            update_product(inventory)
        else:
            console.print(Panel("Invalid choice. Please try again.", title="Error", style="bold red"))

def check_expired_products(inventory: pd.DataFrame) -> None:
    """
    Display all products whose expiry date is before the current date.
    """
    current_date = datetime.now()
    expired_mask = (pd.notnull(inventory['expiry date'])) & (inventory['expiry date'] < current_date)
    expired_products = inventory[expired_mask]
    
    if expired_products.empty:
        console.print(Panel("No expired products found.", title="Expired Products", style="bold green"))
    else:
        console.print(Panel("Expired Products:", title="Expired Products", style="bold red"))
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Product ID", justify="right")
        table.add_column("Product Name")
        table.add_column("Expiry Date")
        
        for _, row in expired_products.iterrows():
            table.add_row(
                str(row['Product_id']),
                row['product_name'],
                row['expiry date'].strftime("%Y-%m-%d")
            )
        console.print(table)

def check_low_quantity_products(inventory: pd.DataFrame) -> None:
    """
    Display all products whose quantity is less than 20.
    """
    low_qty_mask = inventory['total quantity'] < 20
    low_qty_products = inventory[low_qty_mask]
    
    if low_qty_products.empty:
        console.print(Panel("No products with quantity less than 20.", title="Low Quantity", style="bold green"))
    else:
        console.print(Panel("Products with Quantity < 20:", title="Low Quantity", style="bold yellow"))
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Product ID", justify="right")
        table.add_column("Product Name")
        table.add_column("Quantity", justify="right")
        
        for _, row in low_qty_products.iterrows():
            table.add_row(
                str(row['Product_id']),
                row['product_name'],
                str(row['total quantity'])
            )
        console.print(table)

def access_database(inventory: pd.DataFrame) -> None:
    """
    Ask the user if they want to view the entire database or a specific product.
    """
    console.print(Panel(
        "1) View entire inventory\n"
        "2) View a specific product by ID\n"
        "0) Go back",
        title="Access Database",
        style="bold cyan"
    ))
    choice = input("Enter your choice: ").strip()
    if choice.lower() == "exit" or choice == "0":
        return
    
    if choice == "1":
        # Display entire inventory in a table
        if inventory.empty:
            console.print(Panel("Inventory is empty.", style="bold red"))
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Product ID", justify="right")
            table.add_column("Name")
            table.add_column("Quantity", justify="right")
            table.add_column("Type")
            table.add_column("Expiry Date")
            table.add_column("MRP", justify="right")
            
            for _, row in inventory.iterrows():
                expiry_str = (row['expiry date'].strftime("%Y-%m-%d") 
                              if pd.notnull(row['expiry date']) else "N/A")
                table.add_row(
                    str(row['Product_id']),
                    row['product_name'],
                    str(row['total quantity']),
                    row['product type'],
                    expiry_str,
                    str(row['mrp'])
                )
            console.print(table)
    elif choice == "2":
        pid_input = input("Enter the product ID: ").strip()
        if pid_input.lower() == "exit":
            return
        try:
            pid = int(pid_input)
        except ValueError:
            console.print(Panel("Invalid product ID.", title="Error", style="bold red"))
            return
        
        product_filter = inventory['Product_id'] == pid
        if not product_filter.any():
            console.print(Panel("Product not found.", title="Error", style="bold red"))
            return
        
        product_record = inventory[product_filter].iloc[0]
        expiry_str = (product_record['expiry date'].strftime("%Y-%m-%d") 
                      if pd.notnull(product_record['expiry date']) else "N/A")
        
        info_str = (
            f"Product ID: {product_record['Product_id']}\n"
            f"Name: {product_record['product_name']}\n"
            f"Quantity: {product_record['total quantity']}\n"
            f"Type: {product_record['product type']}\n"
            f"Expiry Date: {expiry_str}\n"
            f"MRP: {product_record['mrp']}"
        )
        console.print(Panel(info_str, title="Product Info", style="bold cyan"))
    else:
        console.print(Panel("Invalid choice.", title="Error", style="bold red"))

def update_product(inventory: pd.DataFrame) -> None:
    """
    Let the admin update a product's details (e.g., name, quantity, MRP, etc.).
    """
    pid_input = input("Enter the product ID to update (or 'exit' to go back): ").strip()
    if pid_input.lower() == "exit":
        return
    
    try:
        pid = int(pid_input)
    except ValueError:
        console.print(Panel("Invalid product ID.", title="Error", style="bold red"))
        return
    
    product_filter = inventory['Product_id'] == pid
    if not product_filter.any():
        console.print(Panel("Product not found in inventory.", title="Error", style="bold red"))
        return
    
    product_record = inventory[product_filter].iloc[0]
    console.print(Panel(
        f"Current Product Info:\n"
        f"1) Name: {product_record['product_name']}\n"
        f"2) Quantity: {product_record['total quantity']}\n"
        f"3) Type: {product_record['product type']}\n"
        f"4) Expiry Date: {product_record['expiry date']}\n"
        f"5) MRP: {product_record['mrp']}\n",
        title="Update Product"
    ))
    
    field_choice = input("Which field do you want to update? (1-5, or 'exit' to cancel): ").strip()
    if field_choice.lower() == "exit":
        return
    
    if field_choice not in ["1","2","3","4","5"]:
        console.print(Panel("Invalid choice.", title="Error", style="bold red"))
        return
    
    new_value = input("Enter the new value: ").strip()
    if new_value.lower() == "exit":
        return
    
    if field_choice == "1":
        inventory.loc[product_filter, 'product_name'] = new_value
    elif field_choice == "2":
        try:
            new_qty = int(new_value)
            inventory.loc[product_filter, 'total quantity'] = new_qty
        except ValueError:
            console.print(Panel("Invalid quantity. Update aborted.", title="Error", style="bold red"))
            return
    elif field_choice == "3":
        inventory.loc[product_filter, 'product type'] = new_value
    elif field_choice == "4":
        try:
            new_expiry = pd.to_datetime(new_value)
            inventory.loc[product_filter, 'expiry date'] = new_expiry
        except ValueError:
            console.print(Panel("Invalid date format. Update aborted.", title="Error", style="bold red"))
            return
    elif field_choice == "5":
        try:
            new_mrp = float(new_value)
            inventory.loc[product_filter, 'mrp'] = new_mrp
        except ValueError:
            console.print(Panel("Invalid MRP. Update aborted.", title="Error", style="bold red"))
            return
    
    console.print(Panel("Product updated successfully.", title="Update Success", style="bold green"))

def sales_flow(inventory: pd.DataFrame, sales: pd.DataFrame, sales_file: str, rep_username: str) -> None:
    """
    The existing code flow for sales representatives.
    1) Prompt for product ID and quantity
    2) Check expiry and available quantity
    3) Compute total price with discount
    4) Print a receipt table
    5) Update sales.csv and inventory.csv
    """
    # Generate a new sales_id for the current bill
    if sales.empty:
        bill_id = 1
    else:
        # Ensure sales_id is numeric
        sales['sales_id'] = pd.to_numeric(sales['sales_id'], errors='coerce')
        bill_id = int(sales['sales_id'].max()) + 1

    new_sales = []
    
    while True:
        product_id_input = input("Enter product id (or 'exit' to return to login): ").strip()
        if product_id_input.lower() == "exit":
            # Return to login
            return
        
        try:
            product_id = int(product_id_input)
        except ValueError:
            console.print(Panel("Invalid product id. Please enter a valid integer.", title="Error", style="bold red"))
            continue
        
        # Retrieve the product from the inventory DataFrame
        product_filter = inventory['Product_id'] == product_id
        if not product_filter.any():
            console.print(Panel("Product id not found in inventory. Please try again.", title="Error", style="bold red"))
            continue
        
        # Since product id is unique, take the first matching row
        product_record = inventory[product_filter].iloc[0]
        
        # Check if the product is expired
        current_date = datetime.now()
        if pd.notnull(product_record['expiry date']) and current_date > product_record['expiry date']:
            console.print(Panel("Error: Product has expired. Cannot proceed with sale.", title="Error", style="bold red"))
            continue
        
        # Display the product name automatically
        console.print(Panel(
            f"Product name: [bold green]{product_record['product_name']}[/bold green]",
            title="Product Info"
        ))
        
        # Ask for quantity purchased and validate
        while True:
            qty_input = input("Enter quantity of product purchased: ").strip()
            if qty_input.lower() == "exit":
                return
            
            try:
                qty = int(qty_input)
                if qty <= 0:
                    console.print(Panel("Quantity must be positive. Please enter again.", title="Error", style="bold red"))
                    continue
            except ValueError:
                console.print(Panel("Invalid quantity. Please enter a valid integer.", title="Error", style="bold red"))
                continue
            
            available_qty = int(product_record['total quantity'])
            if qty > available_qty:
                console.print(Panel(
                    f"Insufficient quantity in inventory. Available: {available_qty}. Please enter a lower quantity.",
                    title="Error",
                    style="bold red"
                ))
            else:
                break
        
        # Retrieve MRP and compute store price (10% discount)
        mrp = float(product_record['mrp'])
        store_price = 0.9 * mrp
        total_price = store_price * qty
        
        # Print sale details for confirmation
        sale_details = (
            f"Product id: {product_id}\n"
            f"Product name: {product_record['product_name']}\n"
            f"Store price: {store_price:.2f}\n"
            f"Quantity: {qty}\n"
            f"Total price: {total_price:.2f}"
        )
        console.print(Panel(sale_details, title="Sale Details", style="cyan"))
        
        # Append the sale record, including the billed_by field
        sale_record = {
            'sales_id': bill_id,
            'product_id': product_id,
            'product_name': product_record['product_name'],
            'mrp': mrp,
            'store_price': store_price,
            'quantity purchased': qty,
            'date of purchase': current_date.strftime("%Y-%m-%d %H:%M:%S"),
            'total price': total_price,
            'billed_by': rep_username
        }
        new_sales.append(sale_record)
        
        # Update inventory by reducing the total quantity available
        inventory.loc[product_filter, 'total quantity'] = available_qty - qty
        
        # Ask if the user wants to add another item
        another = input("Do you want to add another item? (Y/N): ").strip().upper()
        if another != 'Y':
            break

    # After processing all items, if there are any sales records, show a final receipt
    if new_sales:
        new_sales_df = pd.DataFrame(new_sales)
        subtotal = new_sales_df["total price"].sum()
        tax = 0.05 * subtotal
        final_total = subtotal + tax
        
        # Build a receipt-like table using Rich
        receipt_table = Table(show_header=True, header_style="bold magenta")
        receipt_table.title = f"Receipt - Bill ID: {bill_id}"
        receipt_table.add_column("Product Name", style="bold green", width=20)
        receipt_table.add_column("Store Price", justify="right")
        receipt_table.add_column("Quantity", justify="right")
        receipt_table.add_column("Line Total", justify="right")

        # Add rows for each item in the bill
        for item in new_sales:
            receipt_table.add_row(
                item['product_name'],
                f"{item['store_price']:.2f}",
                str(item['quantity purchased']),
                f"{item['total price']:.2f}"
            )
        
        # Display the receipt table
        console.print(receipt_table)
        
        # Display the subtotal, tax, and final total in a panel
        bill_summary = (
            f"[bold]Subtotal:[/bold] {subtotal:.2f}\n"
            f"[bold]Tax (5%):[/bold] {tax:.2f}\n"
            f"[bold]Final Total:[/bold] {final_total:.2f}"
        )
        console.print(Panel(bill_summary, title="Bill Summary", style="bold magenta"))
        
        # Append new sales to the existing sales DataFrame and save
        sales = pd.concat([sales, new_sales_df], ignore_index=True)
        sales.to_csv(sales_file, index=False)

# --------------------------------------------------------------------
# MAIN FUNCTION (LOGIN & ROUTING)
# --------------------------------------------------------------------

def main():
    # Prompt user for the base directory containing CSV files
    base_path_input = input(
        "Enter the base directory path where inventory and sales CSV files are located: "
    ).strip()
    base_path = os.path.expanduser(base_path_input)
    
    # Validate directory; if invalid, default to a known path
    if not os.path.exists(base_path):
        console.print(Panel("Invalid directory path. Using default path.", title="Error", style="bold red"))
        base_path = r"C:\Users\sidak\OneDrive\Desktop\VIT\ASSIGNMENTS"
    
    # Construct file paths for inventory and sales
    inventory_file = os.path.join(base_path, "inventory.csv")
    sales_file = os.path.join(base_path, "sales.csv")

    # Define the expected columns for each CSV file; note the new "billed_by" column in sales
    inventory_columns = [
        "Product_id", "product_name", "total quantity",
        "product type", "expiry date", "mrp"
    ]
    sales_columns = [
        "sales_id", "product_id", "product_name", "mrp",
        "store_price", "quantity purchased", "date of purchase", "total price", "billed_by"
    ]

    # Load or create the inventory and sales dataframes
    inventory = load_or_create_csv(inventory_file, inventory_columns)
    sales = load_or_create_csv(sales_file, sales_columns)
    
    # If inventory is not empty, ensure that the expiry date column is in datetime format
    if not inventory.empty:
        inventory['expiry date'] = pd.to_datetime(inventory['expiry date'], errors='coerce')

    # MAIN LOOP (Login screen)
    while True:
        console.print(Panel(
            "Welcome! Are you an admin (A) or sales representative (S)?\n"
            "Type 'exit' to quit.",
            title="Login Screen",
            style="bold green"
        ))
        user_type = input("Enter your choice (A/S/exit): ").strip().lower()
        
        if user_type == "exit":
            console.print(Panel("Exiting program. Goodbye!", title="Exit", style="bold red"))
            break
        
        if user_type == "a":
            # Admin login
            username = input("Enter admin username: ").strip()
            if username.lower() == "exit":
                continue
            password = input("Enter admin password: ").strip()
            if password.lower() == "exit":
                continue
            
            # Default admin credentials
            if username == "admin" and password == "admin":
                # Admin flow
                admin_flow(inventory, sales)
                # Save inventory changes after admin tasks
                inventory.to_csv(inventory_file, index=False)
            else:
                console.print(Panel("Invalid admin credentials.", title="Error", style="bold red"))
        
        elif user_type == "s":
            # Sales representative login
            username = input("Enter your sales username: ").strip().lower()
            if username == "exit":
                continue
            password = input("Enter your password: ").strip().lower()
            if password == "exit":
                continue
            
            # We have two default sales reps: user1, user2 with password 'user'
            valid_users = {"user1": "user", "user2": "user"}
            
            if username in valid_users and valid_users[username] == password:
                # Sales flow: pass the rep's username to record it in sales
                sales_flow(inventory, sales, sales_file, username)
                # Save inventory changes after sales flow
                inventory.to_csv(inventory_file, index=False)
            else:
                console.print(Panel("Invalid sales credentials.", title="Error", style="bold red"))
        
        else:
            console.print(Panel("Invalid option. Please choose 'A' for admin or 'S' for sales.", title="Error", style="bold red"))

if __name__ == "__main__":
    main()
