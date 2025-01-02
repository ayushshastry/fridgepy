from flask import request, jsonify
from config import app, db
from models import Person
from datetime import datetime, date

# CRUD METHOD


# CREATE
@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json

    user_id = data.get('id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    expiration_dict = data.get('expiration_dict')
    dates_heap = data.get('dates_heap')

    if not first_name or not last_name or not email or not phone_number:
        return (jsonify({'message': 'You need all the credentials'}), 400)

    # Create the new person instance with actual values
    new_person = Person(

        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number
    )

    try:
        db.session.add(new_person)
        db.session.commit()
    except Exception as e:
        return (jsonify({"message": str(e)}), 400,)

    # 201 -> successful creation
    return (jsonify({"message": "user created"}), 201)

# READ


@app.route("/users", methods=['GET'])
def get_current_users():

    people = Person.query.all()

    json_people = list(map(lambda x: x.to_json(), people))
    return jsonify({'contacts': json_people})


# UPDATE


@app.route("/update_user/<int:user_id>", methods=['PATCH'])
def update_user(user_id):
    pass


@app.route('/add_item/<int:user_id>', methods=["POST"])
def add_item(user_id):

    current_user = Person.query.get(user_id)

    if not current_user:
        return jsonify({'error': 'User Does Not Exist'}), 404

    data = request.json
    food_item = data.get('food_item')
    exp_date = data.get('expiration_date')

    # Validate the data
    if not food_item or not exp_date:
        return jsonify({"error": "food_item and expiration_date are required"}), 400

    try:
        # Convert the expiration date string to a date object
        expiration_date = datetime.strptime(
            exp_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

    try:
        # Add the item and expiration date to the user's expiration_dict
        current_user.add_expiration(food_item, expiration_date)

        # Commit changes to the database
        db.session.commit()
        return jsonify({"message": "Item added successfully!", "expiration_dict": current_user.expiration_dict}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# DELETE


if __name__ == '__main__':

    # instatiate database
    with app.app_context():
        # create all of the different models in database
        db.create_all()

    app.run(debug=True)
