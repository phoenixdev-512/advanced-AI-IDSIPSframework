"""
Plotly Dash dashboard for Project Argus
"""

import logging
from typing import List, Dict, Any
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class ArgusDashboard:
    """Main dashboard for Project Argus"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize dashboard
        
        Args:
            api_url: URL of the FastAPI backend
        """
        self.api_url = api_url
        
        # Initialize Dash app
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.DARKLY],
            title="Project Argus - Network Security Dashboard"
        )
        
        self._setup_layout()
        self._setup_callbacks()
        
        logger.info("Dashboard initialized")
    
    def _setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("🛡️ Project Argus", className="text-center mb-4"),
                    html.H5("AI-Driven Network Threat Intelligence Platform", 
                           className="text-center text-muted mb-4")
                ])
            ]),
            
            # Statistics Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Devices", className="card-title"),
                            html.H2(id="stat-total-devices", children="0", 
                                   className="text-primary")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Low Trust", className="card-title"),
                            html.H2(id="stat-low-trust", children="0", 
                                   className="text-warning")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Critical", className="card-title"),
                            html.H2(id="stat-critical", children="0", 
                                   className="text-danger")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Blocked IPs", className="card-title"),
                            html.H2(id="stat-blocked", children="0", 
                                   className="text-info")
                        ])
                    ])
                ], width=3),
            ], className="mb-4"),
            
            # Trust Score Chart
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Device Trust Scores"),
                        dbc.CardBody([
                            dcc.Graph(id="trust-score-chart")
                        ])
                    ])
                ], width=8),
                
                # Recent Alerts
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Recent Alerts"),
                        dbc.CardBody([
                            html.Div(id="recent-alerts", 
                                    style={"maxHeight": "400px", "overflowY": "auto"})
                        ])
                    ])
                ], width=4),
            ], className="mb-4"),
            
            # Device Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Device Management"),
                        dbc.CardBody([
                            html.Div(id="device-table")
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Auto-refresh
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # Update every 5 seconds
                n_intervals=0
            ),
            
            # Hidden div for storing data
            html.Div(id='dummy-output', style={'display': 'none'})
            
        ], fluid=True, className="p-4")
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output('stat-total-devices', 'children'),
             Output('stat-low-trust', 'children'),
             Output('stat-critical', 'children'),
             Output('stat-blocked', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_stats(n):
            """Update statistics cards"""
            try:
                response = requests.get(f"{self.api_url}/api/stats", timeout=5)
                if response.status_code == 200:
                    stats = response.json()
                    return (
                        str(stats.get('total_devices', 0)),
                        str(stats.get('low_trust_devices', 0)),
                        str(stats.get('critical_devices', 0)),
                        str(stats.get('blocked_ips', 0))
                    )
            except Exception as e:
                logger.error(f"Error fetching stats: {e}")
            
            return "0", "0", "0", "0"
        
        @self.app.callback(
            Output('trust-score-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_trust_chart(n):
            """Update trust score chart"""
            try:
                response = requests.get(f"{self.api_url}/api/devices", timeout=5)
                if response.status_code == 200:
                    devices = response.json()
                    
                    if not devices:
                        return self._empty_chart()
                    
                    # Sort by trust score
                    devices = sorted(devices, key=lambda x: x['trust_score'])
                    
                    # Create bar chart
                    fig = go.Figure()
                    
                    colors = [
                        'red' if d['trust_score'] < 20 else
                        'orange' if d['trust_score'] < 50 else
                        'yellow' if d['trust_score'] < 75 else
                        'green'
                        for d in devices
                    ]
                    
                    fig.add_trace(go.Bar(
                        x=[d['device_ip'] for d in devices],
                        y=[d['trust_score'] for d in devices],
                        marker_color=colors,
                        text=[f"{d['trust_score']:.1f}" for d in devices],
                        textposition='auto',
                    ))
                    
                    fig.update_layout(
                        title="Device Trust Scores",
                        xaxis_title="Device IP",
                        yaxis_title="Trust Score",
                        yaxis_range=[0, 100],
                        template="plotly_dark",
                        height=400
                    )
                    
                    return fig
            except Exception as e:
                logger.error(f"Error fetching devices: {e}")
            
            return self._empty_chart()
        
        @self.app.callback(
            Output('device-table', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_device_table(n):
            """Update device table"""
            try:
                response = requests.get(f"{self.api_url}/api/devices", timeout=5)
                if response.status_code == 200:
                    devices = response.json()
                    
                    if not devices:
                        return html.P("No devices detected", className="text-muted")
                    
                    # Create table
                    table_header = [
                        html.Thead(html.Tr([
                            html.Th("IP Address"),
                            html.Th("Trust Score"),
                            html.Th("Anomalies"),
                            html.Th("Vulnerable Ports"),
                            html.Th("Status"),
                            html.Th("Actions")
                        ]))
                    ]
                    
                    rows = []
                    for device in sorted(devices, key=lambda x: x['trust_score']):
                        status_badge = self._get_status_badge(device)
                        rows.append(html.Tr([
                            html.Td(device['device_ip']),
                            html.Td(f"{device['trust_score']:.1f}"),
                            html.Td(str(device['anomaly_count'])),
                            html.Td(str(len(device['vulnerable_ports']))),
                            html.Td(status_badge),
                            html.Td([
                                dbc.ButtonGroup([
                                    dbc.Button("✓", size="sm", color="success", 
                                             id={"type": "whitelist", "ip": device['device_ip']}),
                                    dbc.Button("✗", size="sm", color="danger",
                                             id={"type": "block", "ip": device['device_ip']}),
                                ], size="sm")
                            ])
                        ]))
                    
                    table_body = [html.Tbody(rows)]
                    
                    return dbc.Table(
                        table_header + table_body,
                        bordered=True,
                        hover=True,
                        responsive=True,
                        striped=True,
                        className="table-dark"
                    )
            except Exception as e:
                logger.error(f"Error creating device table: {e}")
            
            return html.P("Error loading devices", className="text-danger")
        
        @self.app.callback(
            Output('recent-alerts', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_alerts(n):
            """Update recent alerts"""
            try:
                response = requests.get(f"{self.api_url}/api/devices", timeout=5)
                if response.status_code == 200:
                    devices = response.json()
                    
                    # Show devices with low trust scores as alerts
                    alerts = []
                    for device in devices:
                        if device['trust_score'] < 50 and not device['is_whitelisted']:
                            severity = "danger" if device['trust_score'] < 20 else "warning"
                            alerts.append(
                                dbc.Alert([
                                    html.Strong(f"{device['device_ip']}"),
                                    html.Br(),
                                    f"Trust Score: {device['trust_score']:.1f}",
                                    html.Br(),
                                    f"Anomalies: {device['anomaly_count']}"
                                ], color=severity, className="mb-2")
                            )
                    
                    if not alerts:
                        return html.P("No alerts", className="text-muted")
                    
                    return alerts[:5]  # Show only 5 most recent
            except Exception as e:
                logger.error(f"Error fetching alerts: {e}")
            
            return html.P("Error loading alerts", className="text-danger")
    
    def _get_status_badge(self, device: Dict[str, Any]) -> html.Span:
        """Get status badge for device"""
        if device['is_whitelisted']:
            return dbc.Badge("Whitelisted", color="success")
        elif device['is_blacklisted']:
            return dbc.Badge("Blacklisted", color="danger")
        elif device['trust_score'] < 20:
            return dbc.Badge("Critical", color="danger")
        elif device['trust_score'] < 50:
            return dbc.Badge("Warning", color="warning")
        else:
            return dbc.Badge("Normal", color="success")
    
    def _empty_chart(self) -> go.Figure:
        """Create empty chart"""
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            template="plotly_dark",
            height=400
        )
        return fig
    
    def run(self, host: str = "0.0.0.0", port: int = 8050, debug: bool = False):
        """Run dashboard server
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        logger.info(f"Starting dashboard on {host}:{port}")
        self.app.run_server(host=host, port=port, debug=debug)
