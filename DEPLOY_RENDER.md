# Desplegar en Render

Esta guía te ayudará a desplegar tu aplicación de Georreferenciación en Render (gratis).

## Paso 1: Preparar la aplicación

Tu aplicación ya está lista. Los archivos necesarios han sido creados:
- `Procfile` - Indica a Render cómo ejecutar la app
- `runtime.txt` - Especifica la versión de Python
- `requirements.txt` - Lista todas las dependencias

## Paso 2: Crear cuenta en Render

1. Abre https://render.com
2. Haz clic en "Sign up"
3. Puedes usar tu cuenta de GitHub para registro rápido

## Paso 3: Conectar tu repositorio de GitHub

1. En el dashboard de Render, haz clic en "New +" → "Web Service"
2. Selecciona "Deploy an existing repository from GitHub"
3. Si Render no tiene acceso a tu GitHub:
   - Haz clic en "Connect account"
   - Autoriza a Render para acceder a tus repositorios
4. Selecciona `sistema-georreferenciacion`

## Paso 4: Configurar el servicio web

Completa los siguientes campos:

**Name (Nombre):** 
```
sistema-georreferenciacion
```
(o cualquier nombre que prefieras)

**Environment (Entorno):**
```
Python 3
```

**Build Command (Comando de construcción):**
```
pip install -r requirements.txt
```

**Start Command (Comando de inicio):**
```
gunicorn app:app
```

## Paso 5: Configurar variables de entorno

En la sección "Environment Variables", añade:

1. **SECRET_KEY** (muy importante para producción)
   - Nombre: `SECRET_KEY`
   - Valor: Genera una clave aleatoria (puedes usar un generador online)
   - Ejemplo: `sk-proj-abcdef123456xyz...`

2. **DATABASE_URL** (opcional - usa SQLite por defecto)
   - Si quieres una base de datos PostgreSQL gratuita:
   - Nombre: `DATABASE_URL`
   - Valor: Se proporciona al crear una base de datos en Render

3. **FLASK_ENV**
   - Nombre: `FLASK_ENV`
   - Valor: `production`

## Paso 6: Desplegar

1. Haz clic en "Create Web Service"
2. Render comenzará a desplegar (puede tomar 2-3 minutos)
3. Verás un URL como: `https://sistema-georreferenciacion.onrender.com`

## Paso 7: Usar tu aplicación

Una vez que el deployment esté completo:

1. Tu app estará en: `https://tu-app-name.onrender.com`
2. Accede a la página de login
3. Usa las credenciales de demo:
   - Email: `demo@test.com`
   - Contraseña: `123456`

## Posibles problemas

### "Build failed" o "Deployment failed"
- Revisa los logs en Render (sección "Logs")
- Verifica que todos los archivos estén subidos a GitHub
- Asegúrate de que `requirements.txt` esté actualizado

### La app carga pero muestra error
- Revisa los logs en el dashboard de Render
- Verifica que las variables de entorno estén configuradas correctamente

### Cambios locales no se reflejan
- Después de hacer cambios locales:
  ```bash
  git add .
  git commit -m "Tu mensaje de commit"
  git push origin main
  ```
- Render detectará los cambios automáticamente y redesplegará

## Notas importantes

- El plan gratuito de Render puede tener limitaciones en RAM y CPU
- Las bases de datos gratuitas tienen límites de almacenamiento
- Si el servicio no recibe solicitudes en 15+ minutos, entra en "sleep"
- Para aplicaciones de producción, considera un plan de pago

## Links útiles

- Documentación de Render: https://render.com/docs
- Python en Render: https://render.com/docs/deploy-python
- Variables de entorno: https://render.com/docs/environment-variables

---

¡Listo! Tu aplicación debería estar en línea en pocos minutos.
