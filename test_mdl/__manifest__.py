{
    'name': "Test Module",
    'summary': "Test Module",
    'author': 'Krish Prajapati',
    'category': 'Product',
    'version': '19.0.1.0.0',
    'depends': ['base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/bank_view.xml',
        'views/menu.xml',
    ],
    "application": True,
    "installable": True,
}
