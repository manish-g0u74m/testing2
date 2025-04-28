from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from app.models import Restaurant, SuggestedRestaurant
from app.forms import LoginForm, RegisterForm, SuggestionForm
from . import db, mail
from flask_mail import Message
import os
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import random
from sqlalchemy import text


main = Blueprint('main', __name__)

def generate_otp():
    # Generate a random 6-digit OTP
    return str(random.randint(100000, 999999))

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data.lower().strip()).first()
            if user and user.check_password(form.password.data):
                # Check if user is verified
                if not user.is_verified:
                    flash('Please verify your email address before logging in.', 'warning')
                    return redirect(url_for('main.login'))
                
                login_user(user)
                flash('Welcome back! You have been logged in successfully.', 'success')
                # Get the next page from the URL query parameter, or default to dashboard
                next_page = request.args.get('next', url_for('main.dashboard'))
                return redirect(next_page)
            else:
                flash('Login failed. Please check your email and password.', 'danger')
        except Exception as e:
            flash(f'An error occurred while processing your request. Please try again.', 'danger')
            print(f"Login error: {str(e)}")
    
    return render_template('login.html', form=form, title='Login')

@main.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Clean and normalize the email
            email = form.email.data.lower().strip()
            
            # Check if the user already exists
            existing_user = User.query.filter((User.email == email) | 
                                            (User.username == form.username.data)).first()
            
            if existing_user:
                if existing_user.email == email:
                    flash('This email is already registered. Please login instead.', 'danger')
                else:
                    flash('This username is already taken. Please choose another.', 'danger')
                return render_template('register.html', form=form, title='Register')

            # Create a new user but don't add to DB yet
            new_user = User(
                username=form.username.data,
                email=email,
                is_verified=False
            )
            new_user.set_password(form.password.data)  # Hash the password
            
            # Generate OTP
            otp = generate_otp()
            
            # Store registration data in session
            session['registration_data'] = {
                'username': form.username.data,
                'email': email,
                'password': form.password.data,
                'otp': otp
            }
            
            # Send OTP email
            msg = Message('Email Verification', recipients=[email])
            msg.body = f'''Your OTP for DineMate registration is: {otp}
            
Please enter this code to complete your registration.
            
If you did not register for DineMate, please ignore this email.
'''
            mail.send(msg)
            
            flash('We\'ve sent a verification code to your email. Please check and enter it below.', 'info')
            return redirect(url_for('main.verify_otp'))
            
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            print(f"Registration error: {str(e)}")
            
    return render_template('register.html', form=form, title='Register')

@main.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    # Check if we have registration data in session
    if 'registration_data' not in session:
        flash('Registration session expired. Please try again.', 'danger')
        return redirect(url_for('main.register'))
        
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        reg_data = session['registration_data']
        
        if entered_otp == reg_data['otp']:
            # OTP is correct, create user account
            new_user = User(
                username=reg_data['username'],
                email=reg_data['email'],
                is_verified=True
            )
            new_user.set_password(reg_data['password'])
            
            # Save to database
            db.session.add(new_user)
            db.session.commit()
            
            # Clear session data
            session.pop('registration_data', None)
            
            flash('Your account has been verified and created successfully! Please login.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    
    return render_template('verify_otp.html', title='Verify Email')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))

