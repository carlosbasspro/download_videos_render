import subprocess
import os
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    """
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
    """

    data = request.json
    url = data.get('url')
    format = data.get('format')
    ext = data.get('ext')

    if not url or not format or not ext:
        return jsonify({"error": "URL, format, and extension are required!"}), 400

    try:
        # Define o padrão do nome do arquivo usando o título do vídeo
        output_template = os.path.join(os.getcwd(), '%(title)s.%(ext)s')

        # Comando do yt-dlp para baixar o vídeo
        command = [
            'yt-dlp',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            '--cookies', 'www.youtube.com_cookies.txt',
            '--format', f"{format}",
            '--output', output_template,
            url
        ]

        # Executa o comando yt-dlp
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Extração do título do vídeo no stdout do yt-dlp
        # Exemplo: "[download] Destination: Video_Title.mp4"
        output_lines = result.stdout.splitlines()
        destination_line = next(
            (line for line in output_lines if line.startswith("[download] Destination:")), None
        )
        if not destination_line:
            return jsonify({"error": "Failed to parse downloaded file name!"}), 500

        # Extrai o caminho do arquivo do log
        downloaded_file = destination_line.split(": ", 1)[1].strip()

        # Verifica se o arquivo existe
        if not os.path.exists(downloaded_file):
            return jsonify({"error": "Downloaded file not found!"}), 500

        # Retorna o arquivo baixado como anexo
        return send_file(downloaded_file, as_attachment=True)

    except subprocess.CalledProcessError as e:
        # Trata erros no comando yt-dlp
        return jsonify({"error": f"Failed to download video: {e.stderr}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
