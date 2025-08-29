# -*- coding: utf-8 -*-
import requests
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ExchangeRateApi(models.Model):
    _name = 'exchange.rate.api'
    _description = 'Tasas de Cambio Automática'
    _rec_name = 'name'

    name = fields.Char(
        string='Nombre de Configuración',
        required=True,
        default='API Tipo de Cambio a USD',
        help='Nombre descriptivo para esta configuración de API'
    )
    
    base_url = fields.Char(
        string='URL Base de la API',
        required=True,
        default='https://api.decolecta.com/v1/tipo-cambio/sunat',
        help='URL completa del endpoint de la API para obtener tipo de cambio'
    )
    
    api_key = fields.Char(
        string='API Key',
        help='Clave de autenticación para la API',
        required=True
    )
    
    last_response = fields.Text(
        string='Última Respuesta',
        readonly=True,
        help='Respuesta completa de la última llamada a la API'
    )
    
    last_call = fields.Datetime(
        string='Última Llamada',
        readonly=True,
        help='Fecha y hora de la última llamada exitosa a la API'
    )

    company_id = fields.Many2one(
        'res.company',
        default=False,
        string="Empresa",
        help="Empresa específica para esta configuración."
    )

    target_currency_id = fields.Many2one(
        'res.currency',
        string='Moneda de Destino',
        required=True,
        readonly=True,
        default=1,
        help='Moneda a la cual se convertirá desde la moneda de la Empresa'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está marcado, esta configuración será usada por el cron'
    )

    def call_api(self, raise_on_error=False):
        """
        Método principal para llamar a la API externa.
        Este método es ejecutado por el cron job diariamente.
        """
        for record in self:
            if not record.active:
                _logger.info(f"Configuración '{record.name}' está inactiva, saltando llamada a API")
                continue
                
            try:
                _logger.info(f"Iniciando llamada a API: {record.base_url}")
                
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Odoo-API-Client/1.0'
                }
                
                if record.api_key:
                    headers['Authorization'] = f'Bearer {record.api_key}'
                
                response = requests.get(
                    record.base_url,
                    headers=headers,
                    timeout=30
                )
                
                response.raise_for_status()
                
                data = response.json()
                
                # Extraer el valor del tipo de cambio de la respuesta
                if 'sell_price' in data:
                    # Invertir el valor si la API devuelve PEN por USD pero necesitamos USD por PEN
                    rate_value = 1.0 / float(data['sell_price'])
                    
                    # Crear/actualizar el registro de tipo de cambio
                    record._create_currency_rate(rate_value)
                    
                    # Actualizar campos de seguimiento
                    record.write({
                        'last_response': response.text,
                        'last_call': fields.Datetime.now()
                    })
                
                _logger.info(f"Llamada a API exitosa para '{record.name}'. Status: {response.status_code}")
                
            except requests.exceptions.Timeout as e:
                error_msg = f"Timeout al llamar a la API '{record.name}': {record.base_url}"
                _logger.error(error_msg)
                if raise_on_error:
                    raise UserError(error_msg)
                
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Error de conexión al llamar a la API '{record.name}': {record.base_url}"
                _logger.error(error_msg)
                if raise_on_error:
                    raise UserError(error_msg)
                
            except requests.exceptions.HTTPError as e:
                error_msg = f"Error HTTP al llamar a la API '{record.name}': {e.response.status_code} - {e.response.text}"
                _logger.error(error_msg)
                if raise_on_error:
                    raise UserError(error_msg)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Error general al llamar a la API '{record.name}': {str(e)}"
                _logger.error(error_msg)
                if raise_on_error:
                    raise UserError(error_msg)
                
            except Exception as e:
                error_msg = f"Error inesperado en el procesamiento para '{record.name}': {str(e)}"
                _logger.error(error_msg)
                if raise_on_error:
                    raise UserError(error_msg)

    def action_test_api_connection(self):
        """
        Método para probar la conexión a la API manualmente desde la interfaz.
        """
        self.ensure_one()
        
        if not self.base_url:
            raise UserError("Debe configurar una URL base antes de probar la conexión.")
        
        try:
            old_response = self.last_response
            old_call = self.last_call
            
            self.call_api(raise_on_error=True)
            
            # Si llegamos aquí, la llamada fue exitosa
            return True
            
        except Exception as e:
            # Restaurar valores anteriores si hubo error
            self.write({
                'last_response': old_response,
                'last_call': old_call
            })
            
            raise UserError(f"Error al probar la conexión: {str(e)}")

    @api.model
    def cron_call_api(self):
        """
        Método específico para ser llamado por el cron.
        Busca todas las configuraciones activas y ejecuta call_api().
        """
        _logger.info("Ejecutando cron job para llamadas a API de tipo de cambio")
        
        active_configs = self.search([('active', '=', True)])
        
        if not active_configs:
            _logger.warning("No se encontraron configuraciones activas para llamar a la API")
            return
        
        _logger.info(f"Encontradas {len(active_configs)} configuraciones activas")
        
        # Llamar a la API para cada configuración activa
        active_configs.call_api()
        
        _logger.info("Cron job completado")

    def _create_currency_rate(self, rate_value, rate_date=None):
        """
        Crea un nuevo registro de tipo de cambio en res.currency.rate
        """
        self.ensure_one()
        
        if not rate_date:
            rate_date = fields.Date.today()
        
        # Buscar si ya existe un registro para esta fecha y moneda
        existing_rate = self.env['res.currency.rate'].search([
            ('currency_id', '=', self.target_currency_id.id),
            ('name', '=', rate_date),
            ('company_id', '=', self.company_id.id if self.company_id else False)
        ], limit=1)
        
        if existing_rate:
            # Actualizar el registro existente
            existing_rate.write({
                'rate': rate_value,
            })
            _logger.info(f"Tipo de cambio actualizado para {self.target_currency_id.name}: {rate_value}")
            return existing_rate
        else:
            # Crear nuevo registro
            new_rate = self.env['res.currency.rate'].create({
                'currency_id': self.target_currency_id.id,
                'rate': rate_value,
                'name': rate_date,
                'company_id': self.company_id.id if self.company_id else False,
            })
            _logger.info(f"Nuevo tipo de cambio creado para {self.target_currency_id.name}: {rate_value}")
            return new_rate
