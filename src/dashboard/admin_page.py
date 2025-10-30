"""
Admin & Model Training page for Project Argus Dashboard
"""

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc


def create_admin_layout():
    """Create the Admin & Model Training page layout"""
    
    layout = dbc.Container([
        # Page Header
        dbc.Row([
            dbc.Col([
                html.H2("⚙️ Admin & Model Training", className="mb-1"),
                html.P("Manage ML models and configure advanced settings", className="text-muted")
            ], width=8),
            dbc.Col([
                # Theme toggle will be added by main layout
                html.Div(id="admin-theme-toggle")
            ], width=4)
        ], className="mb-4"),
        
        # Train New Model Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("🚀 Train New Anomaly Detection Model", className="mb-0")
                    ]),
                    dbc.CardBody([
                        # Drag & Drop Upload Area
                        dbc.Row([
                            dbc.Col([
                                html.H5("Dataset Upload", className="mb-3"),
                                dcc.Upload(
                                    id='upload-dataset',
                                    children=html.Div([
                                        html.Div("📁", style={'fontSize': '48px', 'marginBottom': '10px'}),
                                        html.H5("Drag & Drop Your Dataset Here"),
                                        html.P("or click to select files", className="text-muted"),
                                        html.Small("Supported formats: .csv, .parquet, .pkl", className="text-muted")
                                    ]),
                                    style={
                                        'width': '100%',
                                        'height': '200px',
                                        'lineHeight': '200px',
                                        'borderWidth': '2px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '10px',
                                        'textAlign': 'center',
                                        'padding': '20px',
                                        'cursor': 'pointer',
                                        'backgroundColor': '#2d3135'
                                    },
                                    multiple=False
                                ),
                                html.Div(id='upload-status', className="mt-2"),
                                html.Div(id='uploaded-filename', className="mt-2 text-success")
                            ])
                        ], className="mb-4"),
                        
                        # Model Configuration
                        dbc.Row([
                            # Model Type Selection
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Model Type", className="fw-bold"),
                                    dbc.CardBody([
                                        dcc.RadioItems(
                                            id='model-type-select',
                                            options=[
                                                {'label': ' Autoencoder (Deep Learning)', 'value': 'autoencoder'},
                                                {'label': ' Isolation Forest (Ensemble)', 'value': 'isolation_forest'}
                                            ],
                                            value='autoencoder',
                                            labelStyle={'display': 'block', 'marginBottom': '10px'}
                                        )
                                    ])
                                ], className="h-100")
                            ], width=4),
                            
                            # Training Parameters
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Training Parameters", className="fw-bold"),
                                    dbc.CardBody([
                                        html.Label("Epochs:", className="form-label"),
                                        dcc.Input(
                                            id='epochs-input',
                                            type='number',
                                            value=50,
                                            min=10,
                                            max=500,
                                            className="form-control mb-2"
                                        ),
                                        html.Label("Batch Size:", className="form-label"),
                                        dcc.Input(
                                            id='batch-size-input',
                                            type='number',
                                            value=32,
                                            min=16,
                                            max=256,
                                            step=16,
                                            className="form-control"
                                        )
                                    ])
                                ], className="h-100")
                            ], width=4),
                            
                            # Validation & Test Options
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Validation & Test", className="fw-bold"),
                                    dbc.CardBody([
                                        dbc.Checklist(
                                            id='validation-options',
                                            options=[
                                                {'label': ' Cross-Validation (5-fold)', 'value': 'cv'},
                                                {'label': ' Hyperparameter Tuning', 'value': 'tuning'},
                                                {'label': ' Generate Report', 'value': 'report'}
                                            ],
                                            value=['cv', 'report'],
                                            labelStyle={'display': 'block', 'marginBottom': '10px'}
                                        )
                                    ])
                                ], className="h-100")
                            ], width=4)
                        ], className="mb-4"),
                        
                        # Start Training Button
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Start Training 🚀",
                                    id="btn-start-training",
                                    color="primary",
                                    size="lg",
                                    className="w-100",
                                    disabled=True
                                ),
                                html.Div(id='training-status', className="mt-3")
                            ])
                        ])
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Training History and Current Model Status
        dbc.Row([
            # Training History
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📊 Training History", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id='training-history-list', children=[
                            html.P("No training history available", className="text-muted text-center")
                        ])
                    ])
                ])
            ], width=6),
            
            # Current Model Status
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("✅ Current Model Status", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id='current-model-status', children=[
                            html.P("Model:", className="mb-1"),
                            html.H6("Autoencoder (Default)", className="text-primary mb-3"),
                            html.P("Last Trained:", className="mb-1"),
                            html.P("2024-01-15 14:30:00", className="text-muted mb-3"),
                            html.P("Status:", className="mb-1"),
                            dbc.Badge("Active", color="success", className="mb-3"),
                            html.Hr(),
                            dbc.Button(
                                "Activate Selected Model",
                                id="btn-activate-model",
                                color="success",
                                className="w-100",
                                disabled=True
                            )
                        ])
                    ])
                ])
            ], width=6)
        ], className="mb-4"),
        
        # Hidden div for storing selected model
        html.Div(id='selected-model-id', style={'display': 'none'}),
        
        # Auto-refresh interval for training status
        dcc.Interval(
            id='training-interval',
            interval=5*1000,  # 5 seconds
            n_intervals=0
        )
        
    ], fluid=True, className="p-4")
    
    return layout
