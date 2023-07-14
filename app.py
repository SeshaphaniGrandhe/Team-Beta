from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'            #created a database which stores and registers our id and password 
db = SQLAlchemy(app)
app.secret_key = 'your_secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():                           # registeration logic
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('register.html', error=error)

        # Insert the new user into the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():                                        # registeration logic
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve the user from the database
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            # Successful login
            # Store the username in the session
            session['username'] = username

            return redirect(url_for('dashboard'))

        error = 'Invalid username or password.'
        return render_template('login.html', error=error)

    return render_template('login.html')



@app.route('/dashboard')    # created the logic for our dashboard
def dashboard():
    # Retrieve the username from the session
    username = session.get('username')

    return render_template('dashboard.html', username=username)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Retrieve the selected answers from the form
        selected_answers = []
        for i in range(1, 11):
            answer = request.form.get(f'question_{i}')
            selected_answers.append(answer)

        # Store the selected answers in the session
        session['selected_answers'] = selected_answers

        try:
            # Load the trained model from the .pkl file
            with open('random_forest_model.pkl', 'rb') as f:
                model = pickle.load(f)

            # Transform the selected answers using the CountVectorizer
            selected_answers_bow = vectorizer.transform(selected_answers)

            # Perform predictions using the trained model
            predicted_answers = model.predict(selected_answers_bow)

            # Evaluate the answers and calculate the score
            score = calculate_score(predicted_answers)

        except:
            # Fall back to comparing selected answers with CSV file's correct answers
            # Read the correct answers from the CSV file
            correct_answers = []
            with open('updated_file.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    correct_answers.append(row['Answer'])

            # Evaluate the answers and calculate the score
            score = 0
            for selected, correct in zip(selected_answers, correct_answers):
                if selected == correct:
                    score += 1

        # Store the score in the session
        session['score'] = score

        # Redirect to the result page
        return redirect(url_for('result'))

    # Check if there are any previously selected answers in the session
    selected_answers = session.get('selected_answers', [])

    # Read the quiz questions from the CSV file
    questions = []
    with open('updated_file.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            options = [value for key, value in row.items() if key != 'Answer']
            question = {
                'question': row['Question'],
                'options': options
            }
            questions.append(question)

    # Select 10 random questions
    selected_questions = random.sample(questions, 10)

    return render_template('quiz.html', questions=selected_questions, selected_answers=selected_answers)

    
    return interpretation




@app.route('/result')
    return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True)
