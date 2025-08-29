{
    'name': 'Tasas de Cambio Automática API',
    'version': '18.0.1.0.0',
    'summary': 'Módulo para obtener tipo de cambio desde API externa',
    'description': '''
        Este módulo permite:
        - Configurar una API externa para obtener tipo de cambio
        - Ejecutar automáticamente la llamada todos los días a las 5:00 AM (hora Perú)
        - Guardar las respuestas de la API para consulta posterior
        - Manejar errores de conexión de forma segura
    ''',
    'author': 'mhallasi',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/api_config_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}