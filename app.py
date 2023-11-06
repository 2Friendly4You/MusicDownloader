import os
import subprocess
import threading
from flask import Flask, render_template, request, jsonify, send_file
import uuid
import shutil
import time

app = Flask(__name__)

# A list to store pending request UUIDs
pending_requests = []

def run_spotdl(unique_id, search_query, audio_format, lyrics_format, output_format):
    global pending_requests

    download_folder = os.path.join('templates', 'download', unique_id)
    os.makedirs(download_folder, exist_ok=True)

    # Run spotdl with the provided parameters and unique folder
    if not lyrics_format:
        command = f'spotdl "{search_query}" --audio {audio_format} --format {output_format} --output "{download_folder}"'
    else:
        command = f'spotdl "{search_query}" --audio {audio_format} --lyrics {lyrics_format} --format {output_format} --output "{download_folder}"'

    result = subprocess.run(command, shell=True, check=True, text=True)

    if result.returncode == 0:
        # Create a zip file with the contents of the folder
        try:
            shutil.make_archive(download_folder, 'zip', download_folder)
        except FileNotFoundError as e:
            time.sleep(1)
            shutil.make_archive(download_folder, 'zip', download_folder)

    # Remove the original folder
    shutil.rmtree(download_folder)

    # Remove the unique_id from the pending_requests list after the subprocess command has finished executing
    pending_requests.remove(unique_id)

def is_request_pending(unique_id):
    global pending_requests
    return unique_id in pending_requests

def run_spotdl(unique_id, search_query, audio_format, lyrics_format, output_format):
    global pending_requests

    download_folder = os.path.join('templates', 'download', unique_id)
    os.makedirs(download_folder, exist_ok=True)

    # Run spotdl with the provided parameters and unique folder
    if not lyrics_format:
        command = f'spotdl "{search_query}" --audio {audio_format} --format {output_format} --output "{download_folder}"'
    else:
        command = f'spotdl "{search_query}" --audio {audio_format} --lyrics {lyrics_format} --format {output_format} --output "{download_folder}"'

    result = subprocess.run(command, shell=True, check=True, text=True)

    if result.returncode == 0:
        # Create a zip file with the contents of the folder
        try:
            shutil.make_archive(download_folder, 'zip', download_folder)
        except FileNotFoundError as e:
            time.sleep(1)
            shutil.make_archive(download_folder, 'zip', download_folder)

    # Remove the original folder
    shutil.rmtree(download_folder)
    pending_requests.remove(unique_id)

@app.route('/')
def index():
    return render_template('index.html', pending_requests=pending_requests)

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    audio_format = request.form['audio_format']
    lyrics_format = request.form['lyrics_format']
    output_format = request.form['output_format']

    ## Check if the search query is empty
    if not search_query:
        return jsonify({'status': 'error', 'message': 'Search query is required'})

    # Generate a new unique ID
    while True:
        unique_id = str(uuid.uuid4())
        download_folder = os.path.join('templates', 'download', unique_id)
        if not os.path.exists(download_folder):
            break

    # Add the UUID to the list of pending requests
    pending_requests.append(unique_id)

    # Run spotdl in a background thread
    thread = threading.Thread(target=run_spotdl, args=(unique_id, search_query, audio_format, lyrics_format, output_format))
    thread.start()

    return jsonify({'status': 'success', 'message': 'Song download started', 'unique_id': unique_id})

@app.route('/status/<unique_id>', methods=['GET'])
def check_request(unique_id):
    if is_request_pending(unique_id):
        return jsonify({'status': 'pending'})
    else:
        return jsonify({'status': 'completed'})

@app.route('/download/<unique_id>', methods=['GET', 'POST'])
def download(unique_id):
    download_file = os.path.join('templates', 'download', unique_id + ".zip")
    if os.path.isfile(download_file):
        return send_file(download_file, as_attachment=True)
    else:
        return jsonify({'status': 'error', 'message': 'File not found'})
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
 