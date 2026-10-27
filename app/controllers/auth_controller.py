from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from app.models.usuario import Usuario


def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.activo and usuario.check_password(password):
            login_user(usuario)
            siguiente = request.args.get("next")
            # Solo se permiten redirecciones internas
            if siguiente and siguiente.startswith("/") and not siguiente.startswith("//"):
                return redirect(siguiente)
            return redirect(url_for("dashboard.index"))

        flash("Correo o contraseña incorrectos.", "error")

    return render_template("auth/login.html")


def logout():
    logout_user()
    flash("Sesión cerrada.", "ok")
    return redirect(url_for("auth.login"))