import os

from flask import Flask, jsonify, render_template, request, send_file
from pdf_compressor import PDFCompressor
from huffman_compression import HuffmanCompressor
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'

# Ensure upload and compressed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['COMPRESSED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get compression percentage from form (default to 50)
    compression_percentage = int(request.form.get('compression_percentage', 50))
    
    try:
        # Secure filename and save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Determine compression method based on file type
        if filename.lower().endswith('.pdf'):
            # PDF compression
            compressed_result = PDFCompressor.compress_pdf(
                filepath, 
                output_path=os.path.join(app.config['COMPRESSED_FOLDER'], f'compressed_{filename}'),
                compression_percentage=compression_percentage
            )
        else:
            # Huffman compression for other file types
            compressed_result = HuffmanCompressor.compress_file(
                filepath, 
                output_path=os.path.join(app.config['COMPRESSED_FOLDER'], f'compressed_{filename}.huffman'),
                compression_percentage=compression_percentage
            )
        
        return jsonify({
            'original_filename': filename,
            'compressed_filename': os.path.basename(compressed_result['compressed_path']),
            'original_size': compressed_result['original_size'],
            'compressed_size': compressed_result['compressed_size'],
            'compression_percentage': compressed_result['compression_percentage']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['COMPRESSED_FOLDER'], filename), 
            as_attachment=True
        )
    except Exception as e:
        return str(e), 404

@app.route('/decompress', methods=['POST'])
def decompress_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Secure filename and save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Determine decompression method
        if filename.lower().endswith('.huffman'):
            # Huffman decompression
            decompressed_path = HuffmanCompressor.decompress_file(
                filepath, 
                output_path=os.path.join(app.config['COMPRESSED_FOLDER'], filename.replace('.huffman', ''))
            )
        elif filename.lower().startswith('compressed_') and filename.lower().endswith('.pdf'):
            # PDF decompression (essentially just restoring the original file)
            original_filename = filename[len('compressed_'):]
            decompressed_path = os.path.join(app.config['COMPRESSED_FOLDER'], original_filename)
            
            # If the compressed file exists, copy it back to original name
            if os.path.exists(filepath):
                with open(filepath, 'rb') as compressed_file:
                    with open(decompressed_path, 'wb') as original_file:
                        original_file.write(compressed_file.read())
            else:
                return jsonify({'error': 'Compressed PDF not found'}), 404
        else:
            return jsonify({'error': 'Unsupported file type for decompression'}), 400
        
        return jsonify({
            'original_filename': os.path.basename(decompressed_path),
            'decompressed_path': decompressed_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
