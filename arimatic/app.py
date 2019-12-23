import base64
import datetime
import io
import os

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd

def get_layout_markdown():
    layout_path = os.path.join(
        os.path.dirname(__file__),
        'layout.md'
    )
    with open(layout_path, 'r') as layoutfile:
        layoutcontent = layoutfile.read()

    return layoutcontent.split('<!-- divider -->')


external_stylesheets = [
    # 'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://github.com/jgthms/bulma/blob/0.8.0/css/bulma.css',  # https://bulma.io/
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Markdown(get_layout_markdown()[0]),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
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
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
    dcc.Markdown(get_layout_markdown()[1]),
])


def read_data_file(contents, filename):
    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        return df
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

def get_table_display(df):
    return html.Div([
        html.Hr(),  # horizontal line
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line
    ])


def get_line_graph(df, filename):
    lg = dcc.Graph(
        figure=dict(
            data=[
                dict(
                    x=df[df.columns[0]],
                    y=df[df.columns[1]],
                    name=df.columns[1],
                    marker=dict(
                        color='rgb(55, 83, 109)'
                    )
                ),
                dict(
                    x=df[df.columns[0]],
                    y=df[df.columns[1]].rolling(window=3).mean(),
                    name=f"rolling_mean_{df.columns[1]}",
                    marker=dict(
                        color='rgb(55, 0, 0)'
                    )
                ),
            ],
            layout=dict(
                title=filename,
                showlegend=True,
                legend=dict(
                    x=0,
                    y=1.0
                ),
                margin=dict(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 300},
        id='my-graph'
    )
    return lg


def parse_contents_table(contents, filename, date):
    df = read_data_file(contents, filename)
    return html.Div([
        get_line_graph(df, filename),
        get_table_display(df),
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output_table(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents_table(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children




if __name__ == '__main__':
    app.run_server(debug=True)