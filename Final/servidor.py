import base64
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
from datetime import datetime,timedelta
import aiofiles

async def home(request):
    
    async with aiofiles.open('index.html', mode='r') as file:
        content = await file.read()

    return web.Response(text=content, content_type='text/html')

async def upload(request):
    async with aiofiles.open('upload.html', mode='r') as file:
        content = await file.read()
        
    return web.Response(text=content, content_type='text/html')

async def show(request):
    datos = conexion.obtener_datos()
    
    # Obtener la fecha y hora actual
    ahora = datetime.now()
    
    # Construir el contenido HTML
    contenido_html = """
    <html>
    <head>
        <title>Datos de la tabla Patente</title>
        <style>
            img { max-width: 200px; max-height: 200px; }
            .rojo { color: red; }
            .modal {
                display: none;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgb(0,0,0);
                background-color: rgba(0,0,0,0.4);
                padding-top: 60px;
            }
            .modal-content {
                background-color: #fefefe;
                margin: 5% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 80%;
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
            }
            .close:hover,
            .close:focus {
                color: black;
                text-decoration: none;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Datos de la tabla Patente</h1>
        <table border='1'>
            <tr>
                <th>Fecha y Hora</th>
                <th>Imagen</th>
                <th>Ubicación</th>
                <th>Patente</th>
                <th>Tiempo Transcurrido</th>
                <th></th>
            </tr>
    """
    
    for fila in datos:
        fecha_hora = fila[1].strftime("%Y-%m-%d %H:%M")  # Formatear fecha y hora
        imagen_base64 = base64.b64encode(fila[2]).decode('utf-8')
        ubicacion = fila[3]
        
        # Calcular el tiempo transcurrido
        tiempo_transcurrido = ahora - fila[1]
        horas, resto = divmod(tiempo_transcurrido.total_seconds(), 3600)
        minutos = resto // 60
        tiempo_transcurrido_formateado = f"{int(horas)} horas, {int(minutos)} minutos"
        
        # Redondear hacia arriba el tiempo en horas
        horas_redondeadas = int(horas) + (1 if minutos > 0 else 0)
        
        # Verificar si el tiempo transcurrido es mayor a una hora
        if tiempo_transcurrido > timedelta(hours=1):
            estilo_tiempo_transcurrido = 'rojo'
            boton_cobrar = f"""
                <form onsubmit="event.preventDefault(); cobrar({horas_redondeadas});">
                    <input type='hidden' name='tiempo' value='{horas_redondeadas}'>
                    <button type='submit'>Cobrar</button>
                </form>
            """
        else:
            estilo_tiempo_transcurrido = ''
            boton_cobrar = ''
        
        # Modificación para hacer que la ubicación sea un enlace
        contenido_html += f"""
            <tr>
                <td>{fecha_hora}</td>
                <td><img src='data:image/jpeg;base64,{imagen_base64}' alt='Imagen'></td>
                <td><a href='{ubicacion}' target='_blank'>{ubicacion}</a></td>
                <td>{fila[4]}</td>
                <td class='{estilo_tiempo_transcurrido}'>{tiempo_transcurrido_formateado}</td>
                <td>{boton_cobrar}</td>
            </tr>
        """
    
    contenido_html += """
        </table>

        <div id="myModal" class="modal">
            <div class="modal-content">
                <span class="close">&times;</span>
                <p id="modal-text"></p>
            </div>
        </div>

        <script>
            async function cobrar(tiempo) {
                const response = await fetch('/cobrar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `tiempo=${tiempo}`
                });

                const result = await response.text();
                document.getElementById('modal-text').innerText = result;
                document.getElementById('myModal').style.display = 'block';
            }

            var modal = document.getElementById("myModal");
            var span = document.getElementsByClassName("close")[0];

            span.onclick = function() {
                modal.style.display = "none";
            }

            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }
        </script>
    </body>
    </html>
    """

    return web.Response(text=contenido_html, content_type='text/html')


    #return web.Response('mostrar_datos.html', datos=datos)

    #return web.Response(text=content, content_type='text/html', headers={'Connection': 'close'})

async def cobrar(request):
    data = await request.post()
    tiempo = float(data['tiempo'])
    monto_a_pagar = tiempo * 500
    return web.Response(text=f'El monto a pagar es: ${monto_a_pagar:.2f}', content_type='text/plain')


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

async def handle_pagar(request):
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
    app.router.add_post('/pagar', handle_pagar)
    app.router.add_post('/cobrar', cobrar)
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