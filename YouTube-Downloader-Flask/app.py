from flask import Flask, request, render_template, send_file, url_for, redirect
import yt_dlp
import os

app = Flask(__name__)
downloads = {} 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/formats', methods=['POST'])
def list_formats():
    try:
        url = request.form.get('url')

        if not url or not (url.startswith("https://www.youtube.com/") or url.startswith("https://youtu.be/")):
            return "Geçersiz URL. Lütfen geçerli bir YouTube bağlantısı girin."

        ydl_opts = {
            'http_headers': {
                'User-Agent': (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/108.0.0.0 Safari/537.36"
                )
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            video_title = info.get('title', 'downloaded_video').replace(" ", "_")

        audio_formats = [f for f in formats if f.get('acodec') != 'none']
        video_formats = [f for f in formats if f['ext'] == 'mp4' and f.get('height')]

        resolutions = sorted(set(f['height'] for f in video_formats))

        return render_template(
            'formats.html',
            url=url,
            title=video_title,
            audio_formats=audio_formats, 
            resolutions=resolutions,
        )
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@app.route('/download', methods=['POST'])
def download_video():
    try:
        url = request.form.get('url')
        format_type = request.form.get('format_type')
        resolution = request.form.get('resolution')

        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'downloaded_video').replace(" ", "_")

        ext = 'mp3' if format_type == 'mp3' else 'mp4'

        download_path = os.path.join(os.getcwd(), f"{video_title}.%(ext)s")
        if format_type == 'mp3':
            ydl_format = 'bestaudio/best'
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_format = f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
            postprocessors = []

        ydl_opts = {
            'format': ydl_format,
            'outtmpl': download_path,
            'ffmpeg_location': r'C:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin',
            'merge_output_format': ext,
            'quiet': False,
            'postprocessors': postprocessors,
            'http_headers': {
                'User-Agent': (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/108.0.0.0 Safari/537.36"
                )
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
            if result != 0:
                return "İndirme işlemi başarısız oldu."


        final_filename = f"{video_title}.{ext}"
        final_path = os.path.join(os.getcwd(), final_filename)

        if not os.path.exists(final_path):
            return f"Hata: Dosya bulunamadı - {final_path}"

        downloads[final_filename] = final_path

        return redirect(url_for('download_link', filename=final_filename))
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@app.route('/download_link/<filename>')
def download_link(filename):
    if filename in downloads:
        return f"""
            <h1>İndirme Hazır</h1>
            <p>Dosyayı indirmek için aşağıdaki bağlantıya tıklayın:</p>
            <a href="{url_for('serve_file', filename=filename)}" download>Dosyayı İndir</a>
        """
    else:
        return "Dosya bulunamadı.", 404

@app.route('/serve_file/<filename>')
def serve_file(filename):
    file_path = downloads.get(filename)
    if file_path and os.path.exists(file_path):
        ext = filename.split('.')[-1]
        mimetype = 'audio/mpeg' if ext == 'mp3' else 'video/mp4'
        return send_file(file_path, as_attachment=True, download_name=filename, mimetype=mimetype)
    else:
        return "Dosya bulunamadı.", 404

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
