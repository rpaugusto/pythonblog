from flask import Flask, render_template, abort, flash, request, make_response, url_for, Response
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_migrate import Migrate # < --- new update
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import Boolean
from datetime import datetime
from flask_bcrypt import Bcrypt

#Creata a Flask Instance
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'itIsMySecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)

# Create a Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    date_added = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    password_hash = db.Column(db.String(128), nullable=False)
    #realtionship
    todos = db.relationship('Todos', backref='owner', lazy=True)

    def __repr__(self):
        return '<Name %r>' % self.name
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password) # returns True
    
    
class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    description = db.Column(db.String(2048))
    is_complet = db.Column(Boolean, default=False)
    date_add = db.Column(db.DateTime(timezone=True), default=datetime.now)
    date_upt = db.Column(db.DateTime(timezone=True), onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
with app.app_context():
    db.create_all()

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('eMail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
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

@app.route('/user_list')
def user_list():

    our_users = Users.query.order_by(Users.date_added)

    return render_template('user_list.html', our_users=our_users)

@app.route('/user_add', methods=['GET','POST'])
def user_add():
    form = UserForm()

    if request.method=='POST':
        user = Users.query.filter_by(email=form.email.data).first()
    
        if user is None:
            user = Users(email=request.form['email'], name=request.form['name'])
            db.session.add(user)
            db.session.commit()
            flash('User "{}" added Successfully!'.format(form.name.data),category='success')
            form.name.data = ''
            form.email.data = ''
        else:
            flash('e-mail "{}" already exists!'.format(form.email.data),category='warning')
        
    return render_template('user_add.html', form=form)

@app.route('/user_update/<int:id>', methods=['GET','POST'])
def user_update(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        
        try:
            db.session.commit()
            flash('User "{}" updated Successfully!'.format(form.name.data),category='success')
        except:
            flash('Error! ...try again!',category='warning')
            pass
    
    return render_template('user_update.html', form=form, update=user_to_update)

@app.route('/user_list_csv')
def user_list_csv():
    
    our_users = Users.query.order_by(Users.data_added)

    date_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = date_stamp + 'userlist.csv'

    csv_contents = 'ID,User,Email\n'
    for user in our_users:
        csv_contents += '{},{},{}\n'.format(user.id,user.name,user.email)

    return Response(
        csv_contents,
        mimetype='text/csv',
        headers={"Content-disposition":
                     f"attachment; filename={file_name}"}
    )

if __name__ == '__main__':
    app.run(debug=True)