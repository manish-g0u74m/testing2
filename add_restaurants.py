import csv
import os
from app import create_app
from app.models import db, Restaurant

def add_restaurants_from_csv():
    app = create_app()
    
    with app.app_context():
        # Check existing restaurants count
        existing_count = Restaurant.query.count()
        print(f"Current restaurant count: {existing_count}")
        
        # Path to CSV file
        csv_file = 'restaurants.csv'
        
        # Check if file exists
        if not os.path.exists(csv_file):
            print(f"ERROR: CSV file not found at {csv_file}")
            return
        
        # Import data
        imported = 0
        skipped = 0
        errors = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Get header row
                csv_reader = csv.reader(f)
                headers = next(csv_reader)
                print(f"Headers: {headers}")
                
                # Process rows
                for i, row in enumerate(csv_reader):
                    try:
                        # Check if restaurant already exists
                        if len(row) < 4:  # Skip invalid rows
                            skipped += 1
                            continue
                            
                        name = row[0].strip()
                        city = row[3].strip() if len(row) > 3 else ""
                        
                        exists = Restaurant.query.filter(
                            Restaurant.name.ilike(name),
                            Restaurant.city.ilike(city)
                        ).first()
                        
                        if exists:
                            skipped += 1
                            continue
                        
                        # Create new restaurant
                        restaurant = Restaurant(
                            name=name,
                            location=row[1].strip() if len(row) > 1 else "",
                            locality=row[2].strip() if len(row) > 2 else "",
                            city=city,
                            cuisine=row[4].strip() if len(row) > 4 else "",
                            rating=float(row[5]) if len(row) > 5 and row[5] else 0,
                            votes=int(row[6]) if len(row) > 6 and row[6] else 0,
                            cost=int(row[7]) if len(row) > 7 and row[7] else 0
                        )
                        
                        db.session.add(restaurant)
                        imported += 1
                        
                        # Commit in batches to avoid memory issues
                        if imported % 100 == 0:
                            db.session.commit()
                            print(f"Imported {imported} restaurants so far...")
                        
                    except Exception as e:
                        errors += 1
                        if errors < 5:  # Only show first 5 errors
                            print(f"Error importing row {i+1}: {str(e)}")
                
                # Final commit
                db.session.commit()
        
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()
            return
        
        # Final count
        new_count = Restaurant.query.count()
        print(f"Import completed:")
        print(f"- Added: {imported} new restaurants")
        print(f"- Skipped: {skipped} (already exist or invalid)")
        print(f"- Errors: {errors}")
        print(f"- Previous count: {existing_count}")
        print(f"- New count: {new_count}")

if __name__ == "__main__":
    add_restaurants_from_csv() 