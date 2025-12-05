# Gestión de Campañas

Una **Campaña** agrupa tests para validar una funcionalidad o flujo.

## Crear una Campaña

1.  En el Dashboard, clic **Añadir Campaña**.
2.  Completa:
    *   **Nombre**: Único para la campaña.
    *   **Descripción**: Opcional, propósito de la campaña.
3.  Guarda. Serás redirigido al detalle de la campaña.

> **[CAPTURA]** Formulario "Añadir Campaña".

## Vista de Detalle

Centro de control de la campaña.

> **[CAPTURA]** Página de detalles mostrando Información, Ficheros y Tests.

### 1. Información
Muestra metadatos. Puedes editar o borrar la campaña.

### 2. Gestión de Ficheros
Administra ficheros asociados (datos de test, recursos subidos).
*   **Subir**: Añadir ficheros al workdir de la campaña.
*   **Renombrar/Eliminar**: Gestionar ficheros existentes.
*   **Descargar**: Recuperar ficheros.

Estos ficheros son accesibles en tus tests con `{{test.files_dir}}`.

### 3. Lista de Tests
Muestra todos los tests.
*   **Reordenar**: Flechas Arriba/Abajo para cambiar orden.
*   **Añadir Test**: Crear un nuevo caso.
*   **Ejecutar**: Lanzar un test individual.

## Ejecutar una Campaña

1.  Clic en **Ejecutar Campaña**.
2.  **Configura**:
    *   **Nombre**: Auto-generado (ej. "March 2023"), editable.
    *   **Entorno**: Selecciona la filière (Variables).
    *   **Parar en fallo**: Si se marca, detiene al primer fallo.
3.  **Lanzar**: Se ejecuta en background.

> **[CAPTURA]** Modal de ejecución con selección de entorno.

### Monitorización en tiempo real
Verás barra de progreso y estados.
*   **Azul**: En ejecución
*   **Verde**: Completado ok
*   **Rojo**: Fallo

Haz clic en un reporte para ver logs detallados.
