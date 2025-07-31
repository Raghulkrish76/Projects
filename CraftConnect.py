#    CRAFT CONNECT - CONSOLE BASED INDIAN HANDICRAFT SHOPPING SYSTEM
import mysql.connector
from datetime import datetime

# ------------------- Database Class ---------------
class DB:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "Root@1234",
            database = "craftconnect"
        )
        self.cursor = self.conn.cursor(dictionary=True)
    def execute(self,query,params = None):
        self.cursor.execute(query,params or ())
        if "select" not in query.lower():
            self.conn.commit()
    def fetchall(self):
        return self.cursor.fetchall()
    def fetchone(self):
        return self.cursor.fetchone()
    def close(self):
        self.cursor.close()
        self.conn.close()

# ---------------------  User  ----------------------
class user:
    def __init__(self,userid,name,email,role):
        self.name = name
        self.id = userid
        self.email = email
        self.role = role
    @staticmethod
    def register():
        db = DB()
        name = input("Enter Name: ")
        email = input("Enter Email: ")
        password = input("Enter password:")
        role = input("Enter Role:")
        db.execute("INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)",(name,email,password,role))
        print("User Registered Successfully")
        db.close()
    @staticmethod
    def login():
        db = DB()
        email = input("Enter email:")
        password = input("Enter password:")
        db.execute("SELECT * FROM users where email = %s AND password = %s",(email,password))
        userdata = db.fetchone()
        db.close()
        if userdata:
            print(f"Welcome {userdata['name']}!")
            return user(userdata['id'],userdata['name'],userdata['email'],userdata['role'])
        else:
            print("Incorrect Email or Password")
            return None
    ''''
    def show_menu(self):
        if self.role == "buyer":
            Cart(self.user_id).buyer_menu()
        else:
            Product(self.user_id).seller_menu() '''

#--------------------------------------PRODUCT CLASS ---------------------------------------------------------

class Product:
    def __init__(self,seller_id):
        self.seller_id = seller_id
    def seller_menu(self):
        while True:
            print("\n1. Add Product\n2. Update Product \n3. Delete Product\n4. Exit")
            choice = input("Select an Option: ")
            if choice == '1':
                self.add_product()
            elif choice == '2':
                self.update_product()
            elif choice == '3':
                self.delete_product()
            elif choice == '4':
                break
    def add_product(self):
        db = DB()
        name = input("Product Name: ")
        category = input("Category: ")
        origin = input("Origin: ")
        price = float(input("Price:"))
        stock = int(input("Stock:"))
        db.execute("INSERT INTO products (pname,category, orgin, price, stock, seller_id) VALUES (%s,%s,%s,%s,%s,%s)"
                   ,(name,category,origin,price,stock,self.seller_id))
        print("Product Added")
        db.close()
    def update_product(self):
        db = DB()
        product_id = input("Product ID to Update: ")
        new_price = float(input("New Price: "))
        new_stock = int(input("New Stock: "))
        db.execute("UPDATE products SET Price = %s, stock = %s WHERE id = %s AND seller_id = %s",
                   (new_price,new_stock,product_id,self.seller_id))
        print("\nTHE PRODUCT HAS BEEN UPDATED !")
        db.close()
    def delete_product(self):
        db = DB()
        product_id = input("Product ID to be deleted: ")
        db.execute("DELETE FROM products WHERE id = %s AND seller_id = %s",
        (product_id,self.seller_id))
        print("\n PRODUCT DELETED SUCESSFULLY !")
        db.close()
    @staticmethod
    def browse_products():
        db = DB()
        db.execute("SELECT * FROM PRODUCTS WHERE stock > 0")
        for i in db.fetchall():
            print(i)
        db.close()
    
#----------------------------------- CART -------------------------------------------------------------------------
class Cart:
    def __init__(self,user_id):
        self.user_id = user_id
    def buyer_menu(self):
        while True:
            print("\n1. Browse Products\n" \
            "2. Add to Cart\n" \
            "3. View Cart\n" \
            "4. Remove From Cart\n" \
            "5. Checkout\n" \
            "6. View Orders\n" \
            "7. Exit")
            choice = input("Enter the choice: ")
            if choice == 1:
                Product.browse_products()
            elif choice == '2':
                self.add_to_cart()
            elif choice == '3':
                self.view_cart()
            elif choice == '4':
                self.remove_from_cart()
            elif choice == '5':
                self.checkout()
            elif choice == '6':
                self.view_orders()
            elif choice == '7':
                print("Exited Successfully !")
                break
    def add_to_cart(self):
        db = DB()
        product_id = input("Product ID: ")
        quantity = int(input("Enter Quantity: "))
        db.execute("INSERT INTO cart (user_id,product_id, quantity) VALUES (%s,%s,%s)", 
        (self.user_id,product_id,quantity))
        print("✔ Item Added to Cart Sucessfully !")
    def view_cart(self):
        db = DB()
        db.execute("SELECT c.id,p.pname,c.quantity,p.price from cart c JOIN products p ON c.product_id = p.id WHERE c.user_id = %s",
                   (self.user_id,))
        for item in db.fetchall():
            print(item)
        db.close()
    def remove_from_cart(self):
        db = DB()
        cart_id = input("ID of the Item to remvoe: ")
        db.execute("DELETE FROM cart WHERE id = %s AND user_id =%s",(cart_id,self.user_id))
        print("Remove From Cart !")
        db.close()
    def checkout(self):
        db = DB()
        db.execute("SELECT c.product_id,c.quantity, p.price, p.stock from CART C JOIN products p ON c.product_id = p.id WHERE c.user_id = %s",(self.user_id,))
        items = db.fetchall()
        if not items:
            print("Cart is Empty.")
            return
        total = sum(item['price']*item['quantity'] for item in items)
        db.execute("INSERT INTO orders (user_id,total_amount,order_date) VALUES (%s,%s,%s)",
                   (self.user_id,total,datetime.now()))
        order_id = db.cursor.lastrowid
        for item in items:
            db.execute("INSERT INTO order_items (order_id,product_id,quantity,price) VALUES (%s,%s,%s,%s)",
                       (order_id,item['product_id'],item['quantity'],item['price']))
            db.execute("UPDATE products SET stock = stock- %s WHERE id  = %s",
                       (item['quantity'],item['product_id']))
        db.execute("DELETE FROM cart WHERE user_id = %s",(self.user_id,))
        print(f"Order Placed Sucessflly! ")
        print(f"Total Amount: {total}")
    
# ------------------------------ Order ---------------------------------------------
class Order:
    @staticmethod
    def view_orders(user_id):
        db = DB()
        db.execute("SELECT * FROM orders WHERE user_id = %s",(user_id,))
        for order in db.fetchall():
            print(f"Order ID: {order['odrid']} Amount: {order['total_amount']} Date: {order['order_date']}")
        db.close()



# ------------------------------- MAIN -------------------------------------------------
def main():
    while True:
        print("\n ---- Craft Connect -----")
        print("1. Register\n2. Login\n 3.Exit")
        choice = input("Choos an Option: ")
        if choice == '1':
            user.register()
        elif choice == '2':
            useri = user.login()
            if useri:
                user.show_menu()
        elif choice == '3':
            break
if __name__ == "__main__":
    main()
