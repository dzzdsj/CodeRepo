from flask import Flask, request, jsonify
from intent_identification import IntentIdentification
from user_functions import UserFunctions
import configparser


app = Flask(__name__)

def load_config(filepath='config.txt'):
    """加载配置文件."""
    config = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

@app.route('/identify_intent', methods=['POST'])
def identify_intent():
    """鉴别prompt意图的HTTP端点."""
    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        config = load_config()
        base_url = config.get('base_url')
        api_key = config.get('api_key')
        model = config.get('model')

        if not base_url or not api_key or not model:
            return jsonify({'error': 'Base URL, API key, or Model is missing in config'}), 500

        intent_identifier = IntentIdentification(base_url, api_key, model)
        user_funcs = UserFunctions()
        intent_identifier.set_functions(user_funcs)

        results = intent_identifier.identify(prompt)
        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)