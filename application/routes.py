from application import app, api
from flask import render_template, request, Response, json, flash, redirect,url_for, session, jsonify
from application.models import User, Course, Enrollment
from application.forms import LoginForm, RegisterForm
from flask_restplus import Resource


@app.route('/')
@app.route('/home')
def home():
    login = False
    if session.get('username'):
        login = True
    return render_template('home.html',title='home', login=login, home=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and user.get_password(form.password.data):
            flash('You are successfully logged in!', 'success')
            session['user_id'] = user.user_id
            session['username'] = user.username
            return redirect(url_for('home'))
        flash('Login unsuccessful, check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form, login=True)


@app.route('/logout')
def logout():
    session['user_id'] = None
    session['username'] = None
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username'):
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = User.objects.count() + 1
        user = User(user_id=user_id,username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.save()
        flash('Your account has been created you are now able to login!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, register=True)


@app.route('/courses')
@app.route('/courses/<term>')
def courses(term='Spring 2020'):
    courses = Course.objects.order_by('courseID')
    return render_template('courses.html',title='Courses', courseData=courses, term=term, courses=True)


@app.route('/enrollment', methods=['GET', 'POST'])
def enrollment():
    if not session.get('username'):
        return redirect(url_for('login'))
    courseID = request.form.get('courseID')
    courseTitle = request.form.get('title')
    user_id = session.get('user_id')

    if courseID:
        if Enrollment.objects(user_id=user_id, courseID=courseID):
            flash(f'Opps! You are already enrolled in this course {courseTitle}', 'danger')
        else:
            Enrollment(user_id=user_id, courseID=courseID).save()
            flash(f'You are enrolled in {courseTitle}', 'success')

    classes = list(User.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'enrollment', 
                    'localField': 'user_id', 
                    'foreignField': 'user_id', 
                    'as': 'r1'
                }
            }, {
                '$unwind': {
                    'path': '$r1', 
                    'includeArrayIndex': 'r1_id', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$lookup': {
                    'from': 'course', 
                    'localField': 'r1.courseID', 
                    'foreignField': 'courseID', 
                    'as': 'r2'
                }
            }, {
                '$unwind': {
                    'path': '$r2', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'user_id': user_id
                }
            }, {
                '$sort': {
                    'courseID': 1
                }
            }]))
    return render_template('enrollment.html', title='Enrollment', classes=classes, enrollment=True )


##############################################################################

#GET & POST Users
@api.route('/api', '/api/')
class GetAndPost(Resource):
    #GET
    def get(self):
        return jsonify(User.objects.all())

    #POST
    def post(self):
        data = api.payload
        user = User(user_id=data.user_id,username=data.username, email=data.email)
        user.set_password(data.password)
        user.save()
        return jsonify(User.objects(user_id=data.user_id))

#GET one User
@api.route('/api/<id>')
class GetUpdateDelete(Resource):
    def get(self, idx):
        return jsonify(User.objects(user_id=idx))













#############################################################################


# @app.route('/api/')
# @app.route('/api/<idx>')
# def api(idx=None):
#     if idx==None:
#         apiData = courses
#     else:
#         apiData = courses[int(idx)]
#     return Response(json.dumps(apiData), mimetype="application/json")


# @app.route('/users')
# def user():
#     users = User.objects.all()
#     return render_template('users.html',title='Users', users=users)