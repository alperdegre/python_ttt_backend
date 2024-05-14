# Python TicTacToe Backend

This is the backend for my TicTacToe game, built using FastAPI and deployed using CI/CD with Github Actions. This backend handles the whole game logic, authentication, lobby setup, and manages real-time game updates using events via WebSockets.

A demo is deployed on my personal site [here!](http://ttt.alperdegre.com). Feel free to play with friends.

## Installation

If you want to set up the project locally:

1. Clone the repository:
   ```sh
   git clone https://github.com/alperdegre/python_ttt_backend
   ```

2. Navigate to the project directory:
   ```sh
   cd python_ttt_backend
   ```

3. Create a virtual environment:
   ```sh
   python3 -m venv venv
   ```

4. Activate the virtual environment:
   ```sh
   source venv/bin/activate
   ```

5. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

6. Run the application:
   ```sh
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```