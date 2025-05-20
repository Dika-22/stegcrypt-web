from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from stegano import lsb
from PIL import Image
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Caesar Cipher
def caesar_encrypt(text, key):
    return ''.join(chr((ord(c) - 97 + key) % 26 + 97) if c.islower() else c for c in text)

def caesar_decrypt(text, key):
    return caesar_encrypt(text, -key)

# Vigenère Cipher
def vigenere_encrypt(text, key):
    result = ''
    key = key.lower()
    k_len = len(key)
    j = 0
    for c in text:
        if c.isalpha():
            shift = ord(key[j % k_len]) - ord('a')
            base = ord('a') if c.islower() else ord('A')
            result += chr((ord(c) - base + shift) % 26 + base)
            j += 1
        else:
            result += c
    return result

def vigenere_decrypt(text, key):
    result = ''
    key = key.lower()
    k_len = len(key)
    j = 0
    for c in text:
        if c.isalpha():
            shift = ord(key[j % k_len]) - ord('a')
            base = ord('a') if c.islower() else ord('A')
            result += chr((ord(c) - base - shift) % 26 + base)
            j += 1
        else:
            result += c
    return result

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/encrypt", methods=["POST"])
def encrypt():
    image = request.files["image"]
    message = request.form["message"]
    key = request.form["key"]
    method = request.form["method"]

    # Simpan gambar asli
    filename = secure_filename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    # Enkripsi pesan
    if method == "caesar":
        encrypted = caesar_encrypt(message.lower(), int(key))
    elif method == "vigenere":
        encrypted = vigenere_encrypt(message, key)
    else:
        return render_template("index.html", message="Metode tidak valid.")

    # Simpan hasil ke gambar baru
    unique_id = str(uuid.uuid4())[:8]
    output_filename = f"stego_{unique_id}.png"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    stego_img = lsb.hide(image_path, encrypted)
    stego_img.save(output_path)

    file_url = f"/uploads/{output_filename}"
    return render_template("index.html", file_url=file_url)

@app.route("/decrypt", methods=["POST"])
def decrypt():
    image = request.files["image"]
    key = request.form["key"]
    method = request.form["method"]

    filename = secure_filename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    hidden = lsb.reveal(image_path)
    if not hidden:
        return render_template("index.html", message="❌ Tidak ada pesan ditemukan.")

    # Dekripsi pesan
    if method == "caesar":
        decrypted = caesar_decrypt(hidden.lower(), int(key))
    elif method == "vigenere":
        decrypted = vigenere_decrypt(hidden, key)
    else:
        return render_template("index.html", message="Metode tidak valid.")

    return render_template("index.html", message=f"✅ Pesan: {decrypted}")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
    
if __name__ == "__main__":
    app.run(debug=True)
