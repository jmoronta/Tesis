import asyncio
from aiohttp import web
import os
import bottle
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 # 
from PIL import Image


async def handle_resize_from(request):
    reader = await request.multipart()
    field = await reader.next()
    
    # Nombre del archivo
    filename = field.filename
    
    # Ruta donde se guardará la imagen
    save_path = os.path.join('./resized', filename)

    # Guardar la imagen en el servidor
    with open(save_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)

    # Obtener el factor de escala desde el formulario
    #dato = await request.post()
    scale_field = await reader.next()
    scale_str = await scale_field.read()
    print(scale_str)
    try:
            scale = float(scale_str)
    except ValueError:
            return web.Response(text="Error: El valor de escala no es un número válido", status=400)

    # Redimensionar la imagen
    resized_image_path = os.path.join('./resized', 'resized_' + filename)
    resize_image(save_path, resized_image_path, scale)

    return web.Response(text=f'Imagen redimensionada: {resized_image_path}', content_type='text/plain')

def resize_image(input_path, output_path, scale):
    try:
        image = Image.open(input_path)
        # Obtener las nuevas dimensiones
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        print("Antes:",image.width, image.height)
        print("Despues:",new_height,new_width)
        # Redimensionar la imagen
        resized_image = image.resize((new_width, new_height))
        resized_image.save(output_path)
        print(f'Imagen redimensionada a {new_width}x{new_height}: {output_path}')
    except Exception as e:
        print(f'Error al redimensionar la imagen: {e}')

async def home(request):
    content= """
        <html>
			<head>
				<title>Servidor de tratamiento de imagenes</title>
			</head>
			<body>
			<h2>HOLA ESTOY CORRIENDO ESPERANDO PETICIONES</h2>
            </body>
		</html>
    """
    return web.Response(text=content, content_type='text/html')

if __name__ == '__main__':
    
    # Agregar la nueva ruta al router
    app = web.Application()
    app.router.add_post('/resize_from', handle_resize_from)
    app.router.add_get('/', home)
    
    runner = web.AppRunner(app)
    
    # Configurar el bucle de eventos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    
    #site = web.TCPSite(runner, '0.0.0.0', puerto,ssl_context=ssl_context) ver este tema
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    loop.run_until_complete(site.start())

    print("Servidor web en ejecución en https://0.0.0.0:",8080)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        
        # Limpiar el bucle de eventos
        loop.run_until_complete(runner.cleanup())

        # Cerrar el bucle de eventos
        loop.stop()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
