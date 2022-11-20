import sqlite3


def execute_sql(query_string, data=None):
    """
    executes a given query
    :param query_string: string containing an SQL command
    :param data: a list of data for INSERT queries
    :return: a result set of SELECT query on Success or one of the following codes:
        -1 on error
        0 on empty result set
        1 on success of queries other than SELECT
    """
    # create a database connection object
    db = sqlite3.connect('ebookstore')

    try:
        # create a cursor object to execute SQL
        cursor = db.cursor()

        # execute relevant query depending on query_string
        if query_string[0:6] == "SELECT":
            cursor.execute(query_string)
            result = cursor.fetchall()
            if len(result) == 0:
                return 0
            else:
                print(f"SUCCESS: {query_string}")
                display_result(result)
                return result

        elif data:
            cursor.executemany(query_string, data)
            db.commit()
            print(f"SUCCESS: {query_string}")
            return 1

        else:
            cursor.execute(query_string)
            db.commit()
            print(f"SUCCESS: {query_string}")
            return 1

    except Exception as e:
        db.rollback()
        print(e)
        return -1
    finally:
        db.close()


def create_test_table():
    """
    creates and populates books table with sample data for the application

    """
    # create books table and if successful populate
    create_books_table = "CREATE TABLE IF NOT EXISTS books (id int(6) PRIMARY KEY, Title VARCHAR(30)," \
                         " Author VARCHAR(30), quantity int(4))"
    result = execute_sql(create_books_table)

    # result == 1 if table is created or present
    if result == 1:
        data = [(3001, "A Tale of Two Cities", "Charles Dickens", 30),
                (3002, "Harry Potter and the Philosopher's Stone", "J.K. Rowling", 40),
                (3003, "The Lion, the Witch and the Wardrobe", "C.S. Lewis", 25),
                (3004, "The Lord of the Rings", "J.R.R. Tolkien", 37),
                (3005, "Alice in Wonderland", "Lewis Carroll", 12)]
        execute_sql("INSERT INTO books(id, Title, Author, quantity) VALUES(?,?,?,?)", data)


def display_result(result_set):
    """
    formats and displays query result set
    :param result_set: result set provided by a query
    """
    # if result_set does not contain 4 elements per row return nothing
    if len(result_set[0]) != 4:
        return
    print(f"{'ID':<6}  {'Title':<40}  {'Author':<30}  {'Quantity':<12}")
    print("-" * 91)
    for row in result_set:
        print(f"""{row[0]:<6}  {row[1][0:40]:<40}  {row[2][0:30]:<30}  {row[3]:<12}""")


def delete_book():
    """
    deletes a given book
    :return: True on success or False on Failure
    """
    # ask the user to search for the book to delete
    print("First Search for a book to delete ('C' to cancel):")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "c":
            return False
        elif user_input == "":
            print("You have not typed anything in. Try again.")
        else:
            search_result = search_books(user_input)
            # only proceed to update if search result yields 1 result
            if search_result == 0 or search_result == -1:
                print("Search yielded no results. Try again.")
            elif len(search_result) != 1:
                print("You can only proceed with the update if search yields 1 result.")
            else:
                break

    # store elements of the search result in temp variables
    id = search_result[0][0]

    # ask for confirmation
    print("Are you sure you want to delete this book's data? ('Y' or 'N')")
    confirmation = input("> ").strip()
    while True:
        if confirmation.lower() == "n":
            return False
        elif confirmation.lower() == "y":
            result = execute_sql("DELETE FROM books WHERE id = " + str(id))
            if result == -1:
                return False
            if result == 1:
                return True
        else:
            print("Enter 'Y' or 'N'.")


