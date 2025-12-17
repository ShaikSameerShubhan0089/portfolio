<<<<<<< HEAD
from flask import jsonify
import json

def load_scene_config(file_path):
    """Load the 3D scene configuration from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        return {"error": "Scene configuration file not found."}
    except json.JSONDecodeError:
        return {"error": "Error decoding JSON from the scene configuration file."}

def load_animations(animation_files):
    """Load animations from a list of animation file paths."""
    animations = {}
    for file_path in animation_files:
        try:
            with open(file_path, 'r') as file:
                animations[file_path] = json.load(file)
        except FileNotFoundError:
            animations[file_path] = {"error": "Animation file not found."}
        except json.JSONDecodeError:
            animations[file_path] = {"error": "Error decoding JSON from the animation file."}
=======
from flask import jsonify
import json

def load_scene_config(file_path):
    """Load the 3D scene configuration from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        return {"error": "Scene configuration file not found."}
    except json.JSONDecodeError:
        return {"error": "Error decoding JSON from the scene configuration file."}

def load_animations(animation_files):
    """Load animations from a list of animation file paths."""
    animations = {}
    for file_path in animation_files:
        try:
            with open(file_path, 'r') as file:
                animations[file_path] = json.load(file)
        except FileNotFoundError:
            animations[file_path] = {"error": "Animation file not found."}
        except json.JSONDecodeError:
            animations[file_path] = {"error": "Error decoding JSON from the animation file."}
>>>>>>> 876a04cc55f654954d2b5653d97af0de107da3fa
    return animations