# app/services/config_service.py
from app.services.logger import app_logger
import json
import os
import re
from datetime import datetime

# Configuración por defecto del sistema
CONFIG_DEFAULT = {
    'umbral_amarillo': 0.4,
    'umbral_rojo': 0.7,
    'peso_rendimiento': 0.35,
    'peso_asistencia': 0.25,
    'peso_distribucion': 0.20,
    'peso_historial': 0.20,
    'nota_minima_aprobatoria': 12.0,
    'porcentaje_asistencia_minimo': 70.0
}

def obtener_semestre_actual():
    """Calcula el semestre actual basado en la fecha"""
    ahora = datetime.now()
    año = ahora.year
    mes = ahora.month
    
    # Lógica para determinar el semestre:
    # Enero-Junio: Semestre 1, Julio-Diciembre: Semestre 2
    semestre = 1 if 1 <= mes <= 6 else 2
    return f"{año}-{semestre}"

def get_config_path():
    """Obtiene la ruta del archivo de configuración"""
    return os.path.join(os.path.dirname(__file__), '..', 'config_sistema.json')

def cargar_configuracion():
    """Cargar configuración desde archivo o usar valores por defecto"""
    try:
        config_path = get_config_path()
        app_logger.info(f"📁 Buscando configuración en: {config_path}")
        
        # Crear configuración base con semestre actual
        config_base = CONFIG_DEFAULT.copy()
        config_base['semestre_actual'] = obtener_semestre_actual()
        
        if os.path.exists(config_path):
            app_logger.info("✅ Archivo de configuración encontrado")
            with open(config_path, 'r', encoding='utf-8') as f:
                config_cargada = json.load(f)
            
            app_logger.info(f"🔍 Configuración cargada: {list(config_cargada.keys())}")
            
            necesita_migracion = any([
                'peso_historial' not in config_cargada,
                'semestre_actual' not in config_cargada
            ])
            
            if necesita_migracion:
                app_logger.info("🔄 Migrando configuración a nueva estructura...")
                config_migrada = config_base.copy()
                
                # Migrar valores existentes
                campos_a_migrar = [
                    'umbral_amarillo', 'umbral_rojo', 
                    'nota_minima_aprobatoria', 'porcentaje_asistencia_minimo'
                ]
                for campo in campos_a_migrar:
                    if campo in config_cargada:
                        config_migrada[campo] = config_cargada[campo]
                
                if 'peso_distribucion' in config_cargada:
                    config_migrada['peso_distribucion'] = config_cargada['peso_distribucion']
                if 'peso_historial' in config_cargada:
                    config_migrada['peso_historial'] = config_cargada['peso_historial']
                
                guardar_configuracion(config_migrada)
                app_logger.info("✅ Migración completada")
                return config_migrada
            
            # Asegurar que el semestre actual esté presente
            if 'semestre_actual' not in config_cargada:
                config_cargada['semestre_actual'] = obtener_semestre_actual()
                guardar_configuracion(config_cargada)
            
            app_logger.info("✅ Usando configuración actual")
            return config_cargada
        else:
            app_logger.info("📝 No existe archivo de configuración, creando con valores por defecto")
            guardar_configuracion(config_base)
            return config_base
            
    except Exception as e:
        app_logger.error(f"❌ Error cargando configuración: {e}")
        config_base = CONFIG_DEFAULT.copy()
        config_base['semestre_actual'] = obtener_semestre_actual()
        return config_base

def guardar_configuracion(config):
    """Guardar configuración en archivo"""
    try:
        config_path = get_config_path()
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        app_logger.info("✅ Configuración guardada exitosamente")
        return True
    except Exception as e:
        app_logger.error(f"❌ Error guardando configuración: {e}")
        return False

def validar_configuracion(config):
    """Valida que la configuración tenga todos los campos necesarios y valores correctos"""
    errores = []
    
    # Verificar campos requeridos
    campos_requeridos = [
        'umbral_amarillo', 'umbral_rojo', 
        'peso_rendimiento', 'peso_asistencia', 'peso_distribucion',
        'semestre_actual', 'nota_minima_aprobatoria', 'porcentaje_asistencia_minimo'
    ]
    
    for campo in campos_requeridos:
        if campo not in config:
            errores.append(f"Campo requerido faltante: {campo}")
    
    if errores:
        return False, errores
    
    # Validar rangos
    validaciones = [
        (0 <= config['umbral_amarillo'] <= 1, "umbral_amarillo debe estar entre 0 y 1"),
        (0 <= config['umbral_rojo'] <= 1, "umbral_rojo debe estar entre 0 y 1"),
        (0 <= config['peso_rendimiento'] <= 1, "peso_rendimiento debe estar entre 0 y 1"),
        (0 <= config['peso_asistencia'] <= 1, "peso_asistencia debe estar entre 0 y 1"),
        (0 <= config['peso_distribucion'] <= 1, "peso_distribucion debe estar entre 0 y 1"),
        (0 <= config['nota_minima_aprobatoria'] <= 20, "nota_minima_aprobatoria debe estar entre 0 y 20"),
        (0 <= config['porcentaje_asistencia_minimo'] <= 100, "porcentaje_asistencia_minimo debe estar entre 0 y 100")
    ]
    
    for condicion, mensaje in validaciones:
        if not condicion:
            errores.append(mensaje)
    
    # Validar que los pesos sumen 1
    suma_pesos = (config['peso_rendimiento'] + config['peso_asistencia'] + 
                  config['peso_distribucion'] + config['peso_historial'])
    if abs(suma_pesos - 1.0) > 0.01:
        errores.append(f"Los pesos deben sumar 1.0 (suman {suma_pesos:.2f})")
    
    # Validar formato de semestre
    if not re.match(r'^\d{4}-[12]$', config['semestre_actual']):
        errores.append("Formato de semestre inválido. Use: AÑO-SEMESTRE (ej: 2025-1)")
    
    return len(errores) == 0, errores

def actualizar_semestre(nuevo_semestre):
    """Actualiza solo el semestre en la configuración"""
    try:
        if not re.match(r'^\d{4}-[12]$', nuevo_semestre):
            return False, "Formato de semestre inválido"
        
        config = cargar_configuracion()
        config['semestre_actual'] = nuevo_semestre
        guardar_configuracion(config)
        return True, "Semestre actualizado correctamente"
    except Exception as e:
        return False, str(e)