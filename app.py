# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 16:16:07 2020

@author: santi
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import partridge as ptg
import io
import base64
from zipfile import ZipFile
import tempfile

app = dash.Dash()
server = app.server
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files'),
            ' New Predictions (*.zip)'
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        accept=".zip",
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])

@app.callback(dash.dependencies.Output('output-data-upload', 'children'),
              [dash.dependencies.Input('upload-data', 'contents')],
              [dash.dependencies.State('upload-data', 'filename'),
               dash.dependencies.State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    for content, name, date in zip(list_of_contents, list_of_names, list_of_dates):
        # the content needs to be split. It contains the type and the real content
        content_type, content_string = content.split(',')
        # Decode the base64 string
        content_decoded = base64.b64decode(content_string)
        # Use BytesIO to handle the decoded content
        zip_str = io.BytesIO(content_decoded)
        # Now you can use ZipFile to take the BytesIO output
        zip_obj = ZipFile(zip_str, 'r')
        

        with tempfile.TemporaryDirectory() as tmpdirname:
            zip_obj.extractall(tmpdirname)
            children = 'created temporary directory' + tmpdirname
            service_ids = ptg.read_busiest_date(tmpdirname)[1]
            view = {'trips.txt': {'service_id': service_ids}}
            
            feed = ptg.load_geo_feed(tmpdirname, view)
            
            routes = feed.routes
            trips = feed.trips
            stop_times = feed.stop_times
            stops = feed.stops
            shapes = feed.shapes

        return str(routes.loc[0,'route_short_name'])

if __name__ == '__main__':
    app.run_server(debug=False)