def update_book():
    """
    updates a given book
    :return: True on success or False on Failure
    """
    # ask the user to search for the book to update
    print("First Search for a book to update ('C' to cancel):")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "c":
            return False
        elif user_input == "":
            print("You have not typed anything in. Try again.")
        else:
            search_result = search_books(user_input)
            # only proceed to update if search result yields 1 result
            if search_result == 0 or search_result == -1:
                print("Search yielded no results. Try again.")
            elif len(search_result) != 1:
                print("You can only proceed with the update if search yields 1 result.")
            else:
                break

    # store elements of the search result in temp variables
    id = search_result[0][0]
    title = search_result[0][1]
    author = search_result[0][2]
    quantity = search_result[0][3]

    # ask the user what to update and then prompt for and verify new data
    print(f"""What would you like to update?
1. Title
2. Author
3. Quantity
C. Cancel""")
    while True:
        selection = input("> ")
        if selection == "1":
            print("Enter the new title:")
            while True:
                user_input = input("> ")
                if user_input == "":
                    print("Title cannot be empty.")
                elif user_input.lower() == 'c':
                    return False
                else:
                    title = user_input
                    break
            break
        elif selection == "2":
            print("Enter the new author:")
            while True:
                user_input = input("> ")
                if user_input == "":
                    print("Author cannot be empty.")
                elif user_input.lower() == 'c':
                    return False
                else:
                    author = user_input
                    break
            break
        elif selection == "3":
            print("Enter the new quantity:")
            while True:
                user_input = input("> ")
                if user_input == "":
                    print("Quantity cannot be empty.")
                elif user_input.lower() == 'c':
                    return False
                elif not user_input.isnumeric():
                    print("Please enter a valid number.")
                elif int(user_input) not in range(0, 10000):
                    print("Quantity must be between 0 and 9999")
                else:
                    quantity = int(user_input)
                    break
            break
        elif selection.lower() == "c":
            return False
        else:
            print("Invalid option.")

    # update database
    result = execute_sql("UPDATE books SET Title = '" + title + "', Author = '" + author + "', Quantity = " +
                         str(quantity) + " WHERE id = " + str(id))
    if result == -1:
        return False
    else:
        return True


def search_books(text=""):
    """
    queries the database for records matching user input and displays the result
    :param text: text to search for if none provided user will be prompted for it
    :return: query result set or nothing on cancel
    """
    if text == "":
        while True:
            query_input = input("Enter text to search for or 'C' to cancel:\n> ").strip()

            if query_input.lower() == "c":
                return
            elif len(query_input) > 20:
                print("The text to search for is too long. Try again.")
            else:
                break
    else:
        query_input = text

    # query database and return result set
    result = execute_sql(
        "SELECT * FROM books WHERE id LIKE '%" + query_input + "%' OR Title LIKE '%" + query_input +
        "%' OR Author LIKE '%" + query_input + "%'")
    return result


def generate_id():
    """
    generates a new ID for books table
    :return: unique ID higher than the current highest ID
    """
    # query the database for all IDs, sort them and return a new ID higher than the highest current ID
    ids = execute_sql("SELECT MAX(id) FROM books")
    if ids != -1 and ids != 0:
        return ids[0][0] + 1
    else:
        return 1


def enter_book():
    """
    allows the user to add a new book to the database
    :return: True on success False on failure
    """
    # generate book ID
    book_id = generate_id()

    # get book title from the user
    print("Enter Book Title or 'C' to cancel:")
    while True:
        title = input("> ").strip()
        if title == "":
            print("Title cannot be empty. Try again.")
        elif title.lower() == "c":
            return False
        else:
            break

    # get author from the user
    print("Enter Author or 'C' to cancel:")
    while True:
        author = input("> ").strip()
        if author == "":
            print("Author cannot be empty. Try again.")
        elif author.lower() == "c":
            return False
        else:
            break

    # get book quantity
    print("Enter Book quantity (0 - 9999) or 'C' to cancel:")
    while True:
        quantity = input("> ").strip()
        if quantity == "":
            print("Quantity cannot be empty. Try again.")
        elif quantity.lower() == "c":
            return False
        elif not quantity.isnumeric():
            print("You need to type in a valid number.")
        elif int(quantity) not in range(0, 10000):
            print("You need a a number between 0 and 9999.")
        else:
            break

    # save a new book in the database
    data = [(book_id, title, author, quantity)]
    result = execute_sql("INSERT INTO books(id, Title, Author, quantity) VALUES(?,?,?,?)", data)
    if result == 1:
        return True


def display_main_menu():
    """
    displays main menu to the user
    """
    print(f"""
1. Enter Book
2. Update Book
3. Delete Book
4. Search Books
0. Exit""")


def main_loop():
    """
    Checks the status of the database and initiates the main loop of the program
    """
    # check if there are any records in the books table
    select_all_query = "SELECT * FROM books"
    result = execute_sql(select_all_query)

    # 0 means there are no data in the table; 1 means some other error occurred
    if result == 0 or result == -1:
        create_test_table()

    # execute appropriate function depending on user selection
    while True:
        display_main_menu()
        selection = input("> ")

        if selection == "1":
            enter_book()
        elif selection == "2":
            update_book()
        elif selection == "3":
            delete_book()
        elif selection == "4":
            search_books()
        elif selection == "0":
            print("Goodbye!")
            exit()


# start program
main_loop()
