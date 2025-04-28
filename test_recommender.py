from app import create_app
from app.models import Restaurant
import os

def test_recommendations():
    """Test if the restaurant recommendation system is working"""
    app = create_app()
    
    with app.app_context():
        # Check if we have restaurants in the database
        try:
            total = Restaurant.query.count()
            print(f"Total restaurants in database: {total}")
            
            if total == 0:
                print("No restaurants in database. Recommendation system can't work without data.")
                return
                
            # Test basic queries to make sure filtering works
            print("\nTesting filters:")
            
            # Test city filter
            cities = ["Mumbai", "Delhi", "Bangalore"]
            for city in cities:
                count = Restaurant.query.filter(Restaurant.city.ilike(f"%{city}%")).count()
                print(f"  Restaurants in {city}: {count}")
            
            # Test cuisine filter
            cuisines = ["North Indian", "Chinese", "Italian"]
            for cuisine in cuisines:
                count = Restaurant.query.filter(Restaurant.cuisine.ilike(f"%{cuisine}%")).count()
                print(f"  {cuisine} restaurants: {count}")
            
            # Test rating filter
            ratings = [3.0, 4.0, 4.5]
            for rating in ratings:
                count = Restaurant.query.filter(Restaurant.rating >= rating).count()
                print(f"  Restaurants with rating >= {rating}: {count}")
                
            # Test cost filter
            costs = [500, 1000, 1500]
            for cost in costs:
                count = Restaurant.query.filter(Restaurant.cost <= cost).count()
                print(f"  Restaurants with cost <= {cost}: {count}")
                
            # Test combined filters
            count = Restaurant.query.filter(
                Restaurant.city.ilike("%Mumbai%"),
                Restaurant.cuisine.ilike("%North Indian%"),
                Restaurant.rating >= 4.0,
                Restaurant.cost <= 1000
            ).count()
            print(f"\nRestaurants matching combined filters: {count}")
            
            # Get some sample restaurants
            print("\nSample restaurants:")
            samples = Restaurant.query.order_by(Restaurant.rating.desc()).limit(5).all()
            for i, restaurant in enumerate(samples, 1):
                print(f"  {i}. {restaurant.name} - {restaurant.city} - {restaurant.cuisine} - Rating: {restaurant.rating}")
                
            print("\nRecommendation system is working correctly!")
            
        except Exception as e:
            print(f"Error testing recommendation system: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_recommendations() 