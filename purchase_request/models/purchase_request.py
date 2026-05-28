from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Cerere de Achizitie'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Numar Cerere',
        readonly=True,
        default='New'
    )
    product_name = fields.Char(string='Produs', required=True)
    quantity = fields.Float(string='Cantitate', required=True, default=1.0)
    estimated_price = fields.Float(string='Pret Estimat', required=True)
    total_value = fields.Float(
        string='Valoare Totala',
        compute='_compute_total_value',
        store=True
    )
    reason = fields.Text(string='Motiv', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Trimis'),
        ('approved', 'Aprobat'),
        ('rejected', 'Respins'),
    ], string='Status', default='draft', tracking=True)
    requester_id = fields.Many2one(
        'res.users',
        string='Solicitant',
        default=lambda self: self.env.user,
        readonly=True
    )
    reject_reason = fields.Text(string='Motiv Respingere')
    value_eur = fields.Float(string='Valoare EUR', readonly=True)
    value_usd = fields.Float(string='Valoare USD', readonly=True)

    @api.depends('quantity', 'estimated_price')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.quantity * record.estimated_price

    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Cantitatea trebuie sa fie mai mare decat 0!")

    @api.constrains('estimated_price')
    def _check_price(self):
        for record in self:
            if record.estimated_price <= 0:
                raise ValidationError("Pretul estimat trebuie sa fie mai mare decat 0!")

    def action_submit(self):
        for record in self:
            _logger.info("Cerere %s trimisa de %s", record.name, record.requester_id.name)
            record.state = 'submitted'

    def action_approve(self):
        for record in self:
            if record.requester_id == self.env.user:
                raise ValidationError(
                    "Nu poti aproba propria cerere de achizitie!"
                )
            _logger.info("Cerere %s aprobata!", record.name)
            record.state = 'approved'

    def action_reject(self):
        for record in self:
            if record.requester_id == self.env.user:
                raise ValidationError(
                    "Nu poti aproba propria cerere de achizitie!"
                )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Respinge Cerere',
            'res_model': 'purchase.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
            }
        }

    def action_reset_draft(self):
        for record in self:
            record.state = 'draft'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or 'New'
        return super().create(vals)
    

    def action_convert_currency(self):
        import requests

        for record in self:
            try:
                response = requests.get('https://api.exchangerate-api.com/v4/latest/RON')
                data = response.json()

                eur_rate = data['rates']['EUR']
                usd_rate = data['rates']['USD']

                record.value_eur = record.total_value * eur_rate
                record.value_usd = record.total_value * usd_rate

                _logger.info(
                    "Conversie valuta pentru %s: %.2f RON = %.2f EUR = %.2f USD",
                    record.name, record.total_value, record.value_eur, record.value_usd
                )

            except Exception as e:
                _logger.error("Eroare conversie valuta: %s", str(e))
                raise ValidationError(f"Eroare la conversie valuta: {str(e)}")