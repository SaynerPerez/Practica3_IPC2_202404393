import requests
from django.shortcuts import render, redirect
from django.http import Http404
from django.conf import settings
from django.contrib import messages

# URL base de la API Flask
API_URL = settings.FLASK_API_URL

def hacer_peticion_api(endpoint, metodo='GET', datos=None):
    url = f"{API_URL}/{endpoint}"
    try:
        if metodo == 'GET':
            respuesta = requests.get(url)
        elif metodo == 'POST':
            respuesta = requests.post(url, json=datos)
        elif metodo == 'PUT':
            respuesta = requests.put(url, json=datos)
        elif metodo == 'DELETE':
            respuesta = requests.delete(url)
        
        if respuesta.status_code in [200, 201]:
            return respuesta.json()
        else:
            return {'error': f'Error {respuesta.status_code}: {respuesta.text}'}
    
    except requests.exceptions.ConnectionError:
        return {'error': 'No se puede conectar con la API Flask. Asegúrate de que esté ejecutándose.'}
    except Exception as e:
        return {'error': f'Error inesperado: {str(e)}'}

# Listar todos los productos
def lista_productos(request):
    resultado = hacer_peticion_api('productos')
    
    if 'error' in resultado:
        messages.error(request, resultado['error'])
        productos = []
    else:
        productos = resultado
    
    context = {
        'productos': productos,
        'titulo': 'Inventario de Productos'
    }
    return render(request, 'productos/lista_productos.html', context)

# Detalle de un producto
def detalle_producto(request, producto_id):
    resultado = hacer_peticion_api(f'productos/{producto_id}')
    
    if 'error' in resultado:
        messages.error(request, resultado['error'])
        raise Http404("Producto no encontrado")
    
    context = {
        'producto': resultado,
        'titulo': f'Detalle: {resultado["nombre"]}'
    }
    return render(request, 'productos/detalle_producto.html', context)

# Crear nuevo producto
def crear_producto(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        datos_producto = {
            'nombre': request.POST.get('nombre'),
            'categoria': request.POST.get('categoria'),
            'descripcion': request.POST.get('descripcion'),
            'precio': request.POST.get('precio'),
            'cantidad_stock': request.POST.get('cantidad_stock'),
            'fecha_vencimiento': request.POST.get('fecha_vencimiento') or None
        }
        
        # Validaciones básicas
        if not all([datos_producto['nombre'], datos_producto['categoria'], datos_producto['precio']]):
            messages.error(request, 'Nombre, categoría y precio son campos obligatorios.')
            return render(request, 'productos/formulario_producto.html', {
                'titulo': 'Crear Nuevo Producto',
                'producto': datos_producto
            })
        
        # Enviar a la API
        resultado = hacer_peticion_api('productos', 'POST', datos_producto)
        
        if 'error' in resultado:
            messages.error(request, resultado['error'])
            return render(request, 'productos/formulario_producto.html', {
                'titulo': 'Crear Nuevo Producto',
                'producto': datos_producto
            })
        else:
            messages.success(request, f'Producto "{resultado["nombre"]}" creado exitosamente!')
            return redirect('lista_productos')
    
    #  Mostrar formulario vacío
    return render(request, 'productos/formulario_producto.html', {
        'titulo': 'Crear Nuevo Producto',
        'producto': None
    })

# Actualizar producto existente
def actualizar_producto(request, producto_id):
    if request.method == 'GET':
        # Obtener producto actual
        resultado = hacer_peticion_api(f'productos/{producto_id}')
        
        if 'error' in resultado:
            messages.error(request, resultado['error'])
            raise Http404("Producto no encontrado")
        
        return render(request, 'productos/formulario_producto.html', {
            'titulo': f'Editar: {resultado["nombre"]}',
            'producto': resultado,
            'es_edicion': True
        })
    
    elif request.method == 'POST':
        # Obtener datos del formulario
        datos_actualizados = {
            'nombre': request.POST.get('nombre'),
            'categoria': request.POST.get('categoria'),
            'descripcion': request.POST.get('descripcion'),
            'precio': request.POST.get('precio'),
            'cantidad_stock': request.POST.get('cantidad_stock'),
            'fecha_vencimiento': request.POST.get('fecha_vencimiento') or None
        }
        
        # Enviar a la API
        resultado = hacer_peticion_api(f'productos/{producto_id}', 'PUT', datos_actualizados)
        
        if 'error' in resultado:
            messages.error(request, resultado['error'])
            return render(request, 'productos/formulario_producto.html', {
                'titulo': f'Editar: {datos_actualizados["nombre"]}',
                'producto': datos_actualizados,
                'es_edicion': True
            })
        else:
            messages.success(request, f'Producto "{resultado["nombre"]}" actualizado exitosamente!')
            return redirect('detalle_producto', producto_id=producto_id)

# Eliminar producto
def eliminar_producto(request, producto_id):
    if request.method == 'GET':
        # Obtener producto para confirmación
        resultado = hacer_peticion_api(f'productos/{producto_id}')
        
        if 'error' in resultado:
            messages.error(request, resultado['error'])
            raise Http404("Producto no encontrado")
        
        return render(request, 'productos/confirmar_eliminar.html', {
            'producto': resultado,
            'titulo': f'Eliminar: {resultado["nombre"]}'
        })
    
    elif request.method == 'POST':
        # Confirmar eliminación
        resultado = hacer_peticion_api(f'productos/{producto_id}', 'DELETE')
        
        if 'error' in resultado:
            messages.error(request, resultado['error'])
            return redirect('detalle_producto', producto_id=producto_id)
        else:
            messages.success(request, f'Producto eliminado exitosamente!')
            return redirect('lista_productos')