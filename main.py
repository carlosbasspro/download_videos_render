import subprocess
import os
import uuid
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format = data.get('format')
    ext = data.get('ext')

    if not url or not format or not ext:
        return jsonify({"error": "URL, format, and extension are required!"}), 400

    try:
        current_directory = os.getcwd()
        unique_id = str(uuid.uuid4())
        output_file = os.path.join(current_directory, f"{unique_id}.{ext}")

        command = [
            'yt-dlp',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            '--cookies', 'www.youtube.com_cookies.txt',
            '--format', f"{format}",
            '--output', output_file,
            url
        ]

        subprocess.run(command, capture_output=True, text=True, check=True)

        # Verifica se o arquivo baixado existe (pode ser salvo com uma extensão diferente)
        if os.path.exists(output_file):
            return send_file(output_file, as_attachment=True)
        
        # Se o arquivo original não existir, procure por arquivos com o mesmo UUID
        for file in os.listdir(current_directory):
            if file.startswith(unique_id):
                downloaded_file = os.path.join(current_directory, file)
                # Renomeia o arquivo para a extensão desejada
                os.rename(downloaded_file, output_file)
                return send_file(output_file, as_attachment=True)

        return jsonify({"error": "Failed to find downloaded file!"}), 500

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Failed to download video!",
            "stderr": e.stderr
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
