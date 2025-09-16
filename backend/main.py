from flask import Flask, jsonify, request
from tool import deal_data
from flask_cors import CORS
import os
import tempfile

app = Flask(__name__)
CORS(app) # 允许所有来源跨域
@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    file_path = request.args.get('file_path', '')
    if not file_path:
        return jsonify({'error': '请提供file_path参数'})
    result = deal_data.photo(file_path)
    return jsonify(result)

@app.route('/parse_image', methods=['POST'])
def parse_image():
    if 'image' not in request.files:
        return jsonify({'error': '未上传图片'})
    image = request.files['image']
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[-1]) as tmp:
        image.save(tmp.name)
        result = deal_data.photo(tmp.name)
    os.remove(tmp.name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)