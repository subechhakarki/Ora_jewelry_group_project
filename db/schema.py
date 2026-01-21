# db/schema.py

from db.database import get_connection, close_connection

def create_tables():
    """
    Create all database tables for the ORA Jewelry Store.
    Tables: Users, Products, Cart, Sales
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # ============================================
    # 1. USERS TABLE (UPDATED WITH SALT COLUMN)
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            user_email TEXT UNIQUE NOT NULL,
            user_password TEXT NOT NULL,
            user_salt TEXT NOT NULL,  -- Added for password hashing
            user_role TEXT NOT NULL CHECK(user_role IN ('admin', 'user')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ============================================
    # 2. PRODUCTS TABLE
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_price REAL NOT NULL CHECK(product_price >= 0),
            product_quantity INTEGER NOT NULL CHECK(product_quantity >= 0),
            product_image TEXT,
            product_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ============================================
    # 3. CART TABLE
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_quantity INTEGER NOT NULL CHECK(product_quantity > 0),
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            UNIQUE(user_id, product_id)
        )
    ''')
    
    # ============================================
    # 4. SALES TABLE (Orders)
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            sale_quantity INTEGER NOT NULL CHECK(sale_quantity > 0),
            total_price REAL NOT NULL CHECK(total_price >= 0),
            order_status TEXT NOT NULL CHECK(order_status IN ('on-going', 'delivering', 'finished', 'cancelled')),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    print("✅ All tables created successfully!")
    
    # Create default admin user if not exists
    create_default_admin(cursor, conn)
    
    close_connection(conn)

def create_default_admin(cursor, conn):
    """
    Create a default admin user with hashed password
    Email: admin@ora.com
    Password: admin123
    """
    cursor.execute("SELECT * FROM users WHERE user_email = ?", ('admin@ora.com',))
    if not cursor.fetchone():
        # Import security module
        from utils.security import hash_password
        
        # Hash the default password
        hashed_password, salt = hash_password('admin123')
        
        cursor.execute('''
            INSERT INTO users (user_name, user_email, user_password, user_salt, user_role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin', 'admin@ora.com', hashed_password, salt, 'admin'))
        conn.commit()
        print("✅ Default admin user created!")
        print("   Email: admin@ora.com")
        print("   Password: admin123 (hashed)")

def drop_all_tables():
    """
    WARNING: This will delete all tables and data!
    Use only for development/testing.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("DROP TABLE IF EXISTS cart")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS users")
    
    conn.commit()
    close_connection(conn)
    print("⚠️ All tables dropped!")