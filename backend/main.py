from flask import request, jsonify
from config import app, db
from models import Person
from datetime import datetime

# CRUD METHOD


# CREATE
@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone_number = data.get('phone_number')

    if not first_name or not last_name or not email or not phone_number:
        return jsonify({'message': 'Missing required fields'}), 400

    new_person = Person(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number
    )

    try:
        db.session.add(new_person)
        db.session.commit()
        return jsonify({"message": "User created successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# READ


@app.route("/users", methods=['GET'])
def get_current_users():
    people = Person.query.all()
    json_people = [person.to_json() for person in people]
    return jsonify({'users': json_people})


# UPDATE


@app.route("/update_user/<int:user_id>", methods=['PATCH'])
def update_user(user_id):
    user = Person.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.phone_number = data.get('phone_number', user.phone_number)

    try:
        db.session.commit()
        return jsonify({"message": "User updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/add_item/<int:user_id>', methods=["POST"])
def add_item(user_id):
    user = Person.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    food_item = data.get('food_item')
    exp_date = data.get('expiration_date')

    if not food_item or not exp_date:
        return jsonify({"error": "Both food_item and expiration_date are required"}), 400

    try:
        # Convert expiration_date from string to date object
        expiration_date = datetime.strptime(exp_date, '%Y-%m-%d').date()
        user.add_expiration(food_item, expiration_date)
        db.session.commit()
        return jsonify({
            "message": "Item added successfully!",
            "expiration_dict": user.expiration_dict
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# DELETE

# REMOVE ITEM


@app.route('/remove_item/<int:user_id>', methods=["POST"])
def remove_item(user_id):
    user = Person.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    exp_date = data.get('expiration_date')

    if not exp_date:
        return jsonify({"error": "expiration_date is required"}), 400

    try:
        expiration_date = datetime.strptime(exp_date, '%Y-%m-%d').date()
        user.remove_expirations(expiration_date)
        db.session.commit()
        return jsonify({"message": f"Items on {exp_date} removed successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# DELETE USER
@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Person.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':

    # instatiate database
    with app.app_context():
        # create all of the different models in database
        db.create_all()

    app.run(debug=True)
