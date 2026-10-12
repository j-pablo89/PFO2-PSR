import os
import requests
import tempfile
import webbrowser


URL = "http://127.0.0.1:5000"
sesion = requests.Session() 


def pedir_credenciales():
    usuario = input("Usuario: ").strip()
    contraseña = input("Contraseña: ").strip()
    return {"usuario": usuario, "contraseña": contraseña}


def registrar():
    r = sesion.post(f"{URL}/registro", json=pedir_credenciales())
    print(r.status_code, r.json())


def iniciar_sesion():
    r = sesion.post(f"{URL}/login", json=pedir_credenciales())
    print(r.status_code, r.json())


def ver_tareas():
    r = sesion.get(f"{URL}/tareas")
    print(r.status_code)
    if r.status_code != 200:
        print(r.text)
        return
    ruta = os.path.join(tempfile.gettempdir(), "tareas.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(r.text)
    webbrowser.open("file://" + ruta)
    print("Se abrió la página de bienvenida en el navegador.")


def menu():
    opciones = {"1": registrar, "2": iniciar_sesion, "3": ver_tareas}
    while True:
        print("\n1) Registrarse  2) Iniciar sesión  3) Ver tareas  4) Salir")
        op = input("Opción: ").strip()
        if op == "4":
            break
        accion = opciones.get(op)
        if accion:
            try:
                accion()
            except requests.exceptions.ConnectionError:
                print("No se pudo conectar: ¿está corriendo servidor.py?")
        else:
            print("Opción inválida")


if __name__ == "__main__":
    menu()
