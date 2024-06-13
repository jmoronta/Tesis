import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import base64
from datetime import datetime, timedelta
import conexion as conexion

# Obtener los datos de la base de datos
datos = conexion.obtener_datos()

# Iniciar la aplicación Dash
app = dash.Dash(__name__)

# Crear el diseño del dashboard
app.layout = html.Div([
    html.H1('Datos de la tabla Patente'),
    html.Table([
        html.Thead(html.Tr([html.Th('Fecha y Hora'), html.Th('Imagen'), html.Th('Ubicación'), html.Th('Patente'), html.Th('Tiempo Transcurrido')])),
        html.Tbody([
            html.Tr([
                html.Td(print(fila[1])),
                html.Td(html.Img(src=f'data:image/jpeg;base64,{base64.b64encode(fila[2]).decode("utf-8")}', style={'max-width': '200px', 'max-height': '200px'})),
                html.Td(html.A(print(fila[3]), href=fila[3], target='_blank')),
                html.Td(print(fila[4])),
                #html.Td(datetime.now() - fila[1], className='rojo' if (datetime.now() - fila[1]) > timedelta(hours=1) else '')
            ]) for fila in datos
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)


if __name__ == '__main__':
    app.run_server(debug=True)
