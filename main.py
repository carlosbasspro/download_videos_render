import subprocess
import os
import uuid
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    '''
    Essa função lida com requisições POST para baixar conteúdos do YouTube.
    O cliente deve enviar um JSON com o seguinte formato:

    {
        "url": "URL do vídeo do YouTube",
        "format": "Formato desejado (ex: bestaudio/best ou bestvideo+bestaudio)",
        "ext": "Extensão do arquivo de saída (ex: mp3 ou mp4)"
    }

    Respostas possíveis:
    - Sucesso: Retorna o arquivo baixado como anexo.
    - Erro: Retorna uma mensagem JSON com a descrição do erro.
    '''

    data = request.json
    url = data.get('url')
    format = data.get('format')
    ext = data.get('ext')

    if not url or not format or not ext:
        return jsonify({"error": "URL, format, and extension are required!"}), 400

    try:
        current_directory = os.getcwd()
        unique_id = str(uuid.uuid4())  # Gera um ID único para o arquivo

        # Define o caminho de saída, mas agora inclui a extensão diretamente
        output_file = f"{current_directory}/{unique_id}.{ext}"

        # Defina o comando do yt-dlp usando subprocess
        command = [
            'yt-dlp',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            '--cookies', 'www.youtube.com_cookies.txt',
            '--format', f"{format}",
            '--output', output_file,  # Define o arquivo final com a extensão
            url
        ]

        # Executando o comando com subprocess
        subprocess.run(command, capture_output=True, text=True, check=True)

        # Verifica se o arquivo foi baixado
        if not os.path.exists(output_file):
            return jsonify({"error": "Failed to find downloaded file!"}), 500

        # Retorna o arquivo baixado como anexo
        return send_file(output_file, as_attachment=True)

    except subprocess.CalledProcessError as e:
        # Se ocorrer um erro ao executar o comando yt-dlp
        return jsonify({"error": f"Failed to download video: {e.stderr}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
