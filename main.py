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

    # Defina o comando do yt-dlp usando subprocess
    command = [
        'yt-dlp',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        '--cookies-from-browser', 'chrome',  # Usando os cookies do Chrome
        '--format', f"{format}",
        '--output', "download/%(title)s.%(ext)s",  # Defina o caminho de saída para o arquivo
        url
    ]

    try:
        # Executando o comando com subprocess
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # A saída de sucesso vai indicar onde o arquivo foi salvo
        video_title = result.stdout.strip()  # Supondo que o título seja retornado na saída
        video_path = f"./download/{video_title}.{ext}"
        final_path = f"/storage/emulated/0/Download/BaixarTube Downloads/{video_title}.{ext}"

        # Renomeia o arquivo para o local final
        os.rename(video_path, final_path)

        return send_file(final_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        # Se ocorrer um erro ao executar o comando yt-dlp
        return jsonify({"error": f"Failed to download video: {e.stderr}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
