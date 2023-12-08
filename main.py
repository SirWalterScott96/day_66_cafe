from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# Connect to Database
current_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(current_dir, 'instance', 'cafes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        return f'Cafe {self.name}'

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template('index.html')


# HTTP GET - Read Record
@app.route('/random')
def random_cafe():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe_local = random.choice(cafes)

    return jsonify(cafe=random_cafe_local.to_dict())


@app.route('/all')
def get_all():
    cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    all_cafes = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=all_cafes)


@app.route('/search')
def search_cafe():
    query_location = request.args.get('loc')

    loc_cafe = db.session.execute(db.select(Cafe).where(Cafe.location == query_location)).scalars().all()
    if loc_cafe:
        return jsonify(cafe=[cafe.to_dict() for cafe in loc_cafe])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    if request.method == 'POST':
        new_cafe = Cafe(name=request.form['name'],
                        map_url=request.form['map_url'],
                        img_url=request.form['img_url'],
                        location=request.form['location'],
                        seats=request.form['seats'],
                        has_toilet=True if request.form.get('has_toilet') else False,
                        has_wifi=True if request.form.get('has_wifi') else False,
                        has_sockets=True if request.form.get('has_sockets') else False,
                        can_take_calls=True if request.form.get('can_take_calls') else False,
                        coffee_price=request.form['coffee_price']
                        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={
            'success': 'Successfully added the new cafe.'
        })
    return render_template('add.html')


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>')
def update_price_coffe(cafe_id):
    try:
        cafe_to_update = db.get_or_404(Cafe, cafe_id)
        print(request.args.get('new_price'))
        cafe_to_update.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify(success='Successfully update the price.')
    except Exception:
        return jsonify(error={
            'Not Found': 'Sorry, a cafe with that id was not found in the database'
        })



# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