@main.route('/recommend')
@login_required
def recommend():
    # Get filters from URL parameters (e.g., /recommend?city=Delhi&cuisine=North+Indian)
    city = request.args.get('city', '').strip()          
    cuisine = request.args.get('cuisine', current_user.preferred_cuisines.split(',')[0] if current_user.preferred_cuisines else '').strip()
    
    # Use default values for sliders if not provided
    try:
        min_rating = float(request.args.get('min_rating', 0))
    except (ValueError, TypeError):
        min_rating = 0
        
    try:
        max_cost = int(request.args.get('max_cost', 3000))
    except (ValueError, TypeError):
        max_cost = 3000
    
    # Basic debug info without database queries
    print(f"Filtering - City: '{city}', Cuisine: '{cuisine}', Min Rating: {min_rating}, Max Cost: {max_cost}")
    
    # Get popular cities for autocomplete (limited to top 20)
    try:
        popular_cities = db.session.execute(
            text("""
            SELECT DISTINCT city FROM restaurant 
            WHERE city IS NOT NULL AND city != ''
            GROUP BY city
            ORDER BY COUNT(*) DESC
            LIMIT 20
            """)
        ).fetchall()
        popular_cities = [c[0] for c in popular_cities if c[0]]
        print(f"Popular cities: {popular_cities}")
    except Exception as e:
        print(f"Error getting cities: {str(e)}")
        popular_cities = []
    
    # Get popular cuisines for autocomplete (limited to top 15)
    try:
        popular_cuisines = db.session.execute(
            text("""
            SELECT DISTINCT cuisine FROM restaurant 
            ORDER BY rating DESC
            LIMIT 15
            """)
        ).fetchall()
        popular_cuisines = [c[0] for c in popular_cuisines if c[0]]
        print(f"Popular cuisines: {popular_cuisines}")
    except Exception as e:
        print(f"Error getting cuisines: {str(e)}")
        popular_cuisines = []

    # Use raw SQL to safely get restaurant recommendations
    sql_query = """
    SELECT id, name, location, locality, city, cuisine, rating, votes, cost 
    FROM restaurant 
    WHERE 1=1
    """
    
    params = {}
    
    # Add filters to the SQL query based on user input
    if city:
        # Match city in city, location and locality fields for better results
        sql_query += " AND (city LIKE :city OR location LIKE :city OR locality LIKE :city)"
        params['city'] = f"%{city}%"
    
    if cuisine:
        sql_query += " AND cuisine LIKE :cuisine"
        params['cuisine'] = f"%{cuisine}%"
    
    if min_rating > 0:
        sql_query += " AND rating >= :min_rating"
        params['min_rating'] = min_rating
    
    if max_cost and max_cost > 0:
        sql_query += " AND cost <= :max_cost"
        params['max_cost'] = max_cost
    
    # Add sorting and limit
    sql_query += " ORDER BY rating DESC LIMIT 20"
    
    # Execute the query
    try:
        result = db.session.execute(text(sql_query), params)
        
        # Convert result to Restaurant objects
        restaurant_data = result.fetchall()
        restaurants = []
        
        for row in restaurant_data:
            # Create a Restaurant object and set its attributes
            restaurant = Restaurant()
            restaurant.id = row.id
            restaurant.name = row.name
            restaurant.location = row.location
            restaurant.locality = row.locality
            restaurant.city = row.city
            restaurant.cuisine = row.cuisine
            restaurant.rating = row.rating
            restaurant.votes = row.votes
            restaurant.cost = row.cost
            
            restaurants.append(restaurant)
            
        # Print the number of results
        print(f"Found {len(restaurants)} restaurants matching criteria")
        
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        restaurants = []
    
    # Check if any results found
    if not restaurants:
        flash(f"No restaurants found matching your search criteria.",'warning')
        
        # Try to provide more helpful guidance
        # Get sample cities and cuisines using direct SQL
        try:
            # Use simple queries to get sample data
            cities_result = db.session.execute(text("SELECT DISTINCT city FROM restaurant LIMIT 5")).fetchall()
            cuisines_result = db.session.execute(text("SELECT DISTINCT cuisine FROM restaurant LIMIT 5")).fetchall()
            
            cities_str = ", ".join([c[0] for c in cities_result if c[0]])
            cuisines_str = ", ".join([c[0] for c in cuisines_result if c[0]])
            
            if cities_str:
                flash(f"Try these cities: {cities_str}", "info")
            if cuisines_str:
                flash(f"Try these cuisines: {cuisines_str}", "info")
        except Exception as e:
            print(f"Error getting sample data: {str(e)}")
    
    return render_template('recommendations.html', restaurants=restaurants, 
                          popular_cuisines=popular_cuisines,
                          popular_cities=popular_cities)

@main.route('/save_preferences', methods=['POST'])
@login_required
def save_preferences():
    # Get user preferences from form
    favorite_cuisines = request.form.getlist('cuisine')  # Gets all checked boxes
    budget = request.form.get('budget')

    # Update user preferences in database
    current_user.preferred_cuisines = ",".join(favorite_cuisines[:3])  # Store as comma-separated string
    current_user.budget_preference = budget
    db.session.commit()

    flash('Your preferences have been saved!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/suggest', methods=['GET', 'POST'])
def suggest():
    form = SuggestionForm()  # Create form instance
    
    if form.validate_on_submit():
        try:
            suggestion = SuggestedRestaurant(
                name=form.name.data,
                city=form.city.data,
                locality=form.locality.data,
                cuisine=form.cuisine.data,
                rating=form.rating.data,
                comment=form.comment.data,
                user_email=form.email.data,
                user_id=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(suggestion)
            db.session.commit()
            flash('Thank you! Your suggestion has been submitted.', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error submitting suggestion. Please try again.', 'danger')
    return render_template('suggest.html', form=form)

@main.route('/saved-restaurants')
@login_required
def saved_restaurants():
    # This is a placeholder - in a real app, you would fetch the user's saved restaurants
    # For demo purposes, we'll just show some sample restaurants
    sample_restaurants = Restaurant.query.limit(5).all()
    
    return render_template('saved_restaurants.html', restaurants=sample_restaurants, title="Saved Restaurants")

def get_reset_token(user, secret_key):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(user.email, salt='password-reset-salt')

@main.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '')
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if user:
            # Generate token
            token = get_reset_token(user, current_app.config['SECRET_KEY'])
            
            # Create reset URL
            reset_url = url_for('main.reset_token', token=token, _external=True)
            
            # Send email
            msg = Message('Password Reset Request', 
                         recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email.
'''
            mail.send(msg)
            
            flash('Password reset instructions sent to your email.', 'success')
        else:
            flash('Email address not found.', 'danger')
            
        return redirect(url_for('main.login'))
    
    return render_template('reset_password.html', title="Reset Password")

# Add a new route to handle the reset token
@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    # Verify token and get user
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiry
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Invalid or expired token', 'danger')
            return redirect(url_for('main.reset_password'))
    except:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('main.reset_password'))
    
    # Token is valid, show reset form
    if request.method == 'POST':
        password = request.form.get('password')
        
        # Update user's password
        user.set_password(password)
        db.session.commit()
        
        flash('Your password has been updated!', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('reset_token.html', title='Reset Password', token=token)


