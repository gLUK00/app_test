# Instalación Manual

Sigue estos pasos para instalar y ejecutar TestGyver directamente en tu máquina.

## 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd app_test
```

## 2. Crear Entorno Virtual

Se recomienda usar un entorno virtual para gestionar dependencias.

```bash
# Crear el entorno virtual
python3 -m venv .venv

# Activarlo
# En Linux/macOS:
source .venv/bin/activate
# En Windows:
# .venv\Scripts\activate
```

## 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## 4. Configuración

1.  Copia la configuración de ejemplo (si existe) o crea `configuration.json` en la raíz.
2.  Consulta la [Guía de Configuración](configuration.md) para más detalles.

## 5. Inicializar la Base de Datos (Opcional)

Puedes pre-cargar la base con datos iniciales e índices.

```bash
python init/init_database.py
```

Para crear un usuario admin:
```bash
python init/create_user.py
```

## 6. Ejecutar la Aplicación

```bash
# Variables de entorno
export FLASK_APP=app
export FLASK_ENV=development  # Usa 'production' para despliegue

# Ejecutar Flask
flask run --host=0.0.0.0 --port=8080
```

Accede a la aplicación en `http://localhost:8080`.
