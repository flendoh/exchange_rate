# Exchange Rate API Module

## Descripción

Módulo de Odoo 18 para la obtención automática de tipos de cambio PEN→USD desde el servicio de SUNAT a través de **decolecta.com**.

## Características

- **Automatización**: Ejecución diaria a la 1:00 AM (hora Perú)
- **API Integration**: Conexión con decolecta.com usando Bearer Token
- **Timeout**: 30 segundos por llamada
- **Validación**: Botón de prueba de conexión

## Configuración

1. Ir a `Ajustes > Técnico > Acciones Automatizadas > Exchange Rate API`
2. Completar los campos:
   - **URL de la API**: `https://api.decolecta.com/v1/tipo-cambio/sunat`
   - **Bearer Token**: Tu token de decolecta.com
   - **Moneda Base**: PEN
   - **Moneda Destino**: USD
3. Usar "Probar Conexión" para validar
4. Activar la configuración

## Servicio Utilizado

### decolecta.com
- **Proveedor**: Datos oficiales de SUNAT
- **Frecuencia**: Diaria
- **Monedas**: PEN → USD
- **Autenticación**: Bearer Token
- **Documentación**: [decolecta.com](https://decolecta.com)

## Estructura del Módulo

```
exchange_rate/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   └── ir_cron.xml          # Cron job (1:00 AM Perú)
├── models/
│   └── exchange_rate_api.py # Lógica principal
├── security/
│   └── ir.model.access.csv  # Permisos
└── views/
    └── api_config_views.xml # Configuración
```

## Troubleshooting

### Problemas Comunes

1. **Error de Conexión**: Verificar URL y conectividad
2. **Error de Autenticación**: Verificar Bearer Token
3. **No se Actualizan**: Verificar que el cron esté activo

### Logs

Revisar logs de Odoo para ver el estado de las operaciones:
```bash
grep "exchange_rate" /var/log/odoo/odoo.log
```

## Licencia

LGPL-3

---

**Nota**: Este módulo está optimizado para el uso con decolecta.com para obtener tipos de cambio oficiales de SUNAT.
