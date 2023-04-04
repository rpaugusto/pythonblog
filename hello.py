from flask import Flask, render_template, abort, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#Creata a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'itIsMySecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#
db = SQLAlchemy()
db.init_app(app)

# Create a Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    data_added = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.name
    
with app.app_context():
    db.create_all()

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('eMail', validators=[DataRequired()])
    submit = SubmitField('Submit')

#Create a route decorator
@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404

@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'),500

@app.route('/user_add', methods=['GET','POST'])
def user_add():
    form = UserForm()

    if request.method=='POST':
        user = Users.query.filter_by(email=form.email.data).first()
    
        if user is None:
            user = Users(email=request.form['email'], name=request.form['name'])
            db.session.add(user)
            db.session.commit()
    
        form.name.data = ''
        form.email.data = ''
        
        flash('User added Successfully!',category='success')

    our_users = Users.query.order_by(Users.data_added)

    return render_template('user_add.html', form=form, our_users=our_users)

if __name__ == '__main__':
    app.run(debug=True)