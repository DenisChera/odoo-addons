from odoo import models, fields, api

class PurchaseRequestRejectWizard(models.TransientModel):
    _name = 'purchase.request.reject.wizard'
    _description = 'Wizard Respingere Cerere'

    request_id = fields.Many2one(
        'purchase.request',
        string='Cerere',
        required=True   
    )
    reject_reason = fields.Text(
        string='Motiv Respingere',
        required=True
    )

    def action_confirm_reject(self):
        self.request_id.reject_reason = self.reject_reason
        self.request_id.state = 'rejected'
        return {'type': 'ir.actions.act_window_close'}