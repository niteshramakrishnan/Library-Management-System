#Importing the libraries

from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview
import psycopg2
from datetime import datetime, timedelta, date


#Connecting to the database
my_conn = psycopg2.connect(  host="localhost",  user="postgres",  password="12345",  database="lms")
cursor = my_conn.cursor()
my_conn.commit()

cursor = None
todays_date = datetime.today()
borrower_count = 1

#Defining the Interface

class GUI:
    def __init__(self, master):
        self.parent = master
        self.parent.title(" Library Management System ")
        self.frame = Frame(self.parent, bg='yellow', width=800, height=400)
        self.frame.grid(row=0, column=0)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_propagate(False)

        # Parameter Initialization
        self.search_string = None
        self.data = None
        self.borrower_id = None
        self.book_for_check_out_isbn = None

        # Heading grid
        self.heading_label = Frame(self.frame, bg='yellow')
        self.heading_label.grid(row=0, column=0, sticky=N)
        self.heading_label.grid_rowconfigure(0, weight=1)
        self.heading_label.grid_columnconfigure(0, weight=1)
        self.heading_label = Label(self.heading_label,bg='yellow', text='Library Management System', font=('Helvetica',15))
        self.heading_label.grid(row=0, column=0)
        self.heading_label.grid_rowconfigure(0, weight=1)
        self.heading_label.grid_columnconfigure(0, weight=1)
        
        #search frame grid
        self.search_frame = Frame(self.frame, bg='yellow')
        self.search_frame.grid(row=1, column=0, sticky=W+E, padx=10, pady=10)
        self.search_frame.grid_rowconfigure(1, weight=1)
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_label = Label(self.search_frame, text='Search here :', bg='yellow')
        self.search_label.grid(row=1, column=0, sticky=N+S+W, padx=10, pady=10)
        self.search_label.grid_rowconfigure(1, weight=1)
        self.search_label.grid_columnconfigure(0, weight=1)
        self.search_textbox = Entry(self.search_frame, width=65)
        self.search_textbox.grid(row=1, column=0, sticky=N+S, padx=10, pady=10)
        self.search_textbox.grid_rowconfigure(1, weight=1)
        self.search_label.grid_columnconfigure(0, weight=1)
        self.search_button = Button(self.search_frame, text='Search / View All',bg='blue',fg='white', command=self.search)
        self.search_button.grid(row=1, column=0, sticky=N+S+E, padx=10, pady=10)
        self.search_button.grid_rowconfigure(1, weight=1)
        self.search_button.grid_columnconfigure(0, weight=1)
        
        
        # Display Area grid
        self.active_area = Frame(self.frame)
        self.active_area.grid(row=2, column=0, sticky=N)
        self.active_area.grid_rowconfigure(2, weight=0)
        self.result_table = Treeview(self.active_area, columns=["isbn", "Book Title", "Author(s)", "Availability"])
        self.result_table.grid(row=0, column=0)
        self.result_table.grid_rowconfigure(0, weight=0)
        self.result_table.heading('#0', text="isbn")
        self.result_table.heading('#1', text="Book Title")
        self.result_table.heading('#2', text="Author(s)")
        self.result_table.heading('#3', text="Availability")
        self.result_table.bind('<ButtonRelease-1>', self.selectBookForCheckout)

        # Buttons grid
        self.major_functions = Frame(self.frame, bg='yellow')
        self.major_functions.grid(row=3, column=0, sticky=N)
        self.major_functions.grid_rowconfigure(3, weight=1)
        self.check_out_btn = Button(self.major_functions, text="Check Out Book",bg='blue',fg='white', command=self.check_out_fn)
        self.check_out_btn.grid(row=0, column=0, padx=10, pady=10)
        self.check_out_btn.grid_rowconfigure(0, weight=1)
        self.check_out_btn.grid_columnconfigure(0, weight=1)
        self.check_in_btn = Button(self.major_functions, text="Check In Book",bg='blue',fg='white', command=self.check_in_fn)
        self.check_in_btn.grid(row=0, column=1, padx=10, pady=10)
        self.check_out_btn.grid_rowconfigure(0, weight=1)
        self.check_out_btn.grid_columnconfigure(1, weight=1)
        self.update_fines_btn = Button(self.major_functions, text="Updates Fines",bg='blue',fg='white', command=self.update_fines_fn)
        self.update_fines_btn.grid(row=0, column=2, padx=10, pady=10)
        self.pay_fines_btn = Button(self.major_functions, text="Pay Fines",bg='blue',fg='white', command=self.pay_fines)
        self.pay_fines_btn.grid(row=0, column=3, padx=10, pady=10)
        self.change_day_btn = Button(self.major_functions, text="Change Day",bg='blue',fg='white', command=self.change_day)
        self.change_day_btn.grid(row=0, column=4, padx=10, pady=10)
        self.add_borrower_btn = Button(self.major_functions, text="Add New Borrower",bg='blue',fg='white', command=self.add_borrower)
        self.add_borrower_btn.grid(row=0, column=5, padx=10, pady=10)
        
    def change_day(self):
        global todays_date
        todays_date = todays_date + timedelta(days=1)
        messagebox.showinfo("", "Date Changed ")
        #print(todays_date)

    def search(self):
        self.search_string = self.search_textbox.get()
        cursor = my_conn.cursor()
        
        cursor.execute("select book.isbn, book.title, authors.name from book join book_authors on book.isbn = book_authors.isbn join authors on book_authors.author_id = authors.author_id where book.title ilike concat('%', '" + self.search_string + "', '%') OR authors.name ilike concat('%', '" + self.search_string + "', '%') OR book.isbn ilike concat('%', '" + self.search_string + "', '%')")

        self.data = cursor.fetchall()
        self.view_data()

    def view_data(self):
     
        self.result_table.delete(*self.result_table.get_children())
        for elem in self.data:
            cursor = my_conn.cursor()
            cursor.execute("select exists(select book_loans.isbn from book_loans where book_loans.isbn = '" + str(elem[0]) + "')")
            result = cursor.fetchall()
            if result == [(0,)]:
                availability = "Available"
            else:
                cursor = my_conn.cursor()
                cursor.execute("select book_loans.date_in from book_loans where book_loans.isbn = '" + str(elem[0]) + "'")
                result = cursor.fetchall()
                if result[-1][0] is None:
                    availability = "Not Available"
                else:
                    availability = "Available"
            self.result_table.insert('', 'end', text=str(elem[0]),
                                       values=(elem[1], elem[2], availability))

    def selectBookForCheckout(self, a):
        curItem = self.result_table.focus()
        self.book_for_check_out_isbn = self.result_table.item(curItem)['text']

    def check_out_fn(self):
        if self.book_for_check_out_isbn is None:
            messagebox.showinfo("", "Select Book")
            return None
        
        cursor = my_conn.cursor()
        cursor.execute("select exists(select isbn from book_loans where isbn ilike '" + self.book_for_check_out_isbn + "' and date_in is NULL) ")
        result = cursor.fetchall()  
        print(result)
        if result == [(1,)]:
            messagebox.showinfo(" ", "Book not Available")
            return None
        
        self.borrower_id = simpledialog.askstring("Check Out Book", "Enter Borrower ID")
        cursor = my_conn.cursor()
        cursor.execute("select exists(select card_id from borrower where borrower.card_id = '" + str(self.borrower_id) + "')")
        result = cursor.fetchall()  
        
        if int(self.borrower_id) > 1000 + borrower_count:
            messagebox.showinfo(" ", "Borrower not in Database!")
            return None
        else:
            count = 0
            cursor = my_conn.cursor()
            cursor.execute("select book_loans.date_in from book_loans where book_loans.card_id = '" + str(self.borrower_id) + "'")
            result = cursor.fetchall()
            for elem in result:
                if elem[0] is None:
                    count += 1
            if count >= 3:
                messagebox.showinfo(" ", "Borrower has loaned 3 books already!")
                return None
            else:
                cursor = my_conn.cursor()
                
                cursor.execute("insert into book_loans (isbn, card_id, date_out, due_date) VALUES (%s, %s , current_date , current_date + 14)" , ( self.book_for_check_out_isbn , self.borrower_id) )
                my_conn.commit()
                cursor = my_conn.cursor()
                cursor.execute("select MAX(loan_id) from book_loans")
                result = cursor.fetchall()
                loan_id = result[0][0]
                cursor.execute("insert into fines (loan_id, fine_amt, paid) VALUES ('" + str(loan_id) + "', '0.00', '0')")
                my_conn.commit()
                messagebox.showinfo(" ", "Book Loaned Out!")

    def check_in_fn(self):
        self.checkInWindow = Toplevel(self.parent, width=500, height=200, bg='yellow')
        self.checkInWindow.title("Check In Here")
        self.app = CheckIn(self.checkInWindow)

    def update_fines_fn(self):
        cursor = my_conn.cursor()
        cursor.execute("select book_loans.loan_id, book_loans.date_in, book_loans.due_date from book_loans")
        result = cursor.fetchall()
        for record in result:
            date_in = record[1]
            due_date = record[2]

            
            if date_in is None:
                date_in = todays_date.date()
            diff = date_in - due_date

            if diff.days > 0:
                fine = int(diff.days) * 0.25
            else:
                fine = 0

            cursor = my_conn.cursor()
            cursor.execute("update fines set fine_amt = %s where fines.loan_id = %s", (fine, record[0]))
            my_conn.commit()
        messagebox.showinfo(" ","Fines Calculated")

    def pay_fines(self):
        self.newPayFinesWindow = Toplevel(self.parent, bg='yellow')
        self.newPayFinesWindow.title("Pay Fines")
        self.app1 = PayFines(self.newPayFinesWindow)

    def add_borrower(self):
        self.newBorrowerWindow = Toplevel(self.parent, bg='yellow')
        self.newBorrowerWindow.title("Add New Borrower")
        self.newapp = AddBorrower(self.newBorrowerWindow)


