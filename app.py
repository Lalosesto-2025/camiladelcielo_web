from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'clave_secreta_camila_pro_2026'

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="camila_db"
        )
        return conn
    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None

# --- RUTAS PÚBLICAS ---

@app.route('/')
def index():
    perfil = None
    proyectos = []
    total_proyectos = 0
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Obtener perfil
        cursor.execute("SELECT * FROM perfil LIMIT 1;")
        perfil = cursor.fetchone()
        
        # 2. Obtener los últimos 3 proyectos para mostrar en la portada
        cursor.execute("SELECT * FROM proyectos ORDER BY id DESC LIMIT 3;")
        proyectos = cursor.fetchall()
        
        # 3. Contar AUTOMÁTICAMENTE el total real de proyectos en la base de datos
        cursor.execute("SELECT COUNT(*) AS total FROM proyectos;")
        conteo = cursor.fetchone()
        if conteo:
            total_proyectos = conteo['total']
            
        cursor.close()
        conn.close()
        
    return render_template('index.html', 
                           perfil=perfil, 
                           proyectos=proyectos, 
                           total_proyectos=total_proyectos)
@app.route('/proyectos')
def proyectos():
    categoria = request.args.get('categoria', 'Todas')
    proyectos_lista = []
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        if categoria != 'Todas':
            cursor.execute("SELECT * FROM proyectos WHERE categoria = %s ORDER BY id DESC;", (categoria,))
        else:
            cursor.execute("SELECT * FROM proyectos ORDER BY id DESC;")
        proyectos_lista = cursor.fetchall()
        cursor.close()
        conn.close()
        
    return render_template('proyectos.html', proyectos=proyectos_lista, categoria_actual=categoria)

@app.route('/like_proyecto/<int:proyecto_id>', methods=['POST'])
def like_proyecto(proyecto_id):
    conn = get_db_connection()
    nuevos_likes = 0
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("UPDATE proyectos SET likes = likes + 1 WHERE id = %s;", (proyecto_id,))
        conn.commit()
        
        cursor.execute("SELECT likes FROM proyectos WHERE id = %s;", (proyecto_id,))
        res = cursor.fetchone()
        if res:
            nuevos_likes = res['likes']
            
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'likes': nuevos_likes})
    return jsonify({'success': False}), 500

@app.route('/interactivo')
def interactivo():
    puntajes = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM juego_puntajes ORDER BY puntaje DESC, fecha ASC LIMIT 5;")
        puntajes = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('interactivo.html', puntajes=puntajes)

@app.route('/guardar_puntaje', methods=['POST'])
def guardar_puntaje():
    datos = request.get_json()
    jugador = datos.get('jugador', 'Invitado')
    puntaje = datos.get('puntaje', 0)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO juego_puntajes (jugador, puntaje) VALUES (%s, %s);", (jugador, puntaje))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False}), 500

@app.route('/libro_visitas', methods=['GET', 'POST'])
def libro_visitas():
    if request.method == 'POST':
        nombre = request.form['nombre']
        mensaje = request.form['mensaje']
        
        if nombre and mensaje:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO comentarios (nombre_autor, mensaje, aprobado) VALUES (%s, %s, 1);",
                    (nombre, mensaje)
                )
                conn.commit()
                cursor.close()
                conn.close()
                flash('¡Gracias por dejar tu mensaje en el Libro de Visitas! ✨', 'success')
            return redirect(url_for('libro_visitas'))

    comentarios = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM comentarios WHERE aprobado = 1 ORDER BY id DESC;")
        comentarios = cursor.fetchall()
        cursor.close()
        conn.close()
        
    return render_template('libro_visitas.html', comentarios=comentarios)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        mensaje = request.form['mensaje']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO contactos (nombre_remitente, correo, mensaje) VALUES (%s, %s, %s);",
                (nombre, correo, mensaje)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('¡Muchas gracias por tu mensaje privado! Me pondré en contacto contigo pronto. 💌', 'success')
        else:
            flash('Error de conexión a la base de datos.', 'error')
            
        return redirect(url_for('contacto'))
        
    return render_template('contacto.html')

# --- MÓDULO DE ADMINISTRACIÓN PROFESIONAL ---

@app.route('/registro_admin', methods=['GET', 'POST'])
def registro_admin():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM usuarios;")
        total = cursor.fetchone()['total']
        
        # Si ya existe un administrador creado, bloquea el registro público
        if total > 0 and not session.get('admin_logged_in'):
            cursor.close()
            conn.close()
            flash('El usuario administrador ya existe. Inicia sesión.', 'error')
            return redirect(url_for('login'))

        if request.method == 'POST':
            usuario = request.form.get('usuario').strip()
            password = request.form.get('password')
            
            if usuario and password:
                pwd_hash = generate_password_hash(password)
                cursor.execute("INSERT INTO usuarios (usuario, password_hash) VALUES (%s, %s);", (usuario, pwd_hash))
                conn.commit()
                cursor.close()
                conn.close()
                flash('¡Cuenta de Administradora creada con éxito! Ahora inicia sesión.', 'success')
                return redirect(url_for('login'))

        cursor.close()
        conn.close()

    return render_template('registro_admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE usuario = %s;", (usuario,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user['password_hash'], password):
                session['admin_logged_in'] = True
                session['admin_user'] = user['usuario']
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Usuario o contraseña incorrectos. 🔒', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
        
    mensajes = []
    total_mensajes = 0
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM contactos ORDER BY id DESC;")
        mensajes = cursor.fetchall()
        total_mensajes = len(mensajes)
        cursor.close()
        conn.close()
        
    return render_template('admin_dashboard.html', mensajes=mensajes, total_mensajes=total_mensajes)

if __name__ == '__main__':
    app.run(debug=True, port=5050)