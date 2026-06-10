{
    'name': "Subscription Management",
    'summary': "Summery of Subscription Management System",
    'author': 'Krish Prajapati',
    'category': 'Subscription',
    'version': '19.0.1.0.0',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/subscription_order_view.xml',
        'views/res_user_view.xml',
        'data/sequence.xml',
        'data/ir_cron.xml',
        'data/email_template.xml',
        'report/subscription_order_report.xml',
        'views/menu.xml',
    ],
    "application": True,
    "installable": True,
    "sequence": -1999
}
