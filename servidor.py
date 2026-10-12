import sqlite3

from flask import Flask, jsonify, redirect, request, session
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "mi-clave-secreta"
DB = "tareas.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )


PAGINA_INICIO = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gestión de Tareas</title>
<style>
  body { font-family: system-ui, sans-serif; background: #f2f4f8; display: flex;
         justify-content: center; padding-top: 60px; }
  .caja { background: #fff; padding: 28px; border-radius: 10px; width: 320px;
          box-shadow: 0 2px 10px rgba(0,0,0,.1); }
  h1 { font-size: 1.3rem; margin-top: 0; }
  input, button { width: 100%; padding: 10px; margin-top: 10px; box-sizing: border-box; }
  button { cursor: pointer; border: 0; border-radius: 6px; background: #2563eb; color: #fff; }
  button.sec { background: #64748b; }
  #msg { margin-top: 14px; font-size: .9rem; min-height: 1.2em; }
  .ok { color: #15803d; } .error { color: #b91c1c; }
</style>
</head>
<body>
<div class="caja">
  <h1>Sistema de Gestión de Tareas</h1>
  <input id="usuario" placeholder="Usuario" autocomplete="username">
  <input id="contraseña" type="password" placeholder="Contraseña" autocomplete="current-password">
  <button onclick="enviar('/login')">Iniciar sesión</button>
  <button class="sec" onclick="enviar('/registro')">Registrarse</button>
  <div id="msg"></div>
</div>
<script>
async function enviar(ruta) {
  const msg = document.getElementById("msg");
  const r = await fetch(ruta, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      usuario: document.getElementById("usuario").value,
      "contraseña": document.getElementById("contraseña").value
    })
  });
  const datos = await r.json();
  msg.className = r.ok ? "ok" : "error";
  msg.textContent = datos.mensaje || datos.error;
  if (r.ok && ruta === "/login") window.location.href = "/tareas";
}
</script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def inicio():
    return PAGINA_INICIO


@app.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json(silent=True) or {}
    usuario = (datos.get("usuario") or "").strip()
    contraseña = datos.get("contraseña") or ""

    if not usuario or not contraseña:
        return jsonify({"error": "Faltan 'usuario' o 'contraseña'"}), 400

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
                (usuario, generate_password_hash(contraseña)),
            )
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 409

    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True) or {}
    usuario = (datos.get("usuario") or "").strip()
    contraseña = datos.get("contraseña") or ""

    with get_db() as conn:
        fila = conn.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()

    if fila is None or not check_password_hash(fila["password_hash"], contraseña):
        return jsonify({"error": "Credenciales inválidas"}), 401

    session["usuario"] = fila["usuario"]
    return jsonify({"mensaje": f"Bienvenido, {fila['usuario']}"}), 200


@app.route("/tareas", methods=["GET"])
def tareas():
    usuario = session.get("usuario")
    if not usuario:
        if request.accept_mimetypes.best == "text/html":
            return redirect("/")
        return jsonify({"error": "Debes iniciar sesión en /login"}), 401

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="utf-8"><title>Tareas</title></head>
    <body>
        <h1>¡Bienvenido, {escape(usuario)}!</h1>
        <p>Este es tu sistema de gestión de tareas.</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
