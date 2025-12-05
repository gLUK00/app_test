# Informes y Monitorización

Los informes dan el histórico detallado de ejecuciones.

## Acceder a Informes

*   **Desde Dashboard**: Pestaña "Reports" (si está) o desde la campaña.
*   **Desde la Campaña**: Sección "Reports" lista todas las ejecuciones.

## Detalle del Informe

Al hacer clic se abre la vista detallada:

![Página de reporte](../../assets/campaign_rapport.png)
> Página de reporte con estado y lista de tests ejecutados.

### Encabezado
*   **Estado**: Success, Failure o Running.
*   **Progreso**: Porcentaje completado.
*   **Entorno**: Entorno usado.
*   **Tiempos**: Inicio, Fin, Duración total.

### Resultados de Test
Lista de tests ejecutados.
*   **Icono de estado**: ✅ OK / ❌ Fail.
*   **Logs**: Expande para ver trazas.
    *   Datos enviados/recibidos.
    *   Tiempo por acción.
    *   Mensajes de error si falla.

## Actualización en Tiempo Real
Usa WebSockets para actualizar en vivo. No necesitas refrescar para ver progreso.
