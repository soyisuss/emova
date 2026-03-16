# EMOVA API

Esta es la API del backend para el sistema de **Emotion Monitoring and Visual Analysis (EMOVA)**. Está construida utilizando Python y FastAPI, diseñada para ser robusta, rápida y orientada a microservicios o contenedores.

La API se encarga de gestionar de forma segura los usuarios del sistema (Evaluadores), la autenticación mediante tokens JWT y el registro/lectura de reportes generados.

## 🚀 Tecnologías Principales

- **[FastAPI](https://fastapi.tiangolo.com/):** Framework web moderno y rápido para construir APIs con Python 3.10+, basado en Pydantic y tipado estático (Type hints).
- **[MongoDB](https://www.mongodb.com/) & [Motor](https://motor.readthedocs.io/):** Base de datos NoSQL rápida orientada a documentos, utilizando Motor para llamadas asíncronas no bloqueantes.
- **[Pydantic V2](https://docs.pydantic.dev/2.0/):** Validación de datos y gestión de configuraciones (basado en anotaciones de tipo).
- **[JWT (JSON Web Tokens)](https://jwt.io/):** Para la seguridad, generación de sesión de usuarios y autorización de rutas.
- **[uv](https://github.com/astral-sh/uv):** Gestor de paquetes y herramientas ultrarrápido escrito en Rust para correr el proyecto eficientemente.

---

## 🛠️ Estructura del Directorio

El código de la API (`src/emova/api`) está organizado de forma escalable (Arquitectura Multicapa / Domain-Driven Design ligero):

📁 `core/` - Configuraciones generales, variables de entorno y utilidades clave (como `config.py`).
📁 `db/` - Configuración de la base de datos, inyección de dependencias como clientes asíncronos (`database.py`).
📁 `models/` - Esquemas y validación de entidades principales usando Pydantic (`user.py`, `report.py`, `token.py`).
📁 `routers/` - Endpoints agrupados por dominio o entidad (`auth.py`, `users.py`, `reports.py`).
📄 `main.py` - Punto de entrada de la aplicación FastAPI, orquestador de middlewares, variables de ciclo de vida e inclusión de enrutadores.

---

## ⚙️ Configuración Inicial y Variables de Entorno

El servicio utiliza el paquete `pydantic-settings` para cargar configuraciones. Antes de levantar el proyecto, asegúrate de que exista un archivo `.env` en la misma ruta que `main.py` (`src/emova/api/.env`) con al menos las siguientes variables clave:

```env
# Ejemplo del archivo src/emova/api/.env
MONGODB_URL="mongodb://localhost:27017" # O un clúster como MongoDB Atlas
```

*(Las configuraciones sensibles adicionales, como `SECRET_KEY`, pueden proveerse también mediante el archivo `.env` para sobreescribir las opciones por defecto de `config.py`).*

---

## 🏃 ¿Cómo levantar el servicio? (Entorno de Desarrollo)

Para ejecutar el servidor en un ambiente de desarrollo y aprovechar las recargas automáticas (hot-reload) frente a cambios en el código, ubicándote en la raíz o utilizando el módulo `uv`, puedes utilizar el siguiente comando:

```bash
uv run fastapi dev src/emova/api/main.py
```

> **Nota**: Si tu terminal actual ya se encuentra dentro de la ruta `src/emova/api`, puedes utilizar directamente `uv run fastapi dev main.py`.

Una vez corriendo, el servicio levantará por lo general en el puerto `8000`. Podrás validar el estado entrando a:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📖 Documentación Automática (Interactive API Docs)

FastAPI genera vistas de documentación automática mediante los esquemas de OpenAPI en cuanto arrancamos el servidor.

1. **Swagger UI (Recomendada para pruebas)**:
   Ofrece una interfaz amigable donde puedes probar todos los endpoints y la autenticación directamente desde el navegador.
   👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

2. **ReDoc**:
   Documentación más estática y fácil de leer, excelente para entregar como referencia oficial de la API.
   👉 **[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)**

---

## 🔒 Rutas Principales

Una vista a nivel general de los módulos disponibles en nuestra API interactiva:

- **Autenticación (Auth)**: `/token` - Generación de token JWT al pasar `username` (email) y credenciales en esquema oAuth2.
- **Usuarios (Users)**: Endpoints `/users/...` enfocados a registro (`POST`), actualización, y lectura de perfiles limitados bajo seguridad y validación de hash Bcrypt.
- **Reportes (Reports)**: Endpoints `/reports/...` para almacenar registros vitales que generan modelos de Machine Learning y recuperar trazabilidad. Incluye subrutas protegidas.

**Nota de seguridad**: Muchos endpoints, en particular las creaciones/lecturas ajenas, confían en la cabecera `Authorization: Bearer <token>` para extraer la confirmación del usuario actual decodificándolo y validando privilegios.
