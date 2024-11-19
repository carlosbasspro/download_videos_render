from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os

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


    # Configurações do yt-dlp
    ydl_opts = {
        "format": f"{format}",
        "outtmpl": "download/%(title)s.%(ext)s",
        "cookiefile": "www.youtube.com_cookies.txt",
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get("title", None)
            video_ext = info_dict.get("ext", None)
            video_path = f"./download/{video_title}.{video_ext}"
            final_path = f"./download/{video_title}.{ext}"
            os.rename(video_path, final_path)

            return send_file(final_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
