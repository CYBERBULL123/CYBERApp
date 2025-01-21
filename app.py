from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import markdown
from datetime import datetime
from pdf_utils import generate_pdf
from langchain_agent import generate_report
from file_processor import extract_text_from_file
from dotenv import load_dotenv

# Flask app setup
app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Use environment variable for secret key

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))

# Use SQLite for development and PostgreSQL for production
if os.getenv('FLASK_ENV') == 'production':
    # PostgreSQL for production
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Use the PostgreSQL URL from environment
else:
    # SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "cybersecurity.db")}'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
db = SQLAlchemy(app)

# Ensure the upload and instance folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)  # Create the instance folder for SQLite DB

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
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

# Initialize the database
with app.app_context():
    db.create_all()  # Create all database tables

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/ad_report', methods=['GET'])
@login_required
def ad_report():
    # Render the form page
    return render_template('ad_report.html')

@app.route('/generate-report', methods=['POST'])
@login_required
def generate_report_route():
    try:
        # Check if the request contains extracted text (from uploaded file)
        if 'extracted_text' in request.form and 'fileName' in request.form:
            extracted_text = request.form['extracted_text']
            file_name = request.form['fileName']

            # Generate report using the extracted text
            report_content = generate_report(extracted_text)

            # Use the file name as the report title
            report_title = f"Report for {file_name}"
            report = Report(title=report_title, content=report_content, user_id=current_user.id)
            db.session.add(report)
            db.session.commit()

            flash('Report generated successfully!', 'success')
            return redirect(url_for('report', report_id=report.id))  # Redirect to the report page

        # Check if the request contains form data (from ad_html)
        elif 'reportType' in request.form and 'projectName' in request.form:
            # Extract common form data
            report_type = request.form.get('reportType')
            project_name = request.form.get('projectName')
            client_name = request.form.get('clientName')
            assessment_date = request.form.get('assessmentDate')
            assessor_name = request.form.get('assessorName')
            compilance_name = request.form.get('complianceType')

            # Initialize findings, risk_analysis, and recommendations
            findings = ""
            risk_analysis = ""
            recommendations = ""

            # Extract additional fields based on report type
            if report_type == "VAPT":
                findings = request.form.get('highLevelFindings', '') + "\n" + request.form.get('detailedFindings', '')
                risk_analysis = request.form.get('riskDescription', '') + "\n" + request.form.get('businessImpact', '')
                recommendations = request.form.get('mitigationStrategies', '') + "\n" + request.form.get('additionalNotes', '')
            elif report_type == "Pentesting":
                findings = request.form.get('highLevelFindings', '') + "\n" + request.form.get('detailedFindings', '')
                risk_analysis = request.form.get('toolsUsed', '') + "\n" + request.form.get('stepsTaken', '')
                recommendations = request.form.get('mitigationStrategies', '') + "\n" + request.form.get('additionalNotes', '')
            elif report_type == "Incident Response":
                findings = request.form.get('incidentDescription', '')
                risk_analysis = request.form.get('actionsTaken', '')
                recommendations = request.form.get('futurePreventionStrategies', '') + "\n" + request.form.get('lessonsLearned', '')
            elif report_type == "Compliance":
                findings = request.form.get('complianceFindings', '')
                recommendations = request.form.get('recommendations', '')
            elif report_type == "Risk Assessment":
                findings = request.form.get('risksIdentified', '') + "\n" + request.form.get('riskSeverity', '')
                recommendations = request.form.get('riskMitigationPlan', '')

            # Prepare data for the LangChain agent
            form_data = {
                "reportType": report_type,
                "projectName": project_name,
                "clientName": client_name,
                "assessmentDate": assessment_date,
                "assessorName": assessor_name,
                "findings": findings,
                "riskAnalysis": risk_analysis,
                "recommendations": recommendations,
                "complianceType":compilance_name
            }

            # Generate report using the LangChain agent
            report_content = generate_report(form_data)

            # Save the report to the database
            report_title = f"Advanced Report for {project_name}"
            report = Report(title=report_title, content=report_content, user_id=current_user.id)
            db.session.add(report)
            db.session.commit()

            flash('Advanced report generated successfully!', 'success')
            return redirect(url_for('report', report_id=report.id))  # Redirect to the report page

        else:
            flash('Invalid request data. Please try again.', 'error')
            return redirect(url_for('index'))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('error'))


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('index'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))

        try:
            # Step 1: Extract text from the uploaded file
            file_content = extract_text_from_file(file)
            if not file_content:
                flash('Failed to extract text from the file.', 'error')
                return redirect(url_for('index'))

            # Step 2: Display extracted text in the preview
            return render_template('index.html', extracted_text=file_content)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('index'))

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
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

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

@app.route('/dashboard')
@login_required
def dashboard():
    reports = Report.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', reports=reports)

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/report/<int:report_id>')
@login_required
def report(report_id):
    report = Report.query.get_or_404(report_id)
    report_html = markdown.markdown(report.content)
    return render_template('report.html', report=report, report_html=report_html)

@app.route('/download/<int:report_id>')
@login_required
def download(report_id):
    # Fetch the report from the database
    report = Report.query.get_or_404(report_id)

    # Generate the PDF using the utility function
    pdf_buffer = generate_pdf(
        report_title=report.title,
        report_content=report.content,
        created_at=report.created_at.strftime('%Y-%m-%d %H:%M:%S')
    )

    # Prepare the buffer for download
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{report.title}.pdf",
        mimetype='application/pdf'
    )

@app.route('/delete-report/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    try:
        report = Report.query.filter_by(id=report_id, user_id=current_user.id).first()
        if not report:
            flash('Report not found or unauthorized.', 'error')
            return redirect(url_for('dashboard'))
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the report.', 'error')
    return redirect(url_for('dashboard'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)