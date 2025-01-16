from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import markdown
from io import BytesIO
from langchain_agent import generate_report
from file_processor import extract_text_from_file

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cybersecurity.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Add email field
    password = db.Column(db.String(120), nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Check file extension
        allowed_extensions = {'csv', 'txt', 'doc', 'docx', 'pdf', 'json', 'log'}
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            flash('Invalid file type. Allowed file types: CSV, TXT, DOC, DOCX, PDF, JSON, LOG.', 'error')
            return redirect(url_for('index'))
        
        try:
            # Extract text from the uploaded file
            file_content = extract_text_from_file(file)
            if not file_content:
                flash('Failed to extract text from the file.', 'error')
                return redirect(url_for('index'))
            
            # Generate report using Gemini model
            report_content = generate_report(file_content)  # Pass extracted text to Gemini
            
            # Save the report to the database
            report = Report(title=file.filename, content=report_content, user_id=current_user.id)
            db.session.add(report)
            db.session.commit()
            app.logger.info(f"Report generated successfully with ID: {report.id}")  # Debugging
            
            flash('Report generated successfully!', 'success')
            return render_template('report', report_id=report.id) # Redirect to the report page
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    # Render the index page for GET requests
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))  # Redirect back to login page
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']  # Get email from form
        password = request.form['password']
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        elif User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        else:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/dashboard')
@login_required
def dashboard():
    reports = Report.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', reports=reports)

@app.route('/report/<int:report_id>')
@login_required
def report(report_id):
    # Fetch the report from the database
    report = Report.query.get_or_404(report_id)

    # Convert Markdown content to HTML
    report_html = markdown.markdown(report.content)

    return render_template('report.html', report=report, report_html=report_html)

@app.route('/download/<int:report_id>')
@login_required
def download(report_id):
    report = Report.query.get_or_404(report_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, report.title)
    
    # Add content
    p.setFont("Helvetica", 12)
    text = p.beginText(100, 730)
    text.textLines(report.content)
    p.drawText(text)
    
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"{report.title}.pdf", mimetype='application/pdf')

@app.route('/delete-report/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    try:
        # Find the report by ID and ensure it belongs to the current user
        report = Report.query.filter_by(id=report_id, user_id=current_user.id).first()
        if not report:
            flash('Report not found or unauthorized.', 'error')
            return redirect(url_for('dashboard'))

        # Delete the report
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the report.', 'error')
    return redirect(url_for('dashboard'))

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)