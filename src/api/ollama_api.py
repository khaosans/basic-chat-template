import requests

def check_ollama_server():
    """Check if Ollama server is running."""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_available_models():
    """Fetch available models from Ollama API."""
    if not check_ollama_server():
        raise ConnectionError("Cannot connect to Ollama server. Please ensure it's running.")
        
    try:
        response = requests.get('http://localhost:11434/api/tags')
        response.raise_for_status()
        models = response.json().get('models', [])
        return [model['name'] for model in models] or ['mistral']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching models: {e}")
        return ['mistral']  # Return default model as fallback