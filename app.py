from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
from flask_socketio import SocketIO, emit
import image_processing.measure_from_video
import image_processing.measure_from_camera
import secrets
import os

# App object
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Socket object
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

# Image processing object
# measure_from_video = image_processing.measure_from_video.MeasureFromVideo('data/videos_pendule/video_robustness.avi')
measure_from_video = image_processing.measure_from_camera.MeasureFromCamera(0)

# Global variables
ip_login = None
ip_save = None
btnState = True
plotReady = False
running = False

# Users known
users = [
    {"name": "student", "pwd": "pendule"}
]


# Check if the user is known
def search_user(username, password):
    for user in users:
        if user['name'] == username and user['pwd'] == password:
            return user
    return None


# Main web page
@app.route('/')
def index():
    print('IP user : ' + request.environ['REMOTE_ADDR'])
    print('IP serveur : ' + request.remote_addr)

    if 'username' in session:
        return redirect(url_for('mesure'))
    else:
        return redirect(url_for('login'))


# Login web page
@app.route('/login', methods=["POST", "GET"])
def login():
    global ip_login
    global ip_save

    # Check if POST request
    if request.method == "POST" : 
        # Get the username and password that the user has entered
        name = request.form.get('username')
        pwd = request.form.get('password')

        # Check if the username and password are known
        user = search_user(name, pwd)

        # If user known
        if user != None and ip_login == None:
            # Save ip of user connected
            ip_login = request.remote_addr
            ip_save = request.remote_addr

            # Add user to the session
            session['username'] = user['name']

            # Redirect user to mesure web page
            return redirect(url_for('mesure'))
        else:
            # Display user to login web page
            return render_template("login.html")
    else:
        # if user already connected
        if 'username' in session:
            # Redirect user to mesure web page
            return redirect(url_for('mesure'))
        # Display user to login web page
        return render_template("login.html")


# Logout web page
@app.route('/logout', methods=["POST", "GET"])
def logout():
    global ip_login
    global ip_save
    global btnState
    global plotReady
    
    btnState = True
    plotReady = False

    # Forbidding disconnection by get request
    # Another user could disconnect any user connected to a session
    if request.method == "GET":
        return redirect(url_for('mesure'))

    # Remove csv file of data if exists
    file = 'mesure.csv'
    if(os.path.exists(file) and os.path.isfile(file)):
        os.remove(file)
        print("file deleted")
    else:
        print("file not found")

    # Clear ip variables
    ip_login = None
    ip_save = None

    # Pop user of session
    session.pop('username', None)
    return redirect(url_for('login'))


# Mesure web page
@app.route('/mesure', methods=["POST", "GET"])
def mesure():
    # Check if a user is connected
    if ('username' in session) and (ip_save == request.remote_addr) :
        # Display mesure web page
        return render_template("mesure.html",sync_mode=socketio.async_mode)
    else:
        # Redirect user to login web page
        return redirect(url_for('login'))


# Get global variables of "app.py"
@app.route('/getValues', methods=['POST'])
def get_Values():
    global plotReady
    global btnState
    global running
    return {'_plotReady' : plotReady, '_btnState' : btnState, '_running' : running}


# Get data in csv file
@app.route("/getPlotCSV")
def getPlotCSV():
    # Check if a user is connected
    if ('username' in session) and (ip_save == request.remote_addr) :
        with open("mesure.csv") as fp:
            csv = fp.read()
        return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-disposition":"attachment; filename=mesure.csv"})
    else:
        # Redirect user to login web page
        return redirect(url_for('login'))


# Get the data from the measure class
@app.route('/data')
def get_data():
    # Check if a user is connected
    if ('username' in session) and (ip_save == request.remote_addr) :
        data = measure_from_video.signal
        return jsonify(data)
    else:
        # Redirect user to login web page
        return redirect(url_for('login'))


# Background task
@socketio.on('run', namespace='/backgroundTasks')
def run_lengthy_task(data):
    try:
        global btnState
        global plotReady
        global running

        btnState = False
        plotReady = False
        running = True

        # Get acquisition time
        duration = int(data['duration'])

        # Run measures from video
        # measure_from_video.run()  # To run tests on videos
        measure_from_video.run(duration)

        btnState = True
        plotReady = True
        running = False

        # Emit done event
        emit('task_done', broadcast=True)
    except Exception as ex:
        print(ex)


# Stop background task
@socketio.on('stop', namespace='/backgroundTasks')
def stop_task():
    try:
        global btnState
        global running
        global plotReady
        
        btnState = True
        running = False
        plotReady = True

        # Stop measures from video
        measure_from_video.early_stopping()
    except Exception as ex:
        print(ex)


# Connection of WebSocket
@socketio.on('connect')
def connect():
    global ip_login
    global ip_save
    if ip_save == request.remote_addr :
            ip_login = ip_save
    print('Client connected')


# Disconnection of WebSocket
@socketio.on('disconnect')
def disconnect():
    global ip_login
    global ip_save
    print('Client disconnected')

    if ip_save == request.remote_addr :
        ip_login = None
        session.pop('username', None)
        print('IP disconnected')

    print(request.remote_addr)


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app)