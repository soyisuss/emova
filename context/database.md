# Especificación Técnica para Creación de API: Proyecto EMOVA

Actúa como un desarrollador backend experto en FastAPI y MongoDB. Debes generar el código base (modelos de Pydantic y rutas) siguiendo el diagrama de clases y las reglas de negocio adjuntas.

## 1. Entidades de Dominio (Modelos de Datos)

### Evaluador
- `id_evaluador`: UUID/ObjectId (PK)
- `nombre`: string
- `correo`: string (EmailStr, Unique)
- `contrasena`: string (Hashed, no debe retornarse en respuestas de lectura)
- `profesion`: string

### Proyecto
- `id_proyecto`: UUID/ObjectId (PK)
- `nombre`: string
- `descripcion`: string
- `fecha_creacion`: datetime
- `id_evaluador`: UUID/ObjectId (FK)

### Tarea
- `id_tarea`: UUID/ObjectId (PK)
- `nombre`: string
- `descripcion`: string
- `id_proyecto`: UUID/ObjectId (FK)

### Participante
- `id_participante`: UUID/ObjectId (PK)
- `nombre`: string
- `edad`: integer
- `genero`: string
- `ocupacion`: string

### SesionPrueba
- `id_sesion`: UUID/ObjectId (PK)
- `fecha`: date
- `hora_inicio`: time
- `hora_fin`: time
- `id_tarea`: UUID/ObjectId (FK)
- `id_participante`: UUID/ObjectId (FK)

### Reporte
- `id_reporte`: UUID/ObjectId (PK)
- `fecha_generacion`: datetime
- `ruta_archivo`: string (URL de Google Cloud Storage)
- `id_sesion`: UUID/ObjectId (FK)

## 2. Relaciones y Cardinalidad
- **Evaluador (1) -> Proyectos (N)**
- **Proyecto (1) -> Tareas (N)**: Relación de composición (si el proyecto se elimina, sus tareas también).
- **Tarea (1) -> SesionPrueba (N)**
- **Participante (1) -> SesionPrueba (N)**
- **SesionPrueba (1) -> Reporte (1)**

## 3. Reglas de Negocio Obligatorias
- **RB9 (Seguridad):** El registro de `Evaluador` debe validar contraseñas con: mín. 8 caracteres, 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial.
- **RB5 (Integridad):** No permitir la eliminación de una `Tarea` si esta ya tiene asociada al menos una `SesionPrueba`.
- **RB7 (Emociones):** El sistema solo debe procesar las categorías: 'contento', 'descontento', 'neutral'.
- **Confidencialidad:** Las contraseñas se procesan con Argon2 o Bcrypt. Nunca se guardan en texto plano.

## 4. Requerimientos Técnicos del Código
- Usa **Pydantic v2** para esquemas de entrada y salida (separar `UserCreate` de `UserResponse`).
- Implementa **Inyección de Dependencias** para la conexión a MongoDB.
- Las rutas deben ser asíncronas (`async def`).
- Incluye manejo de excepciones HTTP (404 para recursos no encontrados, 400 para violaciones de reglas de negocio).
- Documentación automática con Swagger (incluir etiquetas por cada entidad).