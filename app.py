from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Directory to save downloads
DOWNLOAD_DIR = './downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure the download directory exists

# Fetch video info using yt-dlp
@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = [{'format_id': f['format_id'], 'ext': f['ext']}
                       for f in info_dict['formats'] if f['vcodec'] != 'none']
            return jsonify({'title': info_dict['title'], 'formats': formats})
    except Exception as e:
        logging.error(f"Error fetching video info: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Download the selected format
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # yt-dlp options for downloading the best video and audio
        ydl_opts = {
            'format': 'best',
            'outtmpl': '{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',  # Ensures output format is mp4
            'postprocessors': [{"for this gmail me"
            }],
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            # Sanitize the video title to avoid file path issues
            video_title = info_dict.get('title', 'downloaded_video').replace('/', '_')
            file_path = os.path.join(DOWNLOAD_DIR, f"{video_title}.mp4")
        
        # Check if the file exists before attempting to send it
        if not os.path.exists(file_path):
            logging.error("File not found after download.")
            return jsonify({'error': 'Download failed, file not found'}), 500

        logging.info(f"Download successful, serving file: {file_path}")
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        logging.error(f"Error during download: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Serve frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
