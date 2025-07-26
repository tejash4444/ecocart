### Prerequisites

* Python 3.x installed on your system.
* The project files downloaded to your local machine.

### Installation and Running the Application

Follow these steps to get your development environment running.

1.  **Open your command prompt or terminal.**
    Navigate to the root directory of the project where the `requirements.txt` and `app.py` files are located.

2.  **Install the required packages.**
    Run the following command to install all the necessary dependencies listed in the `requirements.txt` file:
    ```bash
    py -m pip install -r requirements.txt
    ```
    *Note: Depending on your system's Python installation, you might need to use `python` or `python3` instead of `py`.*

3.  **Run the Flask application.**
    Once the dependencies are installed, start the development server with this command:
    ```bash
    py -m flask --app app run
    ```
    *Again, you may need to use `python` or `python3` if `py` does not work.*

4.  **View the application.**
    The application will now be running. Open your web browser and navigate to the address shown in the terminal, which is typically `http://127.0.0.1:5000`.
