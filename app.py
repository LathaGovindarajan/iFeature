from flask import Flask, request, jsonify
import subprocess
import pandas as pd
import os

app = Flask(__name__)

# Function to extract features using iFeature
def extract_features(df, feature_types):
    for feature_type in feature_types:
        for i, row in df.iterrows():
            with open("tmp.fasta", "w") as f:
                f.write(">seq\n" + row["Sequence"])
            # Adjust the path to iFeature.py based on your project structure
            command = ["python3", "iFeature/iFeature.py", "--file", "tmp.fasta", "--type", feature_type, "--out", "tmp.csv"]
            subprocess.run(command, check=True)
            if os.path.isfile("tmp.csv"):
                features_df = pd.read_csv("tmp.csv", sep='\t')
                features = [float(x) for x in features_df.values[0][1:]]
                if 'Features' in df.columns and df.at[i, "Features"]:
                    df.at[i, "Features"] += features
                else:
                    df.at[i, "Features"] = features
                os.remove("tmp.csv")
            os.remove("tmp.fasta")

# Endpoint to handle feature extraction
@app.route('/extract_features', methods=['POST'])
def extract_features_route():
    data = request.get_json()
    df = pd.DataFrame(data)
    feature_types = ["AAC", "DPC", "CTDC", "CTDT"]
    extract_features(df, feature_types)
    return jsonify({'message': 'Features extracted successfully'})

# Handle root endpoint to provide a basic response
@app.route('/', methods=['GET'])
def index():
    return "Welcome to iFeature Flask API!"

# Handle favicon.ico request to prevent 404 error
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
