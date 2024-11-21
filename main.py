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
        unique_id = str(uuid.uuid4())  # Gera um ID único para o arquivo
        output_file = f"{current_directory}/{unique_id}.{ext}"

        command = [
            'yt-dlp',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            '--cookies', 'www.youtube.com_cookies.txt',
            '--format', f"{format}",
            '--output', output_file,
            url
        ]

        # Executando o comando com subprocess
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Verifica se o arquivo foi baixado
        if not os.path.exists(output_file):
            return jsonify({"error": "Failed to find downloaded file!", "stderr": result.stderr}), 500

        # Retorna o arquivo baixado como anexo
        return send_file(output_file, as_attachment=True)

    except subprocess.CalledProcessError as e:
        # Captura a saída de erro e a saída padrão
        return jsonify({
            "error": "Failed to download video",
            "stderr": e.stderr,
            "stdout": e.stdout
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
