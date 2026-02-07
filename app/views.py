import os
import stripe
from ai.genetic_routing import calculate_best_route
from ai.prediction import predict_stock
from flask import Flask, flash, render_template, redirect, url_for, session, request, jsonify

from app import app, db, admin, login_manager, mail
from flask_admin.contrib.sqla import ModelView
from .models import Volounteer, Donation, FoodBank
from .forms import SignupForm, LoginForm, DonationForm, FoodBankForm
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



@app.route('/')
def index():
    return render_template('templates/index.html')

@app.route('/bank', methods=['POST'])
@login_required
def bank():
    threshold = 3
    foodbanks_with_pending = FoodBank.query.filter(FoodBank.pending_pickups > 0).all()
    if foodbanks_with_pending> 0:
        if foodbanks_with_pending > threshold:
            calculate_best_route()
        else:
            return render_template('bank.html', foodbanks=foodbanks_with_pending)
    else:
        need_donations, description = predict_stock()
        return render_template('bank.html', need_donations=need_donations, description=description)
    
@app.route('/volunteer', methods=['POST'])
@login_required
def volunteer():
   
    donations = Donation.query.filter_by(volounteer_id=current_user.volunteer_id).all()

    return render_template('volunteer.html', donations=donations)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    
    # Redirect authenticated users to home page
    if current_user.is_authenticated:
        return redirect(url_for('template'))

    form = SignupForm()

    if form.validate_on_submit():

        hash_password =generate_password_hash(form.password.data)
        if form.role.data == 'foodbank':
            new_user = FoodBank(name=form.username.data, password_hash=hash_password , location=form.location)
            db.session.add(new_user)
            return redirect(url_for('bank')) 
        else:
            new_user = Volounteer(name=form.username.data, password_hash=hash_password,location=form.location)
            db.session.add(new_user)
            return redirect(url_for('volunteer'))
    return render_template('sign_up.html', form=form)
        

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
    return render_template('login.html', form=form)

 