import subprocess
import os
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

    # Define o caminho final diretamente
    download_dir = "/storage/emulated/0/Download/BaixarTube Downloads"
    os.makedirs(download_dir, exist_ok=True)  # Garante que o diretório exista
    output_template = f"{download_dir}/%(title)s.%(ext)s"

    # Defina o comando do yt-dlp usando subprocess
    command = [
        'yt-dlp',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        '--cookies', 'www.youtube.com_cookies.txt',
        '--format', f"{format}",
        '--output', output_template,  # Define o caminho final diretamente
        url
    ]

    try:
        # Executando o comando com subprocess
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Parseando o título do vídeo a partir da saída do yt-dlp
        lines = result.stdout.strip().split("\n")
        video_file = None
        for line in lines:
            if "Destination:" in line:
                video_file = line.split("Destination:")[1].strip()
                break

        if not video_file or not os.path.exists(video_file):
            return jsonify({"error": "Failed to find downloaded file!"}), 500

        return send_file(video_file, as_attachment=True)

    except subprocess.CalledProcessError as e:
        # Se ocorrer um erro ao executar o comando yt-dlp
        return jsonify({"error": f"Failed to download video: {e.stderr}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