class CheckIn:
    def __init__(self, master):
        self.parent = master

        self.book_for_check_in_id = None
        self.search_string = None
        self.data = None

        self.search_label = Label(self.parent, bg='yellow', text="Search here: Borrower ID, Borrower Name or isbn")
        self.search_label.grid(row=0, column=0, sticky=N+S+W, padx=10, pady=10)
        self.search_textbox = Entry(self.parent, width = 70)
        self.search_textbox.grid(row=0, column=0, sticky=N+S, padx=10, pady=10)
        self.searchBtn = Button(self.parent, text="Search / View All",bg='blue',fg='white', command=self.search_book_loans)
        self.searchBtn.grid(row=0, column=0, sticky=N+S+E, padx=10, pady=10)
        self.table = Treeview(self.parent, columns=["Loan ID", "isbn", "Borrower ID", "Title"])
        self.table.grid(row=3, column=0)
        self.table.heading('#0', text="Loan ID")
        self.table.heading('#1', text="isbn")
        self.table.heading('#2', text="Borrower ID")
        self.table.heading('#3', text="Book Title")
        self.table.bind('<ButtonRelease-1>', self.select_book_for_checkin)
        self.check_in_btn = Button(self.parent, text="Check In",bg='blue',fg='white', command=self.check_in_fn)
        self.check_in_btn.grid(row=4, column=0)

    def search_book_loans(self):
        self.search_string = self.search_textbox.get()
        if self.search_string.isdigit():
            self.search_string_int = int(self.search_string)
        cursor = my_conn.cursor()
        cursor.execute("select book_loans.loan_id, book_loans.isbn, book_loans.card_id, book.title, book_loans.date_in from book_loans join borrower on book_loans.card_id = borrower.card_id join book on book_loans.isbn = book.isbn where book_loans.isbn ilike concat('%', '" + self.search_string + "', '%') OR borrower.bname ilike concat('%', '" + self.search_string + "', '%') OR borrower.card_id = {}".format(self.search_string_int))

        self.data = cursor.fetchall()
        self.view_data()

    def view_data(self):
        self.table.delete(*self.table.get_children())
        for elem in self.data:
            if elem[4] is None:
                self.table.insert('', 'end', text=str(elem[0]), values=(elem[1], elem[2], elem[3]))

    def select_book_for_checkin(self, a):
        curItem = self.table.focus()
        self.book_for_check_in_id = self.table.item(curItem)['text']

    def check_in_fn(self):
        if self.book_for_check_in_id is None:
            messagebox.showinfo("Select a Book")
            return None

        cursor = my_conn.cursor()

        cursor.execute("select book_loans.date_in from book_loans where book_loans.loan_id = '" + str(self.book_for_check_in_id) + "'")

        result = cursor.fetchall()

        if result[0][0] is None:
            cursor.execute("update book_loans set date_in = current_date where book_loans.loan_id = "  + str(self.book_for_check_in_id) + " ")
            my_conn.commit()
            messagebox.showinfo("", "Book Checked In Successfully!")
            self.parent.destroy()
        else:
            return None


