from flask import Flask, request, jsonify, send_from_directory
from llm import generate_response
from logger import logger

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory('static', 'page1.html')

@app.route('/page2')
def page2():
    return send_from_directory('static', 'page2.html')

@app.route('/page3')
def page3():
    return send_from_directory('static', 'page3.html')

@app.route('/process', methods=['POST'])
def process_prompt():
    data = request.get_json()
    logger.info("Received data:", data)

    response = generate_response(data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=False)
