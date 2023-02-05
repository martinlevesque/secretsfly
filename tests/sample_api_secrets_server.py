from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/secrets/")
def secrets():
    secret_data = {
        "secrets": [
            {
                "name": "secret1name",
                "value": "secret1value",
            },
            {
                "name": "secret2name",
                "value": "secret2value",
            },
        ]
    }
    return jsonify(secret_data)


if __name__ == '__main__':
    app.run(debug=True)