class AddBorrower:
    def __init__(self, master):
        self.parent = master

        self.titleLabel = Label(self.parent, text="Enter Details of New Borrower", bg='yellow',fg='black', font=('Calibri', 12))
        self.titleLabel.grid(row=0, column=2, padx=20, pady=20)
        self.fnameLabel = Label(self.parent, text="First Name", bg='yellow',fg='black').grid(row=1, column=0, padx=10, pady=5)
        self.fnameTB = Entry(self.parent)
        self.fnameTB.grid(row=2, column=0, padx=10, pady=5)
        self.lnameLabel = Label(self.parent, text="Last Name" ,bg='yellow',fg='black').grid(row=1, column=2, padx=10, pady=5)
        self.lnameTB = Entry(self.parent)
        self.lnameTB.grid(row=2, column=2, padx=10, pady=5)
        self.ssnLabel = Label(self.parent, text="SSN", bg='yellow',fg='black').grid(row=5, column=0, padx=10, pady=5)
        self.ssnTB = Entry(self.parent)
        self.ssnTB.grid(row=6, column=0, padx=10, pady=5)
        self.addressLabel = Label(self.parent, text="Street Address", bg='yellow',fg='black',).grid(row=7, column=0, padx=10, pady=5)
        self.addressTB = Entry(self.parent)
        self.addressTB.grid(row=8, column=0, padx=10, pady=5)
        self.cityLabel = Label(self.parent, text="City", bg='yellow',fg='black').grid(row=7, column=2, padx=10, pady=5)
        self.cityTB = Entry(self.parent)
        self.cityTB.grid(row=8, column=2, padx=10, pady=5)
        self.stateLabel = Label(self.parent, text="State", bg='yellow',fg='black').grid(row=7, column=4, padx=10, pady=5)
        self.stateTB = Entry(self.parent)
        self.stateTB.grid(row=8, column=4, padx=10, pady=5)
        self.numberLabel = Label(self.parent, text="Phone Number", bg='yellow',fg='black').grid(row=13, column=0, padx=10, pady=5)
        self.numberTB = Entry(self.parent)
        self.numberTB.grid(row=14, column=0, padx=10, pady=5)
        self.addBtn = Button(self.parent, text=" Add New Entry ",bg='blue',fg='white', command=self.add_borrower)
        self.addBtn.grid(row=15, column = 2, padx=10, pady=5, sticky=N+S+E+W)

    def add_borrower(self):
        ssn = self.ssnTB.get()
        cursor = my_conn.cursor()
        cursor.execute("select exists(select Ssn from borrower where borrower.ssn = '" + str(ssn) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            address = ', '.join([self.addressTB.get(), self.cityTB.get(), self.stateTB.get()])
            name_new = ' '.join([self.fnameTB.get(), self.lnameTB.get()])
            cursor.execute("Insert into borrower (ssn, bname, address, phone) Values ('" + str(ssn) + "', '" + str(name_new) + "', '" + str(address) + "', '" + str(self.numberTB.get()) + "')" )
            my_conn.commit()
            messagebox.showinfo(" ", "Borrower Added")
            borrower_count += 1
            self.parent.destroy()
        else:
            messagebox.showinfo(" ", "Borrower Already Exists!")


class PayFines:
    def __init__(self, master):
        self.parent = master

        self.v = StringVar()

        self.borrowerLabel = Label(self.parent, text="Enter Borrower ID", bg='yellow', font=('Calibri', 10)).grid(row=0, column=0, padx=20, pady=20)
        self.borrowerEntry = Entry(self.parent)
        self.borrowerEntry.grid(row=1, column=0, padx=20, pady=20)
        self.showFineBtn = Button(self.parent, text="Show Fines",bg='blue',fg='white', command=self.show_fines).grid(row=2, column=0, padx=20, pady=20)
        self.fineLabel = Label(self.parent, textvariable=self.v, bg='yellow')
        self.fineLabel.grid(row=3, column=0, padx=20, pady=20)
        self.payFineBtn = Button(self.parent, text="Pay Fine",bg='blue',fg='white', command=self.pay_fine).grid(row=4, column=0, padx=20, pady=20)

    def show_fines(self):
        borrower_id = int(self.borrowerEntry.get())
        cursor = my_conn.cursor()
        cursor.execute("select exists(select card_id from borrower where borrower.card_id = '" + str(borrower_id) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            messagebox.showinfo(" ", "Borrower does not exist in data")
        else:
            cursor.execute("select fines.fine_amt, fines.paid from fines JOIN book_loans ON fines.loan_id = book_loans.loan_id where book_loans.card_id = '" + str(borrower_id) + "'")
            result = cursor.fetchall()
            total_fine = 0
            for elem in result:
                if elem[1] == 0:
                    total_fine += float(elem[0])

        self.v.set("Fine amount: $ " + str(total_fine))

    def pay_fine(self):
        borrower_id = self.borrowerEntry.get()
        cursor = my_conn.cursor()
        cursor.execute(
            "select exists(select card_id from borrower where borrower.card_id = '" + str(borrower_id) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            messagebox.showinfo(" ", "Borrower does not exist in data")
        else:
            cursor = my_conn.cursor()
            cursor.execute(
                "select fines.loan_id from fines JOIN book_loans ON fines.loan_id = book_loans.loan_id where book_loans.card_id = '" + str(
                    borrower_id) + "'")
            result = cursor.fetchall()
            for elem in result:
                cursor = my_conn.cursor()
                cursor.execute("update fines set paid = 'TRUE' where fines.loan_id = '" + str(elem[0]) + "'")
                my_conn.commit()
            messagebox.showinfo("", "Fines Paid!")
            self.parent.destroy()

if __name__ == '__main__':
    root = Tk()
    tool = GUI(root)
    root.mainloop()
