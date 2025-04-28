from app import create_app
from app.models import db
from sqlalchemy import text

def test_rating_filter():
    """Test the rating filter specifically"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n==== TESTING RATING FILTER ====\n")
            
            # 1. Get total count using raw SQL (safe approach)
            result = db.session.execute(text("SELECT COUNT(*) FROM restaurant")).scalar()
            print(f"Total restaurants (SQL): {result}")
            
            # 2. Print distribution of ratings
            print("\nRating distribution:")
            for rating in [0, 1, 2, 3, 3.5, 4, 4.5, 5]:
                count = db.session.execute(
                    text(f"SELECT COUNT(*) FROM restaurant WHERE rating >= {rating}")
                ).scalar()
                percent = (count / result) * 100 if result > 0 else 0
                print(f"  Rating >= {rating}: {count} restaurants ({percent:.1f}%)")
            
            # 3. Test raw SQL with different rating filters
            print("\nTesting min_rating filter with raw SQL:")
            for rating in [3.0, 3.5, 4.0, 4.5]:
                # Use raw SQL
                count = db.session.execute(
                    text(f"SELECT COUNT(*) FROM restaurant WHERE rating >= {rating}")
                ).scalar()
                percent = (count / result) * 100 if result > 0 else 0
                print(f"  min_rating={rating}: {count} restaurants ({percent:.1f}%)")
            
            # 4. Show some sample restaurants with different ratings
            print("\nSample restaurants by rating:")
            for rating in [3.0, 4.0, 4.5]:
                restaurants = db.session.execute(
                    text(f"""
                    SELECT name, city, rating 
                    FROM restaurant 
                    WHERE rating >= {rating} 
                    ORDER BY rating DESC 
                    LIMIT 3
                    """)
                ).fetchall()
                
                print(f"\n  Restaurants with rating >= {rating}:")
                for i, r in enumerate(restaurants, 1):
                    print(f"    {i}. {r.name} - {r.city} - Rating: {r.rating}")
            
            print("\n==== RATING FILTER TEST COMPLETE ====")
            
        except Exception as e:
            print(f"Error testing rating filter: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_rating_filter() 