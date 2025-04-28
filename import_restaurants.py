import csv
import os
from app import create_app
from app.models import db, Restaurant

def import_restaurants_from_csv():
    app = create_app()
    
    with app.app_context():
        # Check existing restaurants count
        existing_count = Restaurant.query.count()
        print(f"Current restaurant count: {existing_count}")
        
        # Delete existing restaurants for a fresh import
        if existing_count > 0:
            print("Database already has restaurants. Do you want to delete existing records and reimport? (y/n)")
            response = input().lower()
            if response == 'y':
                Restaurant.query.delete()
                db.session.commit()
                print(f"Deleted {existing_count} existing restaurants.")
            else:
                print("Import cancelled.")
                return
        
        # Path to CSV file
        csv_file = 'restaurants.csv'
        
        # Check if file exists
        if not os.path.exists(csv_file):
            print(f"ERROR: CSV file not found at {csv_file}")
            return
        
        # Get CSV file size
        file_size = os.path.getsize(csv_file)
        print(f"CSV file size: {file_size/1024:.2f} KB")
        
        # Import data
        imported = 0
        errors = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Try to detect the header format and column names
                sample = f.read(1024)
                f.seek(0)  # Reset file pointer
                
                # Create a dialect sniffer
                dialect = csv.Sniffer().sniff(sample)
                has_header = csv.Sniffer().has_header(sample)
                
                print(f"CSV dialect: {dialect.delimiter}")
                print(f"Has header: {has_header}")
                
                # Read the file with reader and get header row
                reader = csv.reader(f, dialect)
                headers = next(reader)
                print(f"Detected headers: {headers}")
                
                # Prepare header mapping
                header_map = {}
                for i, header in enumerate(headers):
                    clean_header = header.strip().lower()
                    if 'name' in clean_header:
                        header_map['name'] = i
                    elif 'location' in clean_header:
                        header_map['location'] = i
                    elif 'locality' in clean_header:
                        header_map['locality'] = i
                    elif 'city' in clean_header:
                        header_map['city'] = i
                    elif 'cuisine' in clean_header:
                        header_map['cuisine'] = i
                    elif 'rating' in clean_header:
                        header_map['rating'] = i
                    elif 'votes' in clean_header:
                        header_map['votes'] = i
                    elif 'cost' in clean_header:
                        header_map['cost'] = i
                
                print(f"Header mapping: {header_map}")
                
                # Process rows
                for i, row in enumerate(reader):
                    try:
                        # Create new restaurant
                        restaurant = Restaurant(
                            name=row[header_map.get('name', 0)].strip(),
                            location=row[header_map.get('location', 1)].strip() if 'location' in header_map else '',
                            locality=row[header_map.get('locality', 2)].strip() if 'locality' in header_map else '',
                            city=row[header_map.get('city', 3)].strip() if 'city' in header_map else '',
                            cuisine=row[header_map.get('cuisine', 4)].strip() if 'cuisine' in header_map else '',
                            rating=float(row[header_map.get('rating', 5)]) if row[header_map.get('rating', 5)] else 0,
                            votes=int(row[header_map.get('votes', 6)]) if row[header_map.get('votes', 6)] else 0,
                            cost=int(row[header_map.get('cost', 7)]) if row[header_map.get('cost', 7)] else 0
                        )
                        
                        db.session.add(restaurant)
                        imported += 1
                        
                        # Commit in batches to avoid memory issues
                        if imported % 500 == 0:
                            db.session.commit()
                            print(f"Imported {imported} restaurants so far...")
                        
                    except Exception as e:
                        errors += 1
                        if errors < 10:  # Only show first 10 errors
                            print(f"Error importing row {i+1}: {str(e)}")
                            print(f"Row data: {row}")
                        
                # Final commit
                db.session.commit()
        
        except Exception as e:
            print(f"Error processing CSV: {str(e)}")
            return
        
        # Final count
        new_count = Restaurant.query.count()
        print(f"Import completed:")
        print(f"- Imported: {imported} restaurants")
        print(f"- Errors: {errors}")
        print(f"- Previous count: {existing_count}")
        print(f"- New count: {new_count}")

if __name__ == "__main__":
    import_restaurants_from_csv() 