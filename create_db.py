from app import create_app
from app.models import db, User, Restaurant, SuggestedRestaurant

def create_database():
    # Create Flask app
    app = create_app()
    
    # Create database tables in app context
    with app.app_context():
        # Drop all tables if they exist
        db.drop_all()
        
        # Create all tables based on models
        db.create_all()
        
        print("Database tables created successfully!")
        
        # Show all tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        print("Tables created:")
        for table_name in inspector.get_table_names():
            print(f"- {table_name}")
            # Show columns
            print("  Columns:")
            for column in inspector.get_columns(table_name):
                print(f"  - {column['name']}: {column['type']}")

if __name__ == "__main__":
    create_database() 