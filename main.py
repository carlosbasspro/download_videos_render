from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format = data.get('format')
    ext = data.get('ext')

    if not url or not format or not ext:
        return jsonify({"error": "URL, format, and extension are required!"}), 400

    # Diretório atual
    current_directory = os.getcwd()

    # Criação do diretório download (se não existir)
    download_dir = "download"
    os.makedirs(download_dir, exist_ok=True)

    # Configurações do yt-dlp
    ydl_opts = {
        "format": f"{format}",
        "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
        "cookiefile": "www.youtube.com_cookies.txt",
        "sanitize_filename": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get("title", "video")
            video_ext = info_dict.get("ext", ext)
            video_path = os.path.join(download_dir, f"{video_title}.{video_ext}")
            final_path = os.path.join(download_dir, f"{video_title}.{ext}")

            # Verifique se o arquivo existe antes de renomear
            if not os.path.exists(video_path):
                return jsonify({
                    "error": f"Arquivo não encontrado: {video_path}",
                    "server_directory": current_directory
                }), 500

            # Renomear arquivo
            os.rename(video_path, final_path)

            return send_file(final_path, as_attachment=True)

    except Exception as e:
        # Retornar erro com diretório do servidor
        return jsonify({
            "error": str(e),
            "server_directory": current_directory
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
