from odoo import models, fields, api

class MarketingKnowledge(models.Model):
    _name = 'marketing.knowledge'
    _description = 'Conocimiento de Marketing para IA'

    name = fields.Char(string='Título', required=True)
    content = fields.Text(string='Contenido del Documento', required=True)
    category = fields.Selection([
        ('strategy', 'Estrategia'),
        ('product', 'Información de Producto'),
        ('competitor', 'Competencia')
    ], string='Categoría', default='strategy')
    
    # Campo para rastrear si ya fue indexado en ChromaDB
    is_indexed = fields.Boolean(string='Indexado en VectorDB', default=False)

    def action_sync_to_vector_db(self):
        # Esta acción se puede llamar desde un botón en la UI
        for record in self:
            # Aquí llamaremos a la Tool que crearemos abajo
            pass