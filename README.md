# Citizen Grievance and Issue Tracker

A comprehensive web application built with Django for citizens to report issues and for authorities to manage them.

## Features

### For Citizens
- Register and login
- Submit complaints with categories, descriptions, images/videos, and GPS location
- Track complaint status in real-time
- Provide feedback and ratings for resolved complaints

### For Authorities
- Dashboard with complaint overview
- Assign and update complaint status
- View analytics and reports
- Manage all complaints

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run the server: `python manage.py runserver`

## Usage

- Access the application at `http://localhost:8000`
- Register as a citizen or authority
- Citizens can submit complaints and track them
- Authorities can access the dashboard at `/dashboard/`

## Technologies Used

- Django
- Bootstrap
- Leaflet (for maps)
- Chart.js (for analytics)
- Crispy Forms

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.