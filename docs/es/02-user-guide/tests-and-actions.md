# Tests y Acciones

Un **Test** es una secuencia de **Acciones**. TestGyver las ejecuta secuencialmente.

## Crear un Test

1.  Dentro de una Campaña, clic **Añadir Test**.
2.  Proporciona nombre y descripción.
3.  **Añade Variables** (Opcional): Variables del test (ej. `username`, `itemId`) para usar en acciones.

## Añadir Acciones

Las acciones son los bloques de construcción del test.

1.  Clic **Añadir Acción**.
2.  **Tipo de Acción**: Elige entre plugins disponibles (HTTP, SSH, Wait...).
3.  **Configura**: Completa parámetros específicos.

![Formulario de acción](../../assets/action_request.png)
> Formulario de acción (ej. HTTP) con campos.

### Autocompletado de Variables
Al escribir, TestGyver sugiere variables:

![Autocompletado de variables](../../assets/autocomplete.png)
> Dropdown de autocompletado al escribir `{{` con sugerencias coloreadas.

*   <span style="color:blue">**Variables Globales**</span>: `{{variable_name}}`
*   <span style="color:green">**Variables de Test**</span>: `{{app.variable_name}}`
*   <span style="color:red">**Variables de Colección**</span>: `{{test.test_id}}`, `{{test.files_dir}}`

### Variables de Salida
Algunas acciones generan salida (ej. cuerpo HTTP).
*   Se muestran como **Variables de Salida** en la configuración.
*   Puedes usarlas en acciones posteriores del mismo test.

## Orden de Acciones
Se ejecutan en el orden mostrado. Reordena con drag-and-drop o flechas.

## Ejecución
Puedes ejecutar un test individual desde su detalle para validarlo antes de lanzar la campaña completa.

## Plugins de Acción Disponibles

### Pause
Permite pausar la ejecución del test.
*   **Duración (ms)**: Duración de la pausa en milisegundos (obligatorio, defecto: 20ms).
*   **Mensaje**: Mensaje opcional para mostrar en los registros antes de la pausa.

