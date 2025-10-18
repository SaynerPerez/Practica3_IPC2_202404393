from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde Django

# Archivo donde se guardarán los productos
INVENTARIO_FILE = 'inventario.json'

# Cargar productos desde el archivo JSON
def cargar_productos():
    if not os.path.exists(INVENTARIO_FILE):
        return []
    
    try:
        with open(INVENTARIO_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# Guardar productos en el archivo JSON
def guardar_productos(productos):
    with open(INVENTARIO_FILE, 'w', encoding='utf-8') as file:
        json.dump(productos, file, indent=4, ensure_ascii=False)

# Generar ID único para nuevos productos
def generar_id():
    productos = cargar_productos()
    if not productos:
        return 1
    return max(producto['id'] for producto in productos) + 1

# Validar datos del producto
def validar_producto(data, es_actualizacion=False):
    campos_requeridos = ['nombre', 'categoria', 'descripcion', 'precio', 'cantidad_stock']
    
    if not es_actualizacion:
        for campo in campos_requeridos:
            if campo not in data:
                return False, f"Campo requerido faltante: {campo}"
    
    # Validar tipos de datos
    if 'precio' in data and data['precio']:
        try:
            float(data['precio'])
        except ValueError:
            return False, "Precio debe ser un número válido"
    
    if 'cantidad_stock' in data and data['cantidad_stock']:
        try:
            int(data['cantidad_stock'])
        except ValueError:
            return False, "Cantidad en stock debe ser un número entero"
    
    return True, "OK"

# POST /productos - Crear nuevo producto
@app.route('/productos', methods=['POST'])
def crear_producto():
    try:
        data = request.get_json()
        
        # Validar datos
        es_valido, mensaje = validar_producto(data)
        if not es_valido:
            return jsonify({'error': mensaje}), 400
        
        # Crear nuevo producto
        nuevo_producto = {
            'id': generar_id(),
            'nombre': data['nombre'],
            'categoria': data['categoria'],
            'descripcion': data['descripcion'],
            'precio': float(data['precio']),
            'cantidad_stock': int(data['cantidad_stock']),
            'fecha_vencimiento': data.get('fecha_vencimiento', None)
        }
        
        # Guardar en el archivo
        productos = cargar_productos()
        productos.append(nuevo_producto)
        guardar_productos(productos)
        
        return jsonify(nuevo_producto), 201
    
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

#  GET /productos - Listar todos los productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    try:
        productos = cargar_productos()
        return jsonify(productos), 200
    except Exception as e:
        return jsonify({'error': f'Error al cargar productos: {str(e)}'}), 500

#  GET /productos/<id> - Obtener producto por ID
@app.route('/productos/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    try:
        productos = cargar_productos()
        producto = next((p for p in productos if p['id'] == producto_id), None)
        
        if producto:
            return jsonify(producto), 200
        else:
            return jsonify({'error': 'Producto no encontrado'}), 404
    
    except Exception as e:
        return jsonify({'error': f'Error al buscar producto: {str(e)}'}), 500

# PUT /productos/<id> - Actualizar producto
@app.route('/productos/<int:producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    try:
        data = request.get_json()
        
        # Validar datos (para actualización, algunos campos pueden ser opcionales)
        es_valido, mensaje = validar_producto(data, es_actualizacion=True)
        if not es_valido:
            return jsonify({'error': mensaje}), 400
        
        productos = cargar_productos()
        producto_index = next((i for i, p in enumerate(productos) if p['id'] == producto_id), None)
        
        if producto_index is None:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Actualizar solo los campos proporcionados
        producto_actual = productos[producto_index]
        
        if 'nombre' in data:
            producto_actual['nombre'] = data['nombre']
        if 'categoria' in data:
            producto_actual['categoria'] = data['categoria']
        if 'descripcion' in data:
            producto_actual['descripcion'] = data['descripcion']
        if 'precio' in data:
            producto_actual['precio'] = float(data['precio'])
        if 'cantidad_stock' in data:
            producto_actual['cantidad_stock'] = int(data['cantidad_stock'])
        if 'fecha_vencimiento' in data:
            producto_actual['fecha_vencimiento'] = data['fecha_vencimiento']
        
        guardar_productos(productos)
        return jsonify(producto_actual), 200
    
    except Exception as e:
        return jsonify({'error': f'Error al actualizar producto: {str(e)}'}), 500

# ENDPOINT 5: DELETE /productos/<id> - Eliminar producto
@app.route('/productos/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    try:
        productos = cargar_productos()
        producto_index = next((i for i, p in enumerate(productos) if p['id'] == producto_id), None)
        
        if producto_index is None:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Eliminar producto
        producto_eliminado = productos.pop(producto_index)
        guardar_productos(productos)
        
        return jsonify({'mensaje': 'Producto eliminado correctamente', 'producto': producto_eliminado}), 200
    
    except Exception as e:
        return jsonify({'error': f'Error al eliminar producto: {str(e)}'}), 500

# Ruta de prueba
@app.route('/')
def index():
    return jsonify({'mensaje': 'API Flask para Gestión de Inventario', 'estado': 'Activo'})

if __name__ == '__main__':
    if not os.path.exists(INVENTARIO_FILE):
        guardar_productos([])
    
    print("Iniciando servidor Flask en http://localhost:5000")
    app.run(debug=True, port=5000)