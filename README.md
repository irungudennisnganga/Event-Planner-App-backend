# Event-Planner-App-backend
Event Planner is a web application built with Flask and React that aims to help individuals and organizations plan and organize events efficiently. It provides features for managing events, tasks, resources, expenses, and more, all within a user-friendly interface.

## Features

- User Registration and Authentication
- Dashboard Overview
- Event Management (Create, View, Edit, Delete)
- Task Assignment and Tracking
- Resource Management
- Collaboration and Communication
- Budget Planning and Expense Tracking

## Technologies Used

- Flask: Backend framework for building the API and handling server-side logic.
- SQLAlchemy: ORM for interacting with the PostgreSQL database.
- React: Frontend library for building interactive user interfaces.
- Flask-Migrate: Extension for managing database migrations with Flask.

## Getting Started

1. Clone the repository:

````bash
git clone https://github.com/irungudennisnganga/Event-Planner-App-backend

````

2. Navigate to the project directory:

cd EVENT-PLANNER-APP-BACKEND
pip install -r requirements.txt
python manage.py db upgrade
python manage.py run

3. Open your web browser and navigate to http://localhost:3000 to access the application.

## Contributing
Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. reate a new branch (git checkout -b feature/new-feature).
3. Make your changes and commit them (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature/new-feature).
5. Create a pull request.

---

## User Management

- API endpoints for user registration, login, and authentication using Flask routes.
- JWT authentication for securing endpoints and validating user sessions.

## Database Integration

- Relational database (e.g., PostgreSQL) to store user information, event data, tasks, resources, and expenses.
- SQLAlchemy ORM for interacting with the database within Flask applications.

## Event Management API

- CRUD operations on events, tasks, resources, and expenses.
- Endpoints for creating, updating, deleting events, managing tasks, allocating resources, and recording expenses.

## Task Assignment and Tracking Endpoint

- Endpoints for assigning tasks to team members, updating task status, and tracking task completion.
- Logic for sending notifications and reminders for upcoming tasks and deadlines.

## Resource Management Endpoint

- Endpoints for managing event-related resources such as venues, equipment, and materials.
- Logic for reserving resources, checking availability, and tracking resource usage.

## Collaboration and Communication Endpoint

- Endpoints for facilitating collaboration and communication among event organizers and participants.
- Integration with messaging services or email APIs for sending event updates and notifications.

## Budget Planning and Expense Tracking Endpoint

- Endpoints for setting event budgets, recording expenses, and generating budget reports.
- Logic for calculating total expenses, monitoring spending against budget limits, and providing insights into cost management.

## Authentication Middleware

- Middleware for securing API endpoints and validating user authentication using JWT tokens.
- Decorators to enforce authentication requirements for accessing protected resources.

## Logging and Monitoring

- Logging of critical events and monitoring of system health to identify and resolve issues proactively.
- Log user actions, API requests, and errors to track system activity and troubleshoot problems.

---

This README provides an overview of the backend functionalities of the Event Planner App. For detailed documentation and usage instructions, please refer to the code comments and documentation provided within the application or visit the project's official documentation website.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
