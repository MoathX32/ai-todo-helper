# AI To-Do Helper

AI To-Do Helper is a web application designed to help users create intelligent and actionable plans for their goals using AI.

![Active Screenshot](./active.png)

## Frameworks Used

- **Backend**: A high-performance FastAPI server, chosen for its modernity, speed, and automatic interactive API documentation.
- **Model**: Integrated the Google Gemini API for intelligent plan generation. The backend not only generates tasks but also includes a unique AI-powered validation step to ensure the generated plans are logical and relevant to the user's goal.
- **Database**: SQLite for lightweight, persistent storage of goals and tasks.
- **Frontend**: A clean, responsive frontend built with vanilla JavaScript, HTML, and CSS, demonstrating core web principles without a framework.

## Features

### Backend Features
- **AI-Powered Plan Generation**: Generates detailed, actionable plans for user-defined goals using the Google Gemini API.
- **Plan Validation**: Includes a unique AI-powered validation step to ensure the generated plans are logical and relevant to the user's goal.
- **Database Integration**: Stores goals and tasks in a SQLite database for lightweight, persistent storage.
- **RESTful API**: Provides endpoints for creating, retrieving, updating, and deleting goals and tasks.

### Frontend Features
- **Interactive Goal Management**: Allows users to create, view, and delete goals.
- **Task Completion Tracking**: Users can mark tasks as completed, and progress is visually represented.
- **Floating Messages**: Displays feedback directly on the webpage for better user experience.
- **Responsive Design**: A clean, responsive frontend built with vanilla JavaScript, HTML, and CSS, demonstrating core web principles without a framework.

### Additional Features
- **Error Handling**: Provides clear and actionable error messages when inputs are invalid or plans cannot be generated.
- **Customizable UI**: Includes modern CSS styling for an intuitive and visually appealing interface.

## Documentation

### Installation

#### Prerequisites
- Python 3.10 or higher
- Node.js and npm
- Docker (optional, for containerized deployment)

#### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/MoathX32/ai-todo-helper.git
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
