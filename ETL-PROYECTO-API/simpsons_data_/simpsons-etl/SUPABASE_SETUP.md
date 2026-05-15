# Supabase Setup para simpsons-etl

Estos son los pasos recomendados para enlazar el proyecto local con Supabase y crear migraciones.

## 1. Instalar Supabase CLI

Sigue la guía oficial si no lo tienes instalado:
https://supabase.com/docs/guides/cli

## 2. Ir al directorio correcto

```powershell
cd "c:\Users\sergi\Documents\ETL-INICIAL\etl-weatherstack\ETL-PROYECTO-API\simpsons_data_\simpsons-etl"
```

## 3. Enlazar el proyecto Supabase

```powershell
supabase link --project-ref kcpbqrokdusxipqbvpeb
```

Este comando vincula tu directorio local con el proyecto Supabase.

## 4. Crear una nueva migración

```powershell
supabase migration new new-migration
```

Esto genera un archivo de migración en `supabase/migrations`.

## 5. Configurar las credenciales de conexión

Edita `.env` usando `.env.example` como plantilla. Si usas Supabase, reemplaza el marcador de posición por tu contraseña real:

```text
DATABASE_URL=postgresql+psycopg2://postgres:<your-password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

Si prefieres usar variables por separado:

```text
DB_HOST=aws-0-us-east-1.pooler.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=<your-password>
```

## 6. Aplicar la migración

Si quieres aplicar cambios al esquema, usa:

```powershell
supabase db push
```

O para revisar la diferencia primero:

```powershell
supabase db diff
```

## 7. Verificar conexión desde Python

En el mismo directorio, ejecuta:

```powershell
python -m py_compile config\database.py
python -c "from config.database import engine; print(engine.url)"
```

> Nota: el archivo `.env` no se debe subir al repositorio, porque contiene credenciales privadas.
