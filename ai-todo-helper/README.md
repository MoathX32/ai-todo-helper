# AI To-Do Helper

AI To-Do Helper is a web application designed to help users create intelligent and actionable plans for their goals using AI. The application leverages FastAPI for the backend and a modern JavaScript frontend to deliver a seamless user experience.

## Features

### Backend Features
- **AI-Powered Plan Generation**: Generates detailed, actionable plans for user-defined goals using the Gemini AI model.
- **Plan Validation**: Ensures that generated plans are relevant and logical by validating them with AI.
- **Database Integration**: Stores goals and tasks in a SQLite database for persistence.
- **RESTful API**: Provides endpoints for creating, retrieving, updating, and deleting goals and tasks.

### Frontend Features
- **Interactive Goal Management**: Allows users to create, view, and delete goals.
- **Task Completion Tracking**: Users can mark tasks as completed, and progress is visually represented.
- **Floating Messages**: Displays feedback directly on the webpage for better user experience.
- **Responsive Design**: Ensures the application works seamlessly across devices.

### Additional Features
- **Error Handling**: Provides clear and actionable error messages when inputs are invalid or plans cannot be generated.
- **Customizable UI**: Includes modern CSS styling for an intuitive and visually appealing interface.

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js and npm
- Docker (optional, for containerized deployment)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-todo-helper.git
   cd ai-todo-helper
   ```

2. Install backend dependencies:
   ```bash
   cd server_py
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd ../web-plain
   npm install
   ```

4. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

5. Open `index.html` in your browser to access the frontend.

### Docker Deployment
1. Build the Docker image:
   ```bash
   docker build -t ai-todo-helper .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 ai-todo-helper
   ```

## API Endpoints

### Goals
- `POST /api/goals`: Create a new goal.
- `GET /api/goals`: Retrieve all goals.
- `GET /api/goals/{goal_id}`: Retrieve a specific goal.
- `DELETE /api/goals/{goal_id}`: Delete a specific goal.

### Tasks
- `PATCH /api/tasks/{task_id}/toggle`: Toggle task completion.

## Technologies Used
- **Backend**: FastAPI, SQLite, Google Generative AI
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.

## Contact
For questions or support, please contact [your-email@example.com].
