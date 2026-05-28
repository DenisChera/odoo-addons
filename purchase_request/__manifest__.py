{
    'name': 'Purchase Request',
    'version': '1.0',
    'summary': 'Cereri de achizitie interne',
    'depends': ['base', 'mail'],
    'application': True,
    'data': [
        'security/purchase_request_security.xml',
        'security/ir.model.access.csv',
        'views/purchase_request_views.xml',
        'data/purchase_request_sequence.xml',
        'wizard/purchase_request_reject_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}