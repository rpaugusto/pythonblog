from flask import Flask, render_template

#Creata a Flask Instance
app = Flask(__name__)

#Create a route decorator
@app.route('/')
def index():
    return render_template('base.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'),500

if __name__ == '__main__':
    app.run()