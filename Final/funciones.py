#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys 
import binascii
import fnmatch
import re
import PIL

from concurrent import futures
from PIL import Image
import array

_ERROR_ARCHIVO = "El archivo no se encuentra en el directorio"

def abrir_archivo(file):
    '''Abre el archivo indicado en modo lectura'''
    try :
        fd = os.open(file, os.O_RDONLY)
        return fd
    except FileNotFoundError:
        return 0
    
def cambiar_imagengrises():
    image = Image.open(r"/home/kbza/Proyectos/Compu2-tp/imagen.jpg")
    width = image.size[0]
    height = image.size[1]
    for i in range(0,width): #leer todos los pixeles
        for j in range(0,height):
                data = image.getpixel((i,j))
                rojo = data[0]
                verde = data[1]
                azul = data[2]
                escalagrisis = int((rojo+verde+azul)/3)
                
                image.putpixel((i, j),(escalagrisis,escalagrisis,escalagrisis))
        
    image = image.save("") 
    print("Terminado ....")

def crear_archivo(file):
    '''Crea el archivo indicado en modo escritura'''
    fd = os.open(file, os.O_WRONLY | os.O_CREAT)
    return fd

def grayscale_worker(queue):
    while True:
        image_path = queue.get()
        if image_path is None:
            break

        # Procesar la imagen a escala de grises
        grayscale_image_path = os.path.join('./uploads', 'grayscale_' + os.path.basename(image_path))
        convert_to_grayscale(image_path, grayscale_image_path)
        # Agregar la imagen convertida a la cola de resultados
        output_queue.put(grayscale_image_path)
        
    

def convert_to_grayscale(input_path, output_path):
    try:
        image = Image.open(input_path).convert('L')
        image.save(output_path)
        print(f'Imagen convertida a escala de grises: {output_path}')
    except Exception as e:
        print(f'Error al procesar la imagen: {e}')
        
def remove_lead_and_trail_slash(s):
    if s.startswith('/'):
        s = s[1:]
    if s.endswith('/'):
        s = s[:-1]
    return s

def Index(path): 
		includes = ["*.jpg", "*.ppm"]
		html  = '<html>'
		html += '	<head>'
		html += '		<title>Directorio de Imagenes convertidas</title>'
		html += '	</head>'
		html += '	<body>'
		html += '		<p>Directorio:</p>'
		html += '		<ul>'
		for root, dirs, files in os.walk(path, topdown=False):
			for name in files:
				if name.endswith(('.jpg', '.ppm', '.html')):	
					html += '	<li><a href="' "." '/' + name + '">' + name + '</a></li>'
		html += '		</ul>'
		html += '	</body>'
		html += '</html>'

		body = bytearray(html, 'utf8')

		return body

def list_images(folder_path, allowed_formats=None):
    
    image_list = []

    # Si no se especifican formatos permitidos, se aceptan todos
    if allowed_formats is None:
        allowed_formats = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

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
grayscale_images_folder = './Grayscale'
grayscale_image_list = list_images(grayscale_images_folder)

#print(grayscale_image_list)

def generate_html_page(image_list):
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

    # Agregar imágenes a la página HTML con enlaces de descarga
    for filename in image_list:
        content += f'<div>'
        content += f'<img src="./Grayscale/{filename}" alt="{filename}">'
        content += f'<p><a href="./Grayscale/{filename}" download>Descargar {filename}</a></p>'
        content += f'</div>'

    content += """
        </body>
        </html>
    """

    return content