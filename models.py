from config import db
import heapq
from datetime import date
from collections import defaultdict


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)

    # We'll store the dates and items separately, using a dictionary and a min-heap
    # stores {date: [item1, item2, ...]}
    expiration_dict = db.Column(
        db.PickleType, nullable=False, default=defaultdict(list))
    dates_heap = db.Column(db.PickleType, nullable=False,
                           default=[])  # stores dates in heap order

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

        heapq.heappush(self.dates_heap, expiration_date)

        # Append the food item to the expiration list
        self.expiration_dict[expiration_date].append(food_item)

    def get_expiration_date(self):

        if not self.dates_heap:
            return None, []

        today = date.today()

        earliest_day = date(self.dates_heap[0])

        if earliest_day - today == 3:
            heapq.heappop(self.dates_heap)
            items = self.expiration_dict.pop(earliest_day, [])
            return earliest_day, items

        elif today == earliest_day or today > earliest_day:

            self.remove_expirations(earliest_day)

        return earliest_day, self.expiration_dict[earliest_day]

    def get_food_item(self, food_item):

        pass

    def remove_expirations(self, expiration_date):
        if expiration_date not in self.expiration_dict:
            return None, []
        removed_items = self.expiration_dict.pop(expiration_date, None)
        if removed_items is not None:
            # If the expiration_date was present in expiration_dict, remove it from the dates_heap
            self.dates_heap = [
                d for d in self.dates_heap if d != expiration_date]
            # Rebuild the heap after removal
            heapq.heapify(self.dates_heap)
