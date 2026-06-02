{
    'name': "Odoo Access Request",
    'summary': "Access Request",
    'author': 'Krish Prajapati',
    'category': 'Access & Request',
    'version': '19.0.1.0.0',
    'depends': ['base', 'mail', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/odoo_sh_access_request_view.xml',
        'views/res_users_view.xml',
        'views/project_project_view.xml',
        'views/project_task.xml',
        'data/sequence.xml',
        'data/ir_cron.xml',
        'wizard/access_request_reason_view.xml',
        'views/menu.xml',
    ],
    "application": True,
    "installable": True,
    "sequence": -101
}
