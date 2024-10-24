from flask import Flask, request, jsonify, render_template, send_from_directory
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS  # Importa la librería Flask-CORS

app = Flask(__name__, static_folder='static', template_folder='templates')

# Habilitar CORS para toda la aplicación
CORS(app)

# Función para crear la conexión a la base de datos MySQL
def create_connection():
    try:
        connection = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=server-sql-fiee.database.windows.net;'
    'DATABASE=iot_db;'
    'UID=admin_iot;'
    'PWD=Focm24681012'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

@app.route('/plugins/<path:filename>')
def serve_plugins(filename):
    return send_from_directory('/home/admin_prueba/Proyecto IoT - FIEE/Proyecto IoT -VM/plugins', filename)

# Rutas para renderizar
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/PrimerPiso')
def primer_piso():
    return render_template('PrimerPiso.html')

@app.route('/SegundoPiso')
def segundo_piso():
    return render_template('SegundoPiso.html')

@app.route('/TercerPiso')
def tercer_piso():
    return render_template('TercerPiso.html')

@app.route('/inicio')
def inicio():
    return render_template('index2.html')

@app.route('/Escenas')
def escenas():
    return render_template('Escenas.html')
    
# Ruta para insertar o actualizar datos del ESP32 (sensores)
@app.route('/api/insertdata', methods=['POST'])
def insert_data():
    try:
        mydb = create_connection()
        if mydb is None:
            return "Error: Conexión a la base de datos no disponible", 500
        
        esp_id = request.form['esp_id']
        pir_status = request.form.get('pir_status')
        ldr_status = request.form.get('ldr_status')
        nivel_agua = request.form.get('nivel_agua')
        metal_detectado = request.form.get('metal_detectado')
        temperatura = request.form.get('temperatura')
        
        cursor = mydb.cursor()

        # Verificar si ya existe un registro con ese esp_id
        query_check = "SELECT * FROM sensor_data WHERE esp_id = %s"
        cursor.execute(query_check, (esp_id,))
        result = cursor.fetchone()

        # Si existe un registro, actualizamos los valores
        if result:
            query_update = """
            UPDATE sensor_data 
            SET pir_status = %s, ldr_status = %s, nivel_agua = %s, metal_detectado = %s, temperatura = %s
            WHERE esp_id = %s
            """
            cursor.execute(query_update, (pir_status, ldr_status, nivel_agua, metal_detectado, temperatura, esp_id))
        else:
            # Si no existe, insertamos un nuevo registro
            query_insert = """
            INSERT INTO sensor_data (esp_id, pir_status, ldr_status, nivel_agua, metal_detectado, temperatura)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_insert, (esp_id, pir_status, ldr_status, nivel_agua, metal_detectado, temperatura))

        mydb.commit()
        cursor.close()
        mydb.close()
        return "Datos actualizados", 200
    except Exception as e:
        return f"Error: {e}", 500

# Ruta para obtener el estado más reciente de los sensores
@app.route('/api/getlateststatus', methods=['GET'])
def get_latest_status():
    try:
        esp_id = request.args.get('esp_id')
        mydb = create_connection()
        if mydb is None:
            return "Error: Conexión a la base de datos no disponible", 500
        
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("""
        SELECT pir_status, ldr_status, nivel_agua, metal_detectado, temperatura 
        FROM sensor_data 
        WHERE esp_id = %s ORDER BY id DESC LIMIT 1
        """, (esp_id,))
        result = cursor.fetchone()
        cursor.close()
        mydb.close()

        if result:
            return jsonify(result)
        else:
            return jsonify(pir_status="No hay datos", ldr_status="No hay datos", nivel_agua="No hay datos", metal_detectado="No hay datos", temperatura="No hay datos"), 200
    except Exception as e:
        return f"Error: {e}", 500

# Ruta para actualizar el estado del LED
@app.route('/api/updateled', methods=['POST'])
def update_led():
    try:
        mydb = create_connection()
        if mydb is None:
            return "Error: Conexión a la base de datos no disponible", 500
        
        led_status = request.form.get('led_status')
        led1_status = request.form.get('led1_status')
        led2_status = request.form.get('led2_status')
        esp_id = request.form.get('esp_id')

        cursor = mydb.cursor()

        # Actualizamos los estados de los LEDs
        if led_status:
            query_update_led = "UPDATE sensor_data SET led_status = %s WHERE esp_id = %s"
            cursor.execute(query_update_led, (led_status, esp_id))
        if led1_status:
            query_update_led1 = "UPDATE sensor_data SET led1_status = %s WHERE esp_id = %s"
            cursor.execute(query_update_led1, (led1_status, esp_id))
        if led2_status:
            query_update_led2 = "UPDATE sensor_data SET led2_status = %s WHERE esp_id = %s"
            cursor.execute(query_update_led2, (led2_status, esp_id))

        mydb.commit()
        cursor.close()
        mydb.close()
        return "LED actualizado", 200
    except Exception as e:
        return f"Error: {e}", 500

# Ruta para obtener el estado actual de los LEDs
@app.route('/api/getledstatus', methods=['GET'])
def get_led_status():
    try:
        esp_id = request.args.get('esp_id')
        mydb = create_connection()
        if mydb is None:
            return "Error: Conexión a la base de datos no disponible", 500
        
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("""
        SELECT led_status, led1_status, led2_status 
        FROM sensor_data 
        WHERE esp_id = %s ORDER BY id DESC LIMIT 1
        """, (esp_id,))
        result = cursor.fetchone()
        cursor.close()
        mydb.close()

        if result:
            return jsonify(result)
        else:
            return jsonify(led_status=0, led1_status=0, led2_status=0), 200
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8000))  # Toma el puerto de la variable de entorno PORT, o 8000 como predeterminado.
    app.run(host='0.0.0.0', port=port)
