from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_sales_commission(self, employee, date_from, date_to):
        # Fetch configuration parameters
        commission_percentage = float(self.env['ir.config_parameter'].sudo().get_param('sale_comission.sales_commission_percentage', default=2.5))
        company_margin_percentage = float(self.env['ir.config_parameter'].sudo().get_param('sale_comission.company_margin_percentage', default=80))

        # Fetch related sales orders within the given period
        sales_orders = self.env['sale.order'].search([
            ('user_id', '=', employee.user_id.id),
            ('state', '=', 'sale'),
            ('date_order', '>=', date_from),
            ('date_order', '<=', date_to)
        ])

        total_sales = sum(order.amount_total for order in sales_orders)
        company_commission = (total_sales * company_margin_percentage) / 100
        employee_commission = (company_commission * commission_percentage) / 100

        return employee_commission

    @api.onchange('employee_id')
    def _onchange_employee(self):
        """Automatically calculate and add sales commission to the payslip."""
        if self.employee_id and self.date_from and self.date_to:
            commission = self.get_sales_commission(self.employee_id,self.date_from, self.date_to)
            commission_input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'COM')], limit=1)

            if commission_input_type:
                self.input_line_ids = [(0, 0, {
                    'name': 'Sales Commission',
                    'amount': commission,
                    'input_type_id': commission_input_type.id
                })]



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Commission Percentages
    sales_commission_percentage = fields.Float(
        string="Sales Commission (%)", config_parameter='sale_comission.sales_commission_percentage')
    company_margin_percentage = fields.Float(
        string="Company Margin (%)", config_parameter='sale_comission.company_margin_percentage')
