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
        
        # Initialize Dash app with custom CSS for theme support
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.DARKLY],
            title="Project Argus - Network Security Dashboard",
            suppress_callback_exceptions=True
        )
        
        # Add custom CSS for theme switching
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    :root {
                        --bg-primary: #222;
                        --bg-secondary: #2d3135;
                        --text-primary: #fff;
                        --text-secondary: #adb5bd;
                        --border-color: #444;
                    }
                    
                    [data-theme="light"] {
                        --bg-primary: #f8f9fa;
                        --bg-secondary: #fff;
                        --text-primary: #212529;
                        --text-secondary: #6c757d;
                        --border-color: #dee2e6;
                    }
                    
                    body[data-theme="light"] {
                        background-color: var(--bg-primary) !important;
                        color: var(--text-primary) !important;
                    }
                    
                    [data-theme="light"] .card {
                        background-color: var(--bg-secondary) !important;
                        border-color: var(--border-color) !important;
                        color: var(--text-primary) !important;
                    }
                    
                    [data-theme="light"] .table {
                        color: var(--text-primary) !important;
                        background-color: var(--bg-secondary) !important;
                    }
                    
                    [data-theme="light"] h1, [data-theme="light"] h2, 
                    [data-theme="light"] h3, [data-theme="light"] h4,
                    [data-theme="light"] h5, [data-theme="light"] h6 {
                        color: var(--text-primary) !important;
                    }
                    
                    .theme-toggle-btn {
                        cursor: pointer;
                        padding: 5px 15px;
                        margin: 2px;
                    }
                </style>
                <script>
                    // Load theme from localStorage on page load
                    (function() {
                        const theme = localStorage.getItem('argus-theme') || 'dark';
                        document.documentElement.setAttribute('data-theme', theme);
                        if (theme === 'light') {
                            document.body.setAttribute('data-theme', 'light');
                        }
                    })();
                </script>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        
        self._setup_layout()
        self._setup_callbacks()
        
        logger.info("Dashboard initialized")
    
    def _setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = dbc.Container([
            # Store for theme preference
            dcc.Store(id='theme-store', storage_type='local', data='dark'),
            
            # Hidden div for clientside callbacks
            html.Div(id='theme-output', style={'display': 'none'}),
            
            # Header with System Status
            dbc.Row([
                dbc.Col([
                    html.H1("🛡️ Project Argus", className="text-center mb-2"),
                    html.H5("AI-Driven Network Threat Intelligence Platform", 
                           className="text-center text-muted mb-1"),
                    html.Div(id="system-status-badge", className="text-center mb-3")
                ])
            ]),
            
            # Theme Toggle
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("🌞 Light Mode", id="btn-light-theme", 
                                 color="light", outline=True, size="sm", className="theme-toggle-btn"),
                        dbc.Button("🌙 Dark Mode", id="btn-dark-theme", 
                                 color="dark", outline=False, size="sm", className="theme-toggle-btn"),
                    ], className="float-end mb-3")
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
            
            # Network Monitoring Configuration Card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🌐 Network Monitoring Configuration"),
                        dbc.CardBody([
                            html.Label("Select Monitoring Interface:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id='interface-dropdown',
                                placeholder="Select network interface...",
                                className="mb-3"
                            ),
                            html.Div(id='interface-description', className="text-muted small mb-3"),
                            dbc.Button("🔄 Apply & Restart Monitoring", 
                                     id="btn-restart-monitoring", 
                                     color="primary", 
                                     className="w-100",
                                     disabled=False),
                            html.Div(id='restart-status', className="mt-2")
                        ])
                    ])
                ], width=6),
                
                # System Overview Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 System Overview"),
                        dbc.CardBody([
                            html.Div([
                                html.P("ARGUS Device (Monitoring Hub)", className="text-center mb-2 fw-bold"),
                                html.Div(id="device-overview", className="text-center")
                            ])
                        ])
                    ])
                ], width=6),
            ], className="mb-4"),
            
            # Main Content Row
            dbc.Row([
                dbc.Col([
                    # Trust Score Chart
                    dbc.Card([
                        dbc.CardHeader("📈 Device Trust Scores"),
                        dbc.CardBody([
                            dcc.Graph(id="trust-score-chart")
                        ])
                    ])
                ], width=8),
                
                # Recent Alerts
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("⚠️ Recent Alerts"),
                        dbc.CardBody([
                            html.Div(id="recent-alerts", 
                                    style={"maxHeight": "400px", "overflowY": "auto"})
                        ])
                    ])
                ], width=4),
            ], className="mb-4"),
            
            # Quick Actions Card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("⚡ Quick Actions"),
                        dbc.CardBody([
                            dbc.ButtonGroup([
                                dbc.Button("🔍 Scan for New Devices", 
                                         id="btn-scan-devices",
                                         color="info", 
                                         className="me-2"),
                                dbc.Button("🚫 Block/Quarantine Selected", 
                                         id="btn-block-devices",
                                         color="warning",
                                         className="me-2"),
                                dbc.Button("📋 View Details", 
                                         id="btn-view-details",
                                         color="secondary"),
                            ], className="w-100"),
                            html.Div(id='quick-action-status', className="mt-2")
                        ])
                    ])
                ], width=12),
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
        
        # New callbacks for interface management
        @self.app.callback(
            Output('interface-dropdown', 'options'),
            Output('interface-dropdown', 'value'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_interface_options(n):
            """Load available network interfaces"""
            try:
                response = requests.get(f"{self.api_url}/api/interfaces", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    interfaces = data.get('interfaces', [])
                    current = data.get('current_interface', 'eth0')
                    
                    options = [
                        {'label': iface['display_name'], 'value': iface['name']}
                        for iface in interfaces
                    ]
                    
                    return options, current
            except Exception as e:
                logger.error(f"Error fetching interfaces: {e}")
            
            return [], 'eth0'
        
        @self.app.callback(
            Output('interface-description', 'children'),
            [Input('interface-dropdown', 'value')]
        )
        def update_interface_description(interface):
            """Update interface description based on selection"""
            if interface == 'simulated':
                return dbc.Alert(
                    "📊 Generates synthetic network flows with anomalies for demonstration purposes.",
                    color="info",
                    className="small mb-0"
                )
            elif interface:
                return html.P(f"Monitor live traffic on {interface}", className="text-muted small mb-0")
            return ""
        
        @self.app.callback(
            Output('restart-status', 'children'),
            [Input('btn-restart-monitoring', 'n_clicks')],
            [State('interface-dropdown', 'value')]
        )
        def restart_monitoring(n_clicks, interface):
            """Restart monitoring with selected interface"""
            if not n_clicks or not interface:
                return ""
            
            try:
                # Determine mode based on interface
                mode = 'simulated' if interface == 'simulated' else 'passive'
                
                response = requests.post(
                    f"{self.api_url}/api/interfaces/update",
                    json={'interface': interface, 'mode': mode},
                    timeout=10
                )
                
                if response.status_code == 200:
                    return dbc.Alert(
                        f"✅ Monitoring successfully restarted on {interface}!",
                        color="success",
                        dismissable=True,
                        duration=4000
                    )
                else:
                    return dbc.Alert(
                        f"❌ Error: {response.json().get('detail', 'Unknown error')}",
                        color="danger",
                        dismissable=True
                    )
            except Exception as e:
                logger.error(f"Error restarting monitoring: {e}")
                return dbc.Alert(
                    f"❌ Error: {str(e)}",
                    color="danger",
                    dismissable=True
                )
        
        @self.app.callback(
            Output('system-status-badge', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_system_status(n):
            """Update system status badge"""
            try:
                response = requests.get(f"{self.api_url}/api/system/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    mode = data.get('mode', 'passive')
                    interface = data.get('interface', 'unknown')
                    
                    if mode == 'simulated':
                        badge_text = f"🟢 ONLINE (Simulated Mode)"
                        badge_color = "info"
                    else:
                        badge_text = f"🟢 ONLINE (Passive Mode - {interface})"
                        badge_color = "success"
                    
                    return dbc.Badge(badge_text, color=badge_color, className="p-2")
            except Exception as e:
                logger.error(f"Error fetching system status: {e}")
            
            return dbc.Badge("⚪ OFFLINE", color="secondary", className="p-2")
        
        @self.app.callback(
            Output('device-overview', 'children'),
            [Input('stat-total-devices', 'children')]
        )
        def update_device_overview(total_devices):
            """Update device overview with icons"""
            device_count = int(total_devices) if total_devices.isdigit() else 0
            
            # Simple device representation
            return html.Div([
                html.Div("💻 Devices Detected:", className="mb-2"),
                html.Div([
                    dbc.Badge(f"{device_count}", color="primary", className="p-2 fs-5")
                ])
            ])
        
        # Theme switching callbacks
        @self.app.callback(
            Output('theme-store', 'data'),
            Output('btn-light-theme', 'outline'),
            Output('btn-dark-theme', 'outline'),
            [Input('btn-light-theme', 'n_clicks'),
             Input('btn-dark-theme', 'n_clicks')],
            [State('theme-store', 'data')]
        )
        def switch_theme(light_clicks, dark_clicks, current_theme):
            """Handle theme switching"""
            ctx = callback_context
            if not ctx.triggered:
                # Initial load
                return current_theme or 'dark', True if current_theme == 'light' else False, False if current_theme == 'light' else True
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'btn-light-theme':
                return 'light', False, True
            elif button_id == 'btn-dark-theme':
                return 'dark', True, False
            
            return current_theme or 'dark', True, False
        
        # Clientside callback for theme application
        self.app.clientside_callback(
            """
            function(theme) {
                if (theme) {
                    document.documentElement.setAttribute('data-theme', theme);
                    document.body.setAttribute('data-theme', theme);
                    localStorage.setItem('argus-theme', theme);
                }
                return '';
            }
            """,
            Output('theme-output', 'children'),
            Input('theme-store', 'data')
        )
        
        # Quick action callbacks
        @self.app.callback(
            Output('quick-action-status', 'children'),
            [Input('btn-scan-devices', 'n_clicks'),
             Input('btn-block-devices', 'n_clicks'),
             Input('btn-view-details', 'n_clicks')]
        )
        def handle_quick_actions(scan_clicks, block_clicks, view_clicks):
            """Handle quick action button clicks"""
            ctx = callback_context
            if not ctx.triggered:
                return ""
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'btn-scan-devices':
                return dbc.Alert(
                    "🔍 Device scanning initiated...",
                    color="info",
                    dismissable=True,
                    duration=3000
                )
            elif button_id == 'btn-block-devices':
                return dbc.Alert(
                    "⚠️ Please select devices from the table below to block/quarantine.",
                    color="warning",
                    dismissable=True,
                    duration=3000
                )
            elif button_id == 'btn-view-details':
                return dbc.Alert(
                    "📋 View device details in the table below.",
                    color="secondary",
                    dismissable=True,
                    duration=3000
                )
            
            return ""
    
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
