import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import conexion as conexion

# Obtener los datos de la base de datos
datos = conexion.obtener_datos()

# Extraer las coordenadas de ubicación (latitud y longitud) de los datos
ubicaciones = [(fila[5], fila[6]) for fila in datos]

# Extraer los nombres de las ubicaciones para usarlos en las etiquetas del marcador
nombres_ubicaciones = [fila[4] for fila in datos]

# Crear el DataFrame para Plotly Express
df = px.data.carshare()
df['ubicacion'] = nombres_ubicaciones
df['latitud'] = [ubicacion[0] for ubicacion in ubicaciones]
df['longitud'] = [ubicacion[1] for ubicacion in ubicaciones]

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Crear el diseño del dashboard
app.layout = html.Div([
    html.H1('Mapa de Ubicaciones'),
    dcc.Graph(id='mapa-ubicaciones')
])

# Definir la función de callback para actualizar el mapa
@app.callback(
    Output('mapa-ubicaciones', 'figure'),
    Input('mapa-ubicaciones', 'id')
)
def update_map(id):
    # Crear el mapa con Plotly Express
    fig = px.scatter_mapbox(df, lat="latitud", lon="longitud", hover_name="ubicacion",
                            color_discrete_sequence=["fuchsia"], zoom=10, height=600)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
