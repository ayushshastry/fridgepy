from config import db
import heapq
from datetime import date, datetime
from collections import defaultdict
from sqlalchemy.ext.mutable import MutableDict


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)

    # We'll store the dates and items separately, using a dictionary and a min-heap
    # stores {date: [item1, item2, ...]}
    expiration_dict = db.Column(
        MutableDict.as_mutable(db.PickleType), nullable=False, default=dict
    )
    dates_heap = db.Column(db.PickleType, nullable=False, default=list)

    def to_json(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "expiration_dict": self.expiration_dict,
            "dates_heap": self.dates_heap
        }

    def add_expiration(self, food_item, expiration_date):
        # If expiration_date doesn't exist in expiration_dict, add it and also push to heap

        # Convert date object to string for dictionary key
        expiration_date_str = expiration_date.isoformat()

        if expiration_date_str not in self.expiration_dict:
            heapq.heappush(self.dates_heap, expiration_date_str)

        # Append the food item to the expiration list
        self.expiration_dict.setdefault(
            expiration_date_str, []).append(food_item)

    def get_expiration_date(self):

        if not self.dates_heap:
            return None, []

        # Get the earliest date string from the heap
        earliest_date_str = self.dates_heap[0]
        earliest_date = datetime.strptime(
            earliest_date_str, '%Y-%m-%d').date()  # Convert to date object
        today = date.today()

        if earliest_date <= today:
            # Remove the expired date from the heap and dictionary
            heapq.heappop(self.dates_heap)
            items = self.expiration_dict.pop(earliest_date_str, [])
            return earliest_date, items

        # Return the earliest upcoming expiration date and its items
        return earliest_date, self.expiration_dict.get(earliest_date_str, [])

    def get_food_item(self, food_item):
        for exp_date, items in self.expiration_dict.items():
            if food_item in items:
                return exp_date, items
        return None, []

    def remove_expirations(self):

        if not self.dates_heap:
            return None, []

        # Convert the earliest date back to a date object
        earliest_date_str = self.dates_heap[0]
        earliest_date = datetime.strptime(earliest_date_str, '%Y-%m-%d').date()
        today = date.today()

        if earliest_date <= today:
            heapq.heappop(self.dates_heap)
            items = self.expiration_dict.pop(earliest_date_str, [])
            return earliest_date, items

        return earliest_date, self.expiration_dict.get(earliest_date_str, [])
