{
    'name': "Nexus Trade Flow",
    'summary': "Nexus Trade Flow",
    'author': 'Krish Prajapati',
    'category': 'Trading',
    'version': '19.0.1.0.0',
    'depends': ['base', 'crm', 'sale_management', 'stock', 'purchase', 'sale_stock', 'purchase_stock'],
    'data': [
        'views/crm_lead_view.xml',
        'views/stock_picking_view.xml',
        'views/sale_order_view.xml',
        'data/ir_cron.xml'
    ],
    "application": True,
    "installable": True,
    "sequence": -112000
}
