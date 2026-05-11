
Rol	Usuario	Contraseña	Email	Permisos
Administrador	admin	admin123	admin@sades.edu	Acceso completo a todo el sistema
Coordinador	coordinador	coord123	coordinador@sades.edu	Gestión de estudiantes y cursos
Docente	docente	docente123	docente@sades.edu	Registro de notas y asistencias

---------------------------------------------------------------
markdown
# 📦 Guía de Actualización - Módulador

Guía paso a paso para actualizar la aplicación en el servidor de producción.

## 📋 Requisitos previos

- Acceso SSH al servidor
- Credenciales del servidor
- Conexión a internet

## 🔄 Pasos para actualizar

### 1. Conectarse al servidor

```bash
ssh servidor@dsi-server
cd ~/proyectos/modulador
2. Detener Gunicorn
bash
pkill -f gunicorn
3. Actualizar código desde GitHub
bash
git pull origin master
4. Actualizar dependencias Python
bash
source venv/bin/activate
pip install -r requirements.txt
5. Resetear base de datos (si es necesario)
⚠️ ADVERTENCIA: Esto borra TODOS los datos existentes.

bash
python reset_db.py
# Escribe 'SI' cuando pregunte para confirmar
6. Marcar migraciones como sincronizadas
bash
flask db stamp head
7. Iniciar Gunicorn nuevamente
bash
gunicorn --bind 127.0.0.1:8000 run:app &
8. Verificar que funciona
bash
curl http://127.0.0.1:8000
O abrir en navegador: http://ip-del-servidor

🚀 Script automatizado (opcional)
Para facilitar las actualizaciones, puedes crear este script:

bash
nano ~/actualizar-modulador.sh
Pega el siguiente contenido:

bash
#!/bin/bash
echo "🚀 Iniciando actualización de Módulador..."
cd ~/proyectos/modulador

echo "📦 Deteniendo Gunicorn..."
pkill -f gunicorn

echo "🔄 Actualizando código..."
git pull origin master

echo "📚 Actualizando dependencias..."
source venv/bin/activate
pip install -r requirements.txt

echo "🗄️ ¿Deseas resetear la base de datos? (s/n)"
read respuesta
if [ "$respuesta" = "s" ]; then
    echo "⚠️ Reseteando BD..."
    python reset_db.py
    flask db stamp head
fi

echo "🚀 Iniciando Gunicorn..."
gunicorn --bind 127.0.0.1:8000 run:app &

echo "✅ Actualización completada!"
Dar permisos de ejecución:

bash
chmod +x ~/actualizar-modulador.sh
Usar el script:

bash
~/actualizar-modulador.sh
🛠️ Comandos útiles
Verificar que Gunicorn está corriendo
bash
ps aux | grep gunicorn
Ver logs en tiempo real
bash
# Ver logs de la aplicación
tail -f logs/app.log

# Ver logs del sistema
journalctl -f
Matar Gunicorn si no responde
bash
pkill -9 -f gunicorn
Reiniciar completamente la app
bash
pkill -f gunicorn
cd ~/proyectos/modulador
source venv/bin/activate
gunicorn --bind 127.0.0.1:8000 run:app &
⚠️ Solución de problemas comunes
Error: "Address already in use"
bash
# El puerto 8000 está ocupado
sudo kill -9 $(sudo lsof -t -i:8000)
# Luego volver a iniciar Gunicorn
Error: "Module not found"
bash
# Reinstalar dependencias
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
La base de datos no se actualiza
bash
# Forzar recreación completa
source venv/bin/activate
python -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
"