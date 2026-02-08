import os
import stripe
from .ai.genetic_routing import calculate_best_route
from .ai.prediction import predict_stock
from flask import Flask, flash, render_template, redirect, url_for, session, request, jsonify

from app import app, db, admin, login_manager, mail
from flask_admin.contrib.sqla import ModelView
from .models import Volounteer, Donation, FoodBank
from .forms import SignupForm, LoginForm, DonationForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import timedelta, datetime
from sqlalchemy import func, or_
import json
import math
import uuid
import random       
from cryptography.fernet import Fernet
from decimal import Decimal

login_manager = LoginManager()
login_manager.login_view = 'login'  # redirect to this route if not logged in
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    if not user_id:
        return None
    try:
        uid = int(user_id)
    except ValueError:
        return None
    # Try FoodBank first
    user = FoodBank.query.get(uid)
    if user:
        return user
    # Try Volunteer next
    return Volounteer.query.get(uid)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/bank', methods=['GET', 'POST'])

def bank():
    threshold = 3
    foodbank = FoodBank.query.get(current_user.id)
    
    need_donations, description,requied_last_donation_date = predict_stock()
    foodbank.requied_last_donation_date = datetime.utcnow() + timedelta(days =3)
  
    best_route = calculate_best_route()
          
     
    return render_template('bank.html', need_donations=need_donations, description=description, foodbanks_with_pending=foodbank.pending_pickups, best_route=best_route)

@app.route('/volunteer', methods=['GET', 'POST'])

def volunteer():
   
    donations = Donation.query.filter_by(volounteer_id=current_user.id).all()
    donation_ids = [d.id for d in donations]
    return render_template('volunteer.html', donations=donations,donation_ids=donation_ids)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    
    # Redirect authenticated users to home page
    if current_user.is_authenticated:
        if hasattr(current_user, 'volunteer_id'):
            return redirect(url_for('volunteer'))
        else:
            return redirect(url_for('bank'))

    form = SignupForm()

    if form.validate_on_submit():

        hash_password =generate_password_hash(form.password.data)
        if form.role.data == 'foodbank':
            new_user = FoodBank(name=form.username.data,
                                latitude= 0.0,
                                longitude= 0.0,
                                 password=hash_password ,
                                location=form.location.data,
                                pending_pickups=0,
                                require_donations=False)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return redirect(url_for('bank')) 
        else:
            new_user = Volounteer(name=form.username.data, 
                                  password=hash_password,
                                  location=form.location.data,
                                  latitude= 0.0,
                                  longitude= 0.0)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('volunteer'))
    return render_template('signup.html', form=form)
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect to home if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
  
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        volunteer = Volounteer.query.get(username)
        foodbank = FoodBank.query.get(username)

        if volunteer and check_password_hash(volunteer.password_hash, password):
            login_user(volunteer)
            return redirect(url_for('volunteer'))
        elif foodbank and check_password_hash(foodbank.password_hash, password):
            login_user(foodbank)
            return redirect(url_for('bank'))    
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('/login.html', form=form)

 
@app.route('/accept/<donation_id>', methods=['GET', 'POST'])

def accept(donation_id):
    donation = Donation.query.get(donation_id)
    foodbank = FoodBank.query.get(donation.food_bank_id)
    foodbank.pending_pickups = foodbank.pending_pickups + 1
    db.session.commit()
    return redirect(url_for('volunteer'))

@app.route('/decline/<donation_id>', methods=['GET', 'POST'])

def decline(donation_id):
    donation = Donation.query.get(donation_id)
    donation.food_bank_id = None
    db.session.commit()
    return redirect(url_for('volunteer'))

@app.route('/request', methods=['GET', 'POST'])

def request():
    donations = (
    db.session.query(Donation)
    .join(FoodBank, Donation.food_bank_id == FoodBank.id)
    .filter(Donation.expiry > FoodBank.requied_last_donation_date)
    .all()
  )
    for d in donations:
        d.food_bank_id = current_user.id
    foodbank = FoodBank.query.get(current_user.id)
    foodbank.require_donations = True
    db.session.commit()
    return redirect(url_for('bank'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/new_donation', methods=['GET', 'POST'])

def new_donation():
    form = DonationForm()
    if form.validate_on_submit():
        new_donation = Donation(
            meal_amount=form.meal_amount.data,
            expiry=form.expiry.data,
            volounteer_id=current_user.id,
            food_bank_id=None
        )
        db.session.add(new_donation)
        db.session.commit()
        flash('Donation created successfully!', 'success')
        return redirect(url_for('volunteer'))
    return render_template('new_donation.html', form=form)