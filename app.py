import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib 

# --- 数据库连接配置 ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  
    'password': '040926lkb.',  
    'database': 'secondhand_bookstore_db'
}

# --- 数据库操作模块 ---
class DBConnector:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True) # dictionary=True 让查询结果为字典
            print("数据库连接成功")
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("数据库错误", f"连接失败: {err}")
            print(f"数据库连接失败: {err}")
            return False

    def disconnect(self):
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("数据库连接已关闭")

    def execute_query(self, query, params=None):
        if not self.conn or not self.conn.is_connected():
            if not self.connect(): 
                return None
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("查询错误", f"错误: {err}")
            print(f"查询错误: {err}")
            return None

    def execute_non_query(self, query, params=None):
        if not self.conn or not self.conn.is_connected():
            if not self.connect(): 
                return False
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("操作失败", f"错误: {err}")
            print(f"操作失败: {err}")
            return False

    def get_last_inserted_id(self):
        return self.cursor.lastrowid

# --- 密码哈希 ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- 主应用类 ---
class App(tk.Tk):
    def __init__(self, db_connector):
        super().__init__()
        self.db = db_connector
        self.title("校园二手书交易平台")
        self.geometry("800x600")

        self.current_user_id = None
        self.current_username = None

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)

        # 登录/注册标签页
        self.auth_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.auth_frame, text='登录/注册')
        self.create_auth_widgets(self.auth_frame)

        # 书籍浏览标签页
        self.browse_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.browse_frame, text='浏览书籍')
        self.create_browse_widgets(self.browse_frame)

        # 发布书籍标签页 (登录后可见)
        self.sell_frame = ttk.Frame(self.notebook)
       
        self.create_sell_widgets(self.sell_frame)

        # 我的订单标签页 (登录后可见)
        self.orders_frame = ttk.Frame(self.notebook)
       
        self.create_orders_widgets(self.orders_frame)
        
        # 我的书籍标签页 (登录后可见)
        self.my_books_frame = ttk.Frame(self.notebook)
        self.create_my_books_widgets(self.my_books_frame)

        self.notebook.pack(expand=1, fill='both')
        
        self.status_bar = ttk.Label(self, text="未登录", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_auth_widgets(self, parent_frame):
        auth_container = ttk.LabelFrame(parent_frame, text="用户认证")
        auth_container.pack(padx=10, pady=10, fill='x')

        # 登录部分
        login_frame = ttk.Frame(auth_container)
        login_frame.pack(pady=5, fill='x')
        ttk.Label(login_frame, text="用户名:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.login_username_entry = ttk.Entry(login_frame, width=30)
        self.login_username_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(login_frame, text="密码:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.login_password_entry = ttk.Entry(login_frame, show="*", width=30)
        self.login_password_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(login_frame, text="登录", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Separator(auth_container, orient='horizontal').pack(fill='x', pady=10)

        # 注册部分
        reg_frame = ttk.Frame(auth_container)
        reg_frame.pack(pady=5, fill='x')
        ttk.Label(reg_frame, text="用户名:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.reg_username_entry = ttk.Entry(reg_frame, width=30)
        self.reg_username_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(reg_frame, text="密码:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.reg_password_entry = ttk.Entry(reg_frame, show="*", width=30)
        self.reg_password_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(reg_frame, text="确认密码:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.reg_confirm_password_entry = ttk.Entry(reg_frame, show="*", width=30)
        self.reg_confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(reg_frame, text="邮箱:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.reg_email_entry = ttk.Entry(reg_frame, width=30)
        self.reg_email_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(reg_frame, text="注册", command=self.register).grid(row=4, column=0, columnspan=2, pady=10)
        
        self.logout_button = ttk.Button(auth_container, text="退出登录", command=self.logout, state=tk.DISABLED)
        self.logout_button.pack(pady=10)

    def login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()
        if not username or not password:
            messagebox.showerror("登录失败", "用户名和密码不能为空")
            return

        hashed_password = hash_password(password)
        query = "SELECT user_id, username FROM Users WHERE username = %s AND password_hash = %s"
        user = self.db.execute_query(query, (username, hashed_password))

        if user:
            self.current_user_id = user[0]['user_id']
            self.current_username = user[0]['username']
            messagebox.showinfo("登录成功", f"欢迎, {self.current_username}!")
            self.login_username_entry.delete(0, tk.END)
            self.login_password_entry.delete(0, tk.END)
            self.update_ui_after_login()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()
        email = self.reg_email_entry.get()

        if not all([username, password, confirm_password, email]):
            messagebox.showerror("注册失败", "所有字段均为必填项")
            return
        if password != confirm_password:
            messagebox.showerror("注册失败", "两次输入的密码不一致")
            return
        
        # 检查用户名或邮箱是否已存在
        check_query = "SELECT user_id FROM Users WHERE username = %s OR email = %s"
        existing_user = self.db.execute_query(check_query, (username, email))
        if existing_user:
            messagebox.showerror("注册失败", "用户名或邮箱已被注册")
            return

        hashed_password = hash_password(password)
        query = "INSERT INTO Users (username, password_hash, email, registration_date) VALUES (%s, %s, %s, NOW())"
        if self.db.execute_non_query(query, (username, hashed_password, email)):
            messagebox.showinfo("注册成功", "用户注册成功，请登录")
            self.reg_username_entry.delete(0, tk.END)
            self.reg_password_entry.delete(0, tk.END)
            self.reg_confirm_password_entry.delete(0, tk.END)
            self.reg_email_entry.delete(0, tk.END)
        else:
            messagebox.showerror("注册失败", "注册过程中发生错误")
            
    def logout(self):
        self.current_user_id = None
        self.current_username = None
        messagebox.showinfo("退出登录", "您已成功退出登录")
        self.update_ui_after_logout()

    def update_ui_after_login(self):
        self.status_bar.config(text=f"已登录: {self.current_username}")
        self.logout_button.config(state=tk.NORMAL)
        try:
            self.notebook.add(self.sell_frame, text='发布书籍')
            self.notebook.add(self.orders_frame, text='我的订单')
            self.notebook.add(self.my_books_frame, text='我的书籍')
        except tk.TclError: # 防止重复添加
            pass
        self.load_my_books() # 登录后加载我的书籍
        self.load_my_orders() # 登录后加载我的订单

    def update_ui_after_logout(self):
        self.status_bar.config(text="未登录")
        self.logout_button.config(state=tk.DISABLED)
        try:
            self.notebook.hide(self.notebook.index(self.sell_frame))
            self.notebook.hide(self.notebook.index(self.orders_frame))
            self.notebook.hide(self.notebook.index(self.my_books_frame))
        except tk.TclError:
            pass
        # 清空登录后才显示的内容
        if hasattr(self, 'my_books_tree'):
            for item in self.my_books_tree.get_children():
                self.my_books_tree.delete(item)
        if hasattr(self, 'orders_tree'):
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)

    def create_browse_widgets(self, parent_frame):
        browse_container = ttk.LabelFrame(parent_frame, text="书籍市场")
        browse_container.pack(padx=10, pady=10, fill='both', expand=True)

        search_frame = ttk.Frame(browse_container)
        search_frame.pack(fill='x', pady=5)
        ttk.Label(search_frame, text="搜索书名:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="搜索", command=self.search_books).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="刷新列表", command=self.load_available_books).pack(side=tk.LEFT, padx=5)

        cols = ('ID', '书名', '作者', '价格', '分类', '卖家', '发布日期')
        self.books_tree = ttk.Treeview(browse_container, columns=cols, show='headings', selectmode='browse')
        for col in cols:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100, anchor='center')
        self.books_tree.column('书名', width=200)
        self.books_tree.pack(fill='both', expand=True, pady=5)
        self.books_tree.bind('<<TreeviewSelect>>', self.on_book_select_for_purchase)

        self.purchase_button = ttk.Button(browse_container, text="购买选中书籍", command=self.purchase_selected_book, state=tk.DISABLED)
        self.purchase_button.pack(pady=10)

        self.load_available_books()

    def load_available_books(self, search_term=None):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        query = """
            SELECT b.book_id, b.title, b.author, b.price, c.name as category_name, u.username as seller_name, b.publish_date
            FROM Books b
            JOIN Categories c ON b.category_id = c.category_id
            JOIN Users u ON b.seller_id = u.user_id
            WHERE b.status = 'available'  # 确保书籍状态为可售
        """
        params = []
        if search_term:
            query += " AND b.title LIKE %s"
            params.append(f"%{search_term}%")
        query += " ORDER BY b.publish_date DESC"

        books = self.db.execute_query(query, tuple(params) if params else None)
        if books:
            for book in books:
                self.books_tree.insert('', tk.END, values=(
                    book['book_id'], book['title'], book['author'], f"{book['price']:.2f}", 
                    book['category_name'], book['seller_name'], book['publish_date'].strftime('%Y-%m-%d %H:%M')
                ))

    def search_books(self):
        search_term = self.search_entry.get()
        self.load_available_books(search_term)

    def on_book_select_for_purchase(self, event):
        if not self.current_user_id:
            messagebox.showwarning("提示", "请先登录再进行购买操作。")
            self.purchase_button.config(state=tk.DISABLED)
            # 清除选择，避免未登录时按钮仍可点击的错觉
            if self.books_tree.selection():
                self.books_tree.selection_remove(self.books_tree.selection()[0])
            return
        
        selected_item = self.books_tree.selection()
        if selected_item:
            book_id = self.books_tree.item(selected_item[0])['values'][0]
            seller_name = self.books_tree.item(selected_item[0])['values'][5]
            # 不能购买自己发布的书籍
            if self.current_username == seller_name:
                self.purchase_button.config(state=tk.DISABLED)
                messagebox.showinfo("提示", "您不能购买自己发布的书籍。")
            else:
                self.purchase_button.config(state=tk.NORMAL)
        else:
            self.purchase_button.config(state=tk.DISABLED)

    def purchase_selected_book(self):
        if not self.current_user_id:
            messagebox.showerror("错误", "请先登录!")
            return

        selected_item = self.books_tree.selection()
        if not selected_item:
            messagebox.showerror("错误", "请选择一本书籍进行购买!")
            return

        book_values = self.books_tree.item(selected_item[0])['values']
        book_id = book_values[0]
        book_title = book_values[1]
        book_price = float(book_values[3])
        seller_name = book_values[5]

        if self.current_username == seller_name:
            messagebox.showinfo("提示", "您不能购买自己发布的书籍。")
            return

        confirm = messagebox.askyesno("确认购买", f"您确定要购买《{book_title}》吗？\n价格: {book_price:.2f}元")
        if confirm:
            # 1. 创建订单
            order_query = "INSERT INTO Orders (buyer_id, total_amount, status, order_date) VALUES (%s, %s, %s, NOW())"
            if self.db.execute_non_query(order_query, (self.current_user_id, book_price, 'paid')):
                order_id = self.db.get_last_inserted_id()
                # 2. 创建订单项
                order_item_query = "INSERT INTO Order_Items (order_id, book_id, quantity, price_at_purchase) VALUES (%s, %s, %s, %s)"
                if self.db.execute_non_query(order_item_query, (order_id, book_id, 1, book_price)):
                    # 3. 更新书籍状态为 'sold'
                    update_book_query = "UPDATE Books SET status = 'sold' WHERE book_id = %s"
                    if self.db.execute_non_query(update_book_query, (book_id,)):
                        messagebox.showinfo("购买成功", f"《{book_title}》购买成功！")
                        self.load_available_books() # 刷新书籍列表
                        self.load_my_orders() # 刷新我的订单
                    else:
                        messagebox.showerror("错误", "更新书籍状态失败，但订单已创建部分。请联系管理员。")
                else:
                    messagebox.showerror("错误", "创建订单项失败。请联系管理员。")
            else:
                messagebox.showerror("错误", "创建订单失败。")

    def create_sell_widgets(self, parent_frame):
        sell_container = ttk.LabelFrame(parent_frame, text="发布您的二手书")
        sell_container.pack(padx=10, pady=10, fill='x')

        ttk.Label(sell_container, text="书名:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sell_title_entry = ttk.Entry(sell_container, width=50)
        self.sell_title_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sell_container, text="作者:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.sell_author_entry = ttk.Entry(sell_container, width=50)
        self.sell_author_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sell_container, text="ISBN:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.sell_isbn_entry = ttk.Entry(sell_container, width=50)
        self.sell_isbn_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sell_container, text="出版社:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.sell_publisher_entry = ttk.Entry(sell_container, width=50)
        self.sell_publisher_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(sell_container, text="出版日期 (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.sell_pub_date_entry = ttk.Entry(sell_container, width=50)
        self.sell_pub_date_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sell_container, text="价格 (元):" ).grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.sell_price_entry = ttk.Entry(sell_container, width=20)
        self.sell_price_entry.grid(row=5, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(sell_container, text="分类:").grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.sell_category_combobox = ttk.Combobox(sell_container, width=47, state='readonly')
        self.sell_category_combobox.grid(row=6, column=1, padx=5, pady=5, sticky='ew')
        self.load_categories_for_sell()

        ttk.Label(sell_container, text="品相描述:").grid(row=7, column=0, padx=5, pady=5, sticky='nw')
        self.sell_condition_text = tk.Text(sell_container, width=50, height=3)
        self.sell_condition_text.grid(row=7, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sell_container, text="书籍描述:").grid(row=8, column=0, padx=5, pady=5, sticky='nw')
        self.sell_description_text = tk.Text(sell_container, width=50, height=5)
        self.sell_description_text.grid(row=8, column=1, padx=5, pady=5, sticky='ew')

        ttk.Button(sell_container, text="确认发布", command=self.publish_book).grid(row=9, column=0, columnspan=2, pady=10)
        
        sell_container.columnconfigure(1, weight=1) 

    def load_categories_for_sell(self):
        query = "SELECT category_id, name FROM Categories ORDER BY name"
        categories = self.db.execute_query(query)
        if categories:
            self.category_map = {cat['name']: cat['category_id'] for cat in categories}
            self.sell_category_combobox['values'] = [cat['name'] for cat in categories]
            if self.sell_category_combobox['values']:
                 self.sell_category_combobox.current(0)
        else:
            self.sell_category_combobox['values'] = []
            self.category_map = {}

    def publish_book(self):
        if not self.current_user_id:
            messagebox.showerror("错误", "请先登录再发布书籍!")
            return

        title = self.sell_title_entry.get()
        author = self.sell_author_entry.get()
        isbn = self.sell_isbn_entry.get()
        publisher = self.sell_publisher_entry.get()
        pub_date_str = self.sell_pub_date_entry.get() 
        price_str = self.sell_price_entry.get()
        category_name = self.sell_category_combobox.get()
        condition = self.sell_condition_text.get("1.0", tk.END).strip()
        description = self.sell_description_text.get("1.0", tk.END).strip()

        if not all([title, price_str, category_name]):
            messagebox.showerror("发布失败", "书名、价格和分类为必填项!")
            return
        
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("价格必须大于0")
        except ValueError as e:
            messagebox.showerror("发布失败", f"价格无效: {e}")
            return

        category_id = self.category_map.get(category_name)
        if not category_id:
            messagebox.showerror("发布失败", "无效的书籍分类")
            return
            
        # ISBN 唯一性检查 
        if isbn:
            check_isbn_query = "SELECT book_id FROM Books WHERE isbn = %s"
            existing_book = self.db.execute_query(check_isbn_query, (isbn,))
            if existing_book:
                messagebox.showerror("发布失败", f"ISBN '{isbn}' 已存在于数据库中。")
                return

        query = """
            INSERT INTO Books (seller_id, category_id, title, author, isbn, publisher, publication_date, price, description, condition_desc, status, publish_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'available', NOW())
        """
        params = (
            self.current_user_id, category_id, title, author if author else None, 
            isbn if isbn else None, publisher if publisher else None, 
            pub_date_str if pub_date_str else None, 
            price, description if description else None, condition if condition else None
        )

        if self.db.execute_non_query(query, params):
            messagebox.showinfo("成功", "书籍发布成功!")
            # 清空表单
            self.sell_title_entry.delete(0, tk.END)
            self.sell_author_entry.delete(0, tk.END)
            self.sell_isbn_entry.delete(0, tk.END)
            self.sell_publisher_entry.delete(0, tk.END)
            self.sell_pub_date_entry.delete(0, tk.END)
            self.sell_price_entry.delete(0, tk.END)
            self.sell_condition_text.delete("1.0", tk.END)
            self.sell_description_text.delete("1.0", tk.END)
            if self.sell_category_combobox['values']:
                self.sell_category_combobox.current(0)
            self.load_available_books() # 刷新市场列表
            self.load_my_books() # 刷新我的书籍列表
            self.notebook.select(self.browse_frame) # 切换到书籍浏览页面
        else:
            messagebox.showerror("失败", "书籍发布失败，请检查输入或联系管理员。")

    def create_orders_widgets(self, parent_frame):
        orders_container = ttk.LabelFrame(parent_frame, text="我的购买订单")
        orders_container.pack(padx=10, pady=10, fill='both', expand=True)
        
        ttk.Button(orders_container, text="刷新订单列表", command=self.load_my_orders).pack(pady=5)

        cols = ('订单ID', '下单日期', '总金额', '状态', '书籍名称', '购买时价格')
        self.orders_tree = ttk.Treeview(orders_container, columns=cols, show='headings')
        for col in cols:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=120, anchor='center')
        self.orders_tree.column('书籍名称', width=200)
        self.orders_tree.pack(fill='both', expand=True, pady=5)

    def load_my_orders(self):
        if not self.current_user_id:
            return
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        query = """
            SELECT o.order_id, o.order_date, o.total_amount, o.status, 
                   GROUP_CONCAT(b.title SEPARATOR ', ') as book_titles, 
                   GROUP_CONCAT(oi.price_at_purchase SEPARATOR ', ') as item_prices
            FROM Orders o
            JOIN Order_Items oi ON o.order_id = oi.order_id
            JOIN Books b ON oi.book_id = b.book_id
            WHERE o.buyer_id = %s
            GROUP BY o.order_id, o.order_date, o.total_amount, o.status
            ORDER BY o.order_date DESC
        """
        orders = self.db.execute_query(query, (self.current_user_id,))
        if orders:
            for order in orders:
                self.orders_tree.insert('', tk.END, values=(
                    order['order_id'], order['order_date'].strftime('%Y-%m-%d %H:%M'), 
                    f"{order['total_amount']:.2f}", order['status'],
                    order['book_titles'], order['item_prices']
                ))
                
    def create_my_books_widgets(self, parent_frame):
        my_books_container = ttk.LabelFrame(parent_frame, text="我发布的书籍")
        my_books_container.pack(padx=10, pady=10, fill='both', expand=True)
        
        ttk.Button(my_books_container, text="刷新列表", command=self.load_my_books).pack(pady=5)

        cols = ('ID', '书名', '价格', '状态', '发布日期')
        self.my_books_tree = ttk.Treeview(my_books_container, columns=cols, show='headings', selectmode='browse')
        for col in cols:
            self.my_books_tree.heading(col, text=col)
            self.my_books_tree.column(col, width=120, anchor='center')
        self.my_books_tree.column('书名', width=250)
        self.my_books_tree.pack(fill='both', expand=True, pady=5)
        # 可以添加编辑或下架按钮，并绑定事件
      

    def load_my_books(self):
        if not self.current_user_id:
            return
        for item in self.my_books_tree.get_children():
            self.my_books_tree.delete(item)

        query = """
            SELECT book_id, title, price, status, publish_date
            FROM Books
            WHERE seller_id = %s
            ORDER BY publish_date DESC
        """
        books = self.db.execute_query(query, (self.current_user_id,))
        if books:
            for book in books:
                self.my_books_tree.insert('', tk.END, values=(
                    book['book_id'], book['title'], f"{book['price']:.2f}",
                    book['status'], book['publish_date'].strftime('%Y-%m-%d %H:%M')
                ))

# --- 应用入口 ---
if __name__ == "__main__":
    db_connector = DBConnector(DB_CONFIG)
    if db_connector.connect(): # 尝试初始连接
        app = App(db_connector)
        app.mainloop()
        db_connector.disconnect() # 应用关闭时断开连接
    else:
        print("无法启动应用，数据库连接失败。请检查数据库配置和MySQL服务状态。")

def show_books_for_purchase(self):
    self.books_list.delete(0, tk.END)  # 清空旧数据
    # 添加以下刷新逻辑
    books = self.db.get_available_books()
    for book in books:
        self.books_list.insert(tk.END, f"{book[2]} - ¥{book[7]}")