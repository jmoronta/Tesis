import aiohttp
from aiohttp import web
import asyncio
import funciones as fc
import getGP as gp
import argparse
import os
import multiprocessing
from PIL import Image
import ssl
import socket
import bottle
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
from fast_plate_ocr import ONNXPlateRecognizer
import conexion as conexion
from datetime import datetime

async def home(request):
    content= """
        <html>
			<head>
				<title>Directorio WEB</title>
			</head>
			<body>
			<h2>Upload Image</h2> <a href="upload.html" target="_blank" rel="noopener noreferrer">Upload Filter</a>
			<h2>Apply Resize</h2> <a href="scale.html" target="_blank" rel="noopener noreferrer">Apply Filter</a>
			<h2>Show converted images</h2> <a href="show.html" target="_blank" rel="noopener noreferrer">Show</a>
            </body>
		</html>
    """
    return web.Response(text=content, content_type='text/html')

async def upload(request):
    content= """
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Formulario de Subida de Imágenes</title>
            </head>
            <body>

                <h2>Subir Imagen</h2>

                <form action="/upload" method="post" enctype="multipart/form-data">
                    <label for="image">Selecciona una imagen:</label>
                    <input type="file" id="image" name="image" accept="image/*" required>
                    
                    <br><br>

                    <input type="submit" value="Subir Imagen">
                </form>

            </body>
        </html>
    """
    return web.Response(text=content, content_type='text/html')

async def show(request):
    grayscale_images_folder = './Grayscale'
    image_list = list_images(grayscale_images_folder)
    resized_images_folder='./resized'
    image_list2 = list_images(resized_images_folder)
    content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Imágenes Convertidas</title>
        </head>
        <body>
            <h2>Imágenes Convertidas</h2>
    """
    for filename in image_list:
        content += f'<div>'
        content += f'<a href="/show_image?filename={filename}" target="_blank">'
        content += f'<img src="{grayscale_images_folder}/{filename}" alt="{filename}">'
        content += f'</a>'
        content += f'</div>'
    for filename2 in image_list2:
        content += f'<div>'
        content += f'<a href="/show_image?filename={filename2}" target="_blank">'
        content += f'<img src="{resized_images_folder}/{filename2}" alt="{filename2}">'
        content += f'</a>'
        content += f'</div>'
        
    content += """
        </body>
        </html>
    """

    return web.Response(text=content, content_type='text/html', headers={'Connection': 'close'})


async def show_image(request):
    # Obtener el nombre del archivo de la consulta
    filename = request.query.get('filename', None)

    if not filename:
        return web.Response(text="Error: Se requiere el parámetro 'filename' en la consulta.", status=400)

    # Construir la ruta completa al archivo de imagen
    image_grey_path = os.path.join('./Grayscale', filename)
    image_resize_path = os.path.join('./resized', filename)
    # Verificar si el archivo existe
    #if not os.path.exists(image_grey_path) :
    #    return web.Response(text=f"Error: La imagen '{filename}' no existe.", status=404)
    
    if os.path.exists(image_grey_path):
        # Abrir y leer la imagen
        with open(image_grey_path, 'rb') as image_file:
            image_data = image_file.read()

        # Crear la respuesta con el contenido de la imagen
        return web.Response(body=image_data, content_type='image/jpeg')
    
    elif os.path.exists(image_resize_path):
        # Abrir y leer la imagen
        with open(image_resize_path, 'rb') as image_file:
            image_data = image_file.read()

        # Crear la respuesta con el contenido de la imagen
        return web.Response(body=image_data, content_type='image/jpeg')
    
    # Si ninguna condición es verdadera, devolver un error 404
    return web.Response(text=f"Error: La imagen '{filename}' no existe.", status=404)

async def handle_upload(request):
    reader = await request.multipart()
    field = await reader.next()

    # Nombre del archivo
    filename = field.filename

    # Ruta donde se guardará la imagen 
    save_path = os.path.join('./images', filename)

    # Guardar la imagen en el servidor
    with open(save_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)
    
    # Agregar la imagen a la cola para procesamiento en escala de grises
    image_queue.put(save_path)

    # Bloquear hasta que la conversión de la imagen esté completa
    result_path = image_queue.get()

    return web.Response(text=f'Imagen "{filename}" cargada con éxito.', content_type='text/plain')

def grayscale_worker(queue):
    while True:
        image_path = queue.get()
        if image_path is None:
            break

        # Procesar la imagen 
        m = ONNXPlateRecognizer('argentinian-plates-cnn-model')
        nropatente=m.run(image_path)
        print(nropatente,type(nropatente))
        
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        link=gp.convert_to_gplink(image_path)
        print("La ubicacion es:",link)
        
        conexion.insert_en_tabla(image_path,nropatente,link)
        
        grayscale_image_path = os.path.join('./Grayscale', 'grayscale_' + os.path.basename(image_path))
        #grayscale_image_path = os.path.join('./Grayscale', 'grayscale_' + os.path.basename(image_path))
        convert_to_grayscale(image_path, grayscale_image_path)
        # Agregar la imagen convertida a la cola de resultados
        image_queue.put(grayscale_image_path)
        
    

def convert_to_grayscale(input_path, output_path):
    try:
        image = Image.open(input_path).convert('L')
        image.save(output_path)
        #print(f'Imagen convertida a escala de grises: {output_path}')
    except Exception as e:
        print(f'Error al procesar la imagen: {e}')

def list_images(folder_path, allowed_formats=None):
    
    image_list = []

    # Si no se especifican formatos permitidos, se aceptan todos
    if allowed_formats is None:
        allowed_formats = [".jpg", ".jpeg", ".png", ".gif", ".bmp","dng"]

    # Obtener la lista de archivos en la carpeta especificada
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Verificar si el archivo es una imagen válida
        try:
            with Image.open(file_path):
                # Verificar si la extensión del archivo está en los formatos permitidos
                if any(filename.lower().endswith(format) for format in allowed_formats):
                    image_list.append(filename)
        except (IOError, OSError):
            pass  # El archivo no es una imagen válida

    return image_list

# Uso específico para la carpeta Grayscale
#grayscale_images_folder = './Grayscale'
#grayscale_image_list = list_images(grayscale_images_folder)

async def handle_resize(request):
    content= """
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Subida y Modificacion de Imágenes</title>
            </head>
            <body>

                <h2>Subir Imagen</h2>

                <form action="/resize" method="post" enctype="multipart/form-data">
                    <label for="image">Selecciona una imagen:</label>
                    <input type="file" id="image" name="image" accept="image/*" required>
                    <p>
                        Escala:
                        <input type="number" id="escala" name="escala" min="0">
                    </p>
                    <br><br>

                    <input type="submit" value="Subir Imagen">
                </form>

            </body>
        </html>
    """
    return web.Response(text=content, content_type='text/html')

async def resize(request):

    try:
        dato = await request.post()
        file_data = dato['image']
        scale = dato['escala']
        
        if file_data.file:

			# Lee los datos del archivo
            file_content = file_data.file.read()
            
			# Ruta donde se guardará la imagen 
            #save_path = os.path.join('./resize', file_data.filename)

            # Guardar la imagen en el servidor
            #with open(save_path, 'wb') as f:
            #    f.write(file_content)
            
            form = aiohttp.FormData()
            form.add_field('image', file_content, filename=file_data.filename)
            form.add_field('scale', scale)
            
            
            async with aiohttp.ClientSession() as session:
                async with session.post('http://localhost:8080/resize_from', data=form) as response:
                    response_text = await response.text()
                    if response.status == 200:
                            print("Se ha aplicado los cambios exitosamente!")
                            reduced_image_data = await response.read()
                            return aiohttp.web.Response(body=reduced_image_data, content_type='image/jpeg')
                    else:
                        print("Ha ocurrido un error ")
                        return aiohttp.web.Response(text="La solicitud al segundo servidor fallo")
    except Exception as e:
        return aiohttp.web.Response(text=f"Error al comunicarse con el 2do servidor : {e}")

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Arrays')
    parser.add_argument('-p', '--port', required=True,action="store", dest="puerto",type=int, help="Puerto")
    
    args = parser.parse_args()
    puerto=args.puerto
    
    image_queue = multiprocessing.Queue()

    # Crear el proceso hijo para el servicio de escala de grises
    grayscale_process = multiprocessing.Process(target=grayscale_worker, args=(image_queue,))
    grayscale_process.start()

    app = web.Application()
    app.router.add_get('/', home)
    app.router.add_get('/upload.html', upload)
    app.router.add_post('/upload', handle_upload)
    app.router.add_get('/show.html', show)
    app.router.add_get('/scale.html', handle_resize)
    app.router.add_post('/resize', resize)
    app.router.add_get('/show_image', show_image)
    
    #app.router.add_static('/static/', path='./static', name='static')

    # Crear la carpeta 'uploads' si no existe
    os.makedirs('./uploads', exist_ok=True)
    os.makedirs('./Grayscale', exist_ok=True)
    os.makedirs('./resize', exist_ok=True)
    os.makedirs('./resized', exist_ok=True)
    
    # Configuración de SSL para habilitar HTTPS
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('/home/kbza/temp/cert.pem', '/home/kbza/temp/key.pem')

    runner = web.AppRunner(app)

    # Configurar el bucle de eventos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())

    #site = web.TCPSite(runner, '0.0.0.0', puerto,ssl_context=ssl_context) ver este tema
    # Permitir conexiones en IPv4
    site_ipv4 = web.TCPSite(runner, '0.0.0.0', puerto,ssl_context=ssl_context)
    loop.run_until_complete(site_ipv4.start())
    
    # Permitir conexiones en IPv6
    site_ipv6 = web.TCPSite(runner, '::', puerto, ssl_context=ssl_context)
    loop.run_until_complete(site_ipv6.start())

    print("Servidor web en ejecución en https://0.0.0.0:",puerto)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # Detener el servicio de escala de grises
        image_queue.put(None)
        grayscale_process.join()

        # Limpiar el bucle de eventos
        loop.run_until_complete(runner.cleanup())

        # Cerrar el bucle de eventos
        loop.stop()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        
        # Detener sitios IPv4 e IPv6
        loop.run_until_complete(site_ipv4.stop())
        loop.run_until_complete(site_ipv6.stop())