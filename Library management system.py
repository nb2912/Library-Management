from tkinter import messagebox, ttk
import pymysql
from tkinter import *
from datetime import datetime, timedelta

# Connect to the MySQL database
db =      0 
cursor = db.cursor()

# Create a books table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        author VARCHAR(255),
        price DECIMAL(10, 2),
        year_of_publishing INT,
        version INT,
        copies INT,
        available_copies INT,
        availability BOOLEAN
    )
""")

# Create a transactions table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        book_id INT,
        person_name VARCHAR(255),
        phone_number VARCHAR(15),
        email VARCHAR(255),
        vending_date DATE,
        return_date DATE,
        due_date DATE,
        fine DECIMAL(10, 2),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )
""")

# Function to add a book to the database
def add_book():
    title = title_entry.get()
    author = author_entry.get()
    price = price_entry.get()
    year_of_publishing = year_entry.get()
    version = version_entry.get()
    copies = copies_entry.get()
    availability = True  # Assuming a newly added book is available

    # Insert the book details into the database
    cursor.execute("""
        INSERT INTO books (title, author, price, year_of_publishing, version, copies, available_copies, availability)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (title, author, price, year_of_publishing, version, copies, copies, availability))
    db.commit()
    messagebox.showinfo("Success", "Book added successfully")

# Function to view all books in the database
def view_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    # Display the books in a scrollable table in the GUI
    for widget in books_frame.winfo_children():
        widget.destroy()

    tree = ttk.Treeview(books_frame, columns=("ID", "Title", "Author", "Price", "Year", "Version", "Copies", "Available Copies", "Availability"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Author", text="Author")
    tree.heading("Price", text="Price")
    tree.heading("Year", text="Year")
    tree.heading("Version", text="Version")
    tree.heading("Copies", text="Copies")
    tree.heading("Available Copies", text="Available Copies")
    tree.heading("Availability", text="Availability")

    tree.column("ID", width=40)
    tree.column("Title", width=150)
    tree.column("Author", width=150)
    tree.column("Price", width=80)
    tree.column("Year", width=60)
    tree.column("Version", width=60)
    tree.column("Copies", width=60)
    tree.column("Available Copies", width=120)
    tree.column("Availability", width=100)

    for book in books:
        tree.insert("", "end", values=book)

    tree.pack(fill="both", expand=True)
    scrollbar = ttk.Scrollbar(books_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

# Function to lend a book
def lend_book():
    book_id = lend_book_id_entry.get()
    person_name = person_name_entry.get()
    phone_number = phone_number_entry.get()
    email = email_entry.get()
    issue_date = issue_date_entry.get()
    due_date = due_date_entry.get()

    # Convert string dates to datetime objects
    issue_date = datetime.strptime(issue_date, "%Y-%m-%d").date()
    due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

    # Check if there are available copies of the book
    cursor.execute("SELECT available_copies FROM books WHERE id = %s", (book_id,))
    result = cursor.fetchone()
    if result and result[0] > 0:
        # Insert the due date and book details into the transactions table
        cursor.execute("""
            INSERT INTO transactions (book_id, person_name, phone_number, email, vending_date, due_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (book_id, person_name, phone_number, email, issue_date, due_date))
        db.commit()

        # Update book availability and available copies
        cursor.execute("UPDATE books SET availability = FALSE, available_copies = available_copies - 1 WHERE id = %s", (book_id,))
        db.commit()

        messagebox.showinfo("Success", "Book lent successfully")
    else:
        messagebox.showerror("Error", "No available copies of the book")

# Function to return a book
def return_book():
    book_id = return_book_id_entry.get()
    return_date = return_date_entry.get()

    # Convert string date to datetime object
    return_date = datetime.strptime(return_date, "%Y-%m-%d").date()

    # Get the due date and calculate the fine
    cursor.execute("SELECT due_date FROM transactions WHERE book_id = %s AND return_date IS NULL", (book_id,))
    result = cursor.fetchone()
    if result:
        due_date = result[0]
        if return_date > due_date:
            fine = (return_date - due_date).days * 10  # Fine is 10 rupees per day of delay
        else:
            fine = 0
    else:
        fine = 0

    # Update book availability and available copies to True and increment by 1
    cursor.execute("UPDATE books SET availability = TRUE, available_copies = available_copies + 1 WHERE id = %s", (book_id,))
    db.commit()

    # Update return date and fine in the transactions table
    cursor.execute("UPDATE transactions SET return_date = %s, fine = %s WHERE book_id = %s AND return_date IS NULL", (return_date, fine, book_id))
    db.commit()

    if fine > 0:
        messagebox.showinfo("Success", f"Book returned successfully. Fine: {fine} rupees")
    else:
        messagebox.showinfo("Success", "Book returned successfully")

# Function to search for a book by title, author, and version
def search_book():
    title = title_search_entry.get()
    author = author_search_entry.get()
    version = version_search_entry.get()

    # Search for the book in the database
    cursor.execute("SELECT * FROM books WHERE title = %s AND author = %s AND version = %s", (title, author, version))
    result = cursor.fetchall()

    # Destroy previous widgets in the search_frame
    for widget in search_frame.winfo_children():
        widget.destroy()
    

    if result:
        book = result[0]
        book_details = f"ID: {book[0]}\nTitle: {book[1]}\nAuthor: {book[2]}\nPrice: {book[3]}\n" \
                        f"Year: {book[4]}\nVersion: {book[5]}\nCopies: {book[6]}\n" \
                        f"Available Copies: {book[7]}\nAvailability: {'Available' if book[8] else 'Not Available'}"
        messagebox.showinfo("Book Details", book_details)
        
    else:
        strin =  "Book Not Found"
        messagebox.showinfo("Book Not Found",strin)
# GUI setup
root = Tk()
root.title("BOOKISH HEAVEN")

# Book details entry
title_label = Label(root, text="Title:")
title_label.grid(row=0, column=0)
title_entry = Entry(root)
title_entry.grid(row=0, column=1)

author_label = Label(root, text="Author:")
author_label.grid(row=1, column=0)
author_entry = Entry(root)
author_entry.grid(row=1, column=1)

price_label = Label(root, text="Price:")
price_label.grid(row=2, column=0)
price_entry = Entry(root)
price_entry.grid(row=2, column=1)

year_label = Label(root, text="Year of Publishing:")
year_label.grid(row=3, column=0)
year_entry = Entry(root)
year_entry.grid(row=3, column=1)

version_label = Label(root, text="Version:")
version_label.grid(row=4, column=0)
version_entry = Entry(root)
version_entry.grid(row=4, column=1)

copies_label = Label(root, text="Number of Copies:")
copies_label.grid(row=5, column=0)
copies_entry = Entry(root)
copies_entry.grid(row=5, column=1)

add_button = Button(root, text="Add Book", command=add_book)
add_button.grid(row=6, column=0, columnspan=2)

# Lending and returning books entry
lend_book_id_label = Label(root, text="Book ID to lend:")
lend_book_id_label.grid(row=7, column=0)
lend_book_id_entry = Entry(root)
lend_book_id_entry.grid(row=7, column=1)

person_name_label = Label(root, text="Person Name:")
person_name_label.grid(row=8, column=0)
person_name_entry = Entry(root)
person_name_entry.grid(row=8, column=1)

phone_number_label = Label(root, text="Phone Number:")
phone_number_label.grid(row=9, column=0)
phone_number_entry = Entry(root)
phone_number_entry.grid(row=9, column=1)

email_label = Label(root, text="Email:")
email_label.grid(row=10, column=0)
email_entry = Entry(root)
email_entry.grid(row=10, column=1)

issue_date_label = Label(root, text="Issue Date (YYYY-MM-DD):")
issue_date_label.grid(row=11, column=0)
issue_date_entry = Entry(root)
issue_date_entry.grid(row=11, column=1)

due_date_label = Label(root, text="Due Date (YYYY-MM-DD):")
due_date_label.grid(row=12, column=0)
due_date_entry = Entry(root)
due_date_entry.grid(row=12, column=1)

lend_button = Button(root, text="Lend Book", command=lend_book)
lend_button.grid(row=13, column=0, columnspan=2)

return_book_id_label = Label(root, text="Book ID to return:")
return_book_id_label.grid(row=14, column=0)
return_book_id_entry = Entry(root)
return_book_id_entry.grid(row=14, column=1)

return_date_label = Label(root, text="Return Date (YYYY-MM-DD):")
return_date_label.grid(row=15, column=0)
return_date_entry = Entry(root)
return_date_entry.grid(row=15, column=1)

return_button = Button(root, text="Return Book", command=return_book)
return_button.grid(row=16, column=0, columnspan=2)

# Search for a book entry
title_search_label = Label(root, text="Search Book - Title:")
title_search_label.grid(row=17, column=0)
title_search_entry = Entry(root)
title_search_entry.grid(row=17, column=1)

author_search_label = Label(root, text="Search Book - Author:")
author_search_label.grid(row=18, column=0)
author_search_entry = Entry(root)
author_search_entry.grid(row=18, column=1)

version_search_label = Label(root, text="Search Book - Version:")
version_search_label.grid(row=19, column=0)
version_search_entry = Entry(root)
version_search_entry.grid(row=19, column=1)

search_button = Button(root, text="Search Book", command=search_book)
search_button.grid(row=20, column=0, columnspan=2)

# View Books button
view_button = Button(root, text="View Books", command=view_books)
view_button.grid(row=21, column=0, columnspan=2)

# Book listbox
books_frame = Frame(root)
books_frame.grid(row=22, column=0, columnspan=2)

# Search result frame
search_frame = Frame(root)
search_frame.grid(row=23, column=0, columnspan=2)

root.mainloop()

# Close the database connection when the application is closed
db.close()
