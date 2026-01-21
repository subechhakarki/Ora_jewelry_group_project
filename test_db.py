# test_db.py

from db.database import init_database

if __name__ == "__main__":
    print("🚀 Initializing ORA Jewelry Database...")
    init_database()
    print("\n✅ Database setup complete!")
    print("📁 Database file created: ora_jewelry.db")