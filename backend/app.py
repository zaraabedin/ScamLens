import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from analyzer import (
    analyze_with_ai,
    local_fallback_analysis,
    analyze_screenshot
)


# ==========================================================
# CONFIGURATION
# ==========================================================

load_dotenv()

app = Flask(__name__)

CORS(app)


# ==========================================================
# BASIC ROUTES
# ==========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "name": "ScamLens API",
        "version": "1.0",
        "status": "running",
        "message": "Think before you click."
    })


@app.route("/health", methods=["GET"])
def health():

    api_configured = bool(
        os.getenv("OPENAI_API_KEY")
    )

    return jsonify({
        "status": "healthy",
        "ai_configured": api_configured
    })


# ==========================================================
# ANALYZE ENDPOINT
# ==========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "error": "Request body must contain JSON."
            }), 400


        message = data.get("text", "")

        if not isinstance(message, str):

            return jsonify({
                "error": "text must be a string."
            }), 400


        message = message.strip()


        # ----------------------------------------------
        # Validate
        # ----------------------------------------------

        if not message:

            return jsonify({
                "error": "Please provide a message to analyze."
            }), 400


        if len(message) > 5000:

            return jsonify({
                "error":
                    "Message is too long. Maximum length is 5000 characters."
            }), 400


        # ----------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------

        api_key = os.getenv("OPENAI_API_KEY")


        if api_key:

            try:

                result = analyze_with_ai(message)

                result["analysis_source"] = "ai"

                return jsonify(result), 200

            except Exception as ai_error:

                print(
                    "AI analysis failed:",
                    str(ai_error)
                )

                print(
                    "Using local fallback analyzer."
                )


        # ----------------------------------------------
        # FALLBACK
        # ----------------------------------------------

        result = local_fallback_analysis(message)

        result["analysis_source"] = "fallback"

        return jsonify(result), 200


    except Exception as error:

        print(
            "Unexpected server error:",
            str(error)
        )

        return jsonify({
            "error":
                "Something went wrong while analyzing the message."
        }), 500

# ==========================================================
# SCREENSHOT ANALYSIS
# ==========================================================

@app.route("/analyze-image", methods=["POST"])
def analyze_image():

    try:

        # ----------------------------------------------
        # Check file
        # ----------------------------------------------

        if "image" not in request.files:

            return jsonify({
                "error": "No image uploaded."
            }), 400


        image = request.files["image"]


        if not image.filename:

            return jsonify({
                "error": "Please select an image."
            }), 400


        # ----------------------------------------------
        # Allowed file types
        # ----------------------------------------------

        allowed_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp"
        }

        filename = image.filename.lower()

        if not any(
            filename.endswith(ext)
            for ext in allowed_extensions
        ):

            return jsonify({
                "error":
                    "Please upload a PNG, JPG, JPEG or WEBP image."
            }), 400


        # ----------------------------------------------
        # Read image
        # ----------------------------------------------

        image_bytes = image.read()


        # ----------------------------------------------
        # Size protection
        # ----------------------------------------------

        max_size = 8 * 1024 * 1024

        if len(image_bytes) > max_size:

            return jsonify({
                "error":
                    "Image is too large. Maximum size is 8 MB."
            }), 400


        if len(image_bytes) == 0:

            return jsonify({
                "error":
                    "The uploaded image is empty."
            }), 400


        # ----------------------------------------------
        # AI Vision Analysis
        # ----------------------------------------------

        try:

            result = analyze_screenshot(
                image_bytes,
                image.filename
            )

            result["analysis_source"] = "vision"

            return jsonify(result), 200


        except Exception as ai_error:

            print(
                "Screenshot analysis failed:",
                str(ai_error)
            )

            return jsonify({
                "error":
                    "ScamLens could not analyze this screenshot. "
                    "Please try another image."
            }), 500


    except Exception as error:

        print(
            "Image endpoint error:",
            str(error)
        )

        return jsonify({
            "error":
                "Something went wrong while processing the image."
        }), 500

    
# ==========================================================
# ERROR HANDLERS
# ==========================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        "error": "Method not allowed."
    }), 405


# ==========================================================
# RUN SERVER
# ==========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )