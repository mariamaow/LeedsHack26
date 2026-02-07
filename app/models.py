from app import db
from datetime import datetime
from flask_login import UserMixin

class Volounteer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    def __repr__(self):
        return f'<Volounteer {self.name}>'

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_amount = db.Column(db.Integer, nullable=False)
    expiry = db.Column(db.DateTime, default=datetime.utcnow)
    volounteer_id = db.Column(db.Integer, db.ForeignKey('volounteer.id'), nullable=False)
    food_bank_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'), nullable=False)
    volounteer = db.relationship('Volounteer', backref=db.backref('donations', lazy=True))

    def __repr__(self):
        return f'<Donation {self.amount} by Volounteer ID {self.volounteer_id}>'
    
class FoodBank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    location = db.Column(db.String(200), nullable=False)
    pending_pickups = db.Column(db.Integer, nullable=True)
    require_donations = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<FoodBank {self.name}>'