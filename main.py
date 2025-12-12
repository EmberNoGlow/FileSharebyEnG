import os
from flask import Flask, request, send_from_directory, render_template_string
from werkzeug.utils import secure_filename

# --- Configuration ---
# Directory where files will be stored
UPLOAD_FOLDER = 'shared_files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'zip'}
# Port on which the server will run
PORT = 5000

# Create the upload folder if it does not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Helper Functions ---

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Minimalistic HTML Template for the web interface
HTML_TEMPLATE = """
<!doctype html>
<title>File Exchange (Flask)</title>
<style>
    body { font-family: sans-serif; margin: 20px; background-color: #f9f9f9; }
    .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
    h2 { color: #555; margin-top: 25px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    th { background-color: #e6e6e6; color: #333; }
    input[type="file"] { padding: 8px; border: 1px solid #ccc; border-radius: 4px; margin-right: 10px; }
    input[type="submit"] { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
    input[type="submit"]:hover { background-color: #0056b3; }
    a { color: #007bff; text-decoration: none; }
    a:hover { text-decoration: underline; }
</style>

<body>
    <div class="container">
        <h1>Cross-Platform File Exchange</h1>
        
        <!-- Upload Form -->
        <h2>1. Upload File to this Device</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="Upload">
        </form>
        
        <hr>

        <!-- File List for Download -->
        <h2>2. Download File from this Device</h2>
        {% if files %}
            <table>
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for file in files %}
                        <tr>
                            <td>{{ file }}</td>
                            <td><a href="/download/{{ file }}">Download</a></td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p>The '{{ UPLOAD_FOLDER }}' folder is currently empty.</p>
        {% endif %}
        
        <p style="margin-top: 30px; font-size: small; color: #777;">
            To access this exchange from other devices, use the following address in their browser: <strong>{{ ip_address }}:{{ port }}</strong>
        </p>
    </div>
</body>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            return "Error: No file part", 400
        
        file = request.files['file']
        
        if file.filename == '':
            return "Error: No selected file", 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return f"File '{filename}' successfully uploaded!"
        else:
            return "Error: File type not allowed (you can pack file into .zip)", 400

    # GET request: display the interface
    
    # Get list of files in the shared folder
    files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    
    # Determine the local IP address of the host machine
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1 (Check your network settings)"

    return render_template_string(
        HTML_TEMPLATE, 
        files=files, 
        UPLOAD_FOLDER=UPLOAD_FOLDER,
        ip_address=local_ip,
        port=PORT
    )

@app.route('/download/<filename>')
def download_file(filename):
    """Sends the requested file to the user for download."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404


if __name__ == '__main__':
    print("="*50)
    print("FLASK FILE EXCHANGER STARTED")
    print(f"Files will be stored in the directory: ./{UPLOAD_FOLDER}")
    print("To access from other devices, open a browser and enter:")
    print(f"http://<THIS_DEVICE_IP>:{PORT}")
    print("="*50)
    
    # Run the server publicly on port 5000
    app.run(host='0.0.0.0', port=PORT, debug=True)