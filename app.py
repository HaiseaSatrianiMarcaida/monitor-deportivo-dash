import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime
import json
import os
import pandas as pd
import numpy as np
import matplotlib as mpl  
import plotly.graph_objects as go
from dash.dependencies import ClientsideFunction

# ===============================
# CONFIGURACIÃ“N BASE
# ===============================
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG, 
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
    ], 
    suppress_callback_exceptions=True
)
server = app.server
app.title = "Athletica â€“ Monitor Deportivo"
server = app.server

# CONFIGURACIÃ“N PARA PERMITIR CALLBACKS DUPLICADOS CON LLAMADA INICIAL
app.config.suppress_callback_exceptions = True
app.config.prevent_initial_callbacks = 'initial_duplicate'  

# ===============================
# ALMACENAMIENTO DE USUARIOS (ACTUALIZADO PARA DOCTORES)
# ===============================
USERS_FILE = "users.json"
DOCTORS_FILE = "doctors.json"

# FunciÃ³n para inicializar usuarios de prueba
def initialize_test_users():
    test_users = {
        "Haisea": {
            "password": "123",
            "email": "haisea.satriani@gmail.com",
            "full_name": "Haisea",
            "onboarding_completed": True,
            "activity_level": 10,
            "type": "athlete"
        },
        "test": {
            "password": "test",
            "email": "test@test.com", 
            "full_name": "Usuario Test",
            "onboarding_completed": True,
            "activity_level": 5,
            "type": "athlete"
        }
    }
    print(f"ðŸ‘¥ Usuarios de prueba inicializados: {list(test_users.keys())}")
    return test_users

# FunciÃ³n para inicializar mÃ©dicos de prueba
def initialize_test_doctors():
    test_doctors = {
        "medico1": {
            "password": "doctor123",
            "email": "dr.smith@athletica.com",
            "full_name": "Dr. John Smith",
            "type": "doctor",
            "patients": ["Haisea", "test"]  # AsegÃºrate que estos usuarios existen
        },
        "neuro_med": {
            "password": "neuro2024",
            "email": "neuro@neuralink.com",
            "full_name": "Dr. Neuralink Specialist",
            "type": "doctor",
            "patients": ["Haisea"]  # AÃ±ade algÃºn paciente
        }
    }
    print(f"ðŸ‘¨â€âš•ï¸ MÃ©dicos de prueba inicializados: {list(test_doctors.keys())}")
    return test_doctors

# FunciÃ³n para cargar usuarios desde archivo - VERSIÃ“N ACTUALIZADA
def load_users():
    # Primero inicializar con usuarios de prueba
    test_users = initialize_test_users()
    
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                file_users = json.load(f)
            
            print(f"âœ… Usuarios cargados desde archivo: {list(file_users.keys())}")
            
            # Combinar: usuarios del archivo tienen prioridad sobre usuarios de prueba
            combined_users = {**test_users, **file_users}
            return combined_users
            
        except Exception as e:
            print(f"âŒ Error cargando usuarios: {e}")
            print("ðŸ“‹ Usando usuarios de prueba como respaldo")
            return test_users
    else:
        print("ðŸ“‚ Archivo de usuarios no encontrado, usando usuarios de prueba")
        return test_users

# FunciÃ³n para cargar mÃ©dicos desde archivo
def load_doctors():
    # Primero inicializar con mÃ©dicos de prueba
    test_doctors = initialize_test_doctors()
    
    if os.path.exists(DOCTORS_FILE):
        try:
            with open(DOCTORS_FILE, 'r', encoding='utf-8') as f:
                file_doctors = json.load(f)
            
            print(f"âœ… MÃ©dicos cargados desde archivo: {list(file_doctors.keys())}")
            
            # Combinar: mÃ©dicos del archivo tienen prioridad sobre mÃ©dicos de prueba
            combined_doctors = {**test_doctors, **file_doctors}
            return combined_doctors
            
        except Exception as e:
            print(f"âŒ Error cargando mÃ©dicos: {e}")
            print("ðŸ“‹ Usando mÃ©dicos de prueba como respaldo")
            return test_doctors
    else:
        print("ðŸ“‚ Archivo de mÃ©dicos no encontrado, usando mÃ©dicos de prueba")
        return test_doctors

# FunciÃ³n para guardar mÃ©dicos en archivo
def save_doctors(doctors_data):
    try:
        with open(DOCTORS_FILE, 'w', encoding='utf-8') as f:
            json.dump(doctors_data, f, indent=2, ensure_ascii=False)
        print(f"ðŸ’¾ MÃ©dicos guardados: {len(doctors_data)} mÃ©dicos")
        return True
    except Exception as e:
        print(f"âŒ Error guardando mÃ©dicos: {e}")
        return False

def save_users(users_data):
    """Guarda usuarios en archivo"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        print(f"ðŸ’¾ Usuarios guardados: {len(users_data)} usuarios")
        return True
    except Exception as e:
        print(f"âŒ Error guardando usuarios: {e}")
        return False

def save_user(username, email, password, full_name=None, user_type="athlete"):
    """Guarda un nuevo usuario en la base de datos correspondiente"""
    
    if user_type == "doctor":
        # Guardar como mÃ©dico
        new_doctor = {
            "password": password,
            "email": email,
            "full_name": full_name if full_name else username,
            "type": "doctor",
            "patients": []  # Lista vacÃ­a de pacientes inicial
        }
        
        # Agregar a DOCTORS_DB
        DOCTORS_DB[username] = new_doctor
        
        # Guardar en archivo
        if save_doctors(DOCTORS_DB):
            print(f"âœ… Nuevo mÃ©dico registrado: {username} ({full_name})")
            return True
        else:
            print(f"âŒ Error guardando mÃ©dico: {username}")
            return False
    
    else:
        # Guardar como atleta (por defecto)
        new_user = {
            "password": password,
            "email": email,
            "full_name": full_name if full_name else username,
            "onboarding_completed": False,  # Atletas necesitan onboarding
            "activity_level": 5,  # Nivel por defecto
            "type": "athlete"
        }
        
        # Agregar a USERS_DB
        USERS_DB[username] = new_user
        
        # Guardar en archivo
        if save_users(USERS_DB):
            print(f"âœ… Nuevo atleta registrado: {username} ({full_name})")
            return True
        else:
            print(f"âŒ Error guardando atleta: {username}")
            return False

def mark_onboarding_completed(username):
    """Marca el onboarding como completado para un usuario"""
    if username in USERS_DB:
        USERS_DB[username]["onboarding_completed"] = True
        
        # Guardar el cambio
        if save_users(USERS_DB):
            print(f"âœ… Onboarding marcado como completado para {username}")
            return True
    
    print(f"âŒ Error marcando onboarding como completado para {username}")
    return False

def update_user_activity_level(username, activity_level):
    """Actualiza el nivel de actividad del usuario"""
    if username in USERS_DB:
        USERS_DB[username]["activity_level"] = activity_level
        
        # Guardar el cambio
        if save_users(USERS_DB):
            print(f"âœ… Nivel de actividad actualizado para {username}: {activity_level}")
            return True
    
    print(f"âŒ Error actualizando nivel de actividad para {username}")
    return False

def get_user_activity_level(username):
    """Obtiene el nivel de actividad del usuario"""
    if username in USERS_DB:
        return USERS_DB[username].get("activity_level", 5)
    return 5  # Valor por defecto

# Cargar usuarios y mÃ©dicos al inicio
USERS_DB = load_users()
DOCTORS_DB = load_doctors()

print(f"ðŸŽ¯ Base de datos lista: {len(USERS_DB)} usuarios y {len(DOCTORS_DB)} mÃ©dicos cargados")

# ===============================
# CALLBACKS DINÃMICOS PARA AÃ‘ADIR PACIENTES
# ===============================
# Lista para almacenar dinÃ¡micamente las saludos de los callbacks
add_patient_outputs = []

# Crear un callback para cada botÃ³n posible
def create_add_patient_callback(button_id):
    """Crea un callback para un botÃ³n especÃ­fico de aÃ±adir paciente"""
    
    @app.callback(
        [Output("doctor-search-results", "children", allow_duplicate=True),
         Output("doctor-dashboard-refresh-trigger", "data", allow_duplicate=True)],
        [Input(button_id, "n_clicks")],
        [State(f"patient-username-{button_id.replace('add-patient-btn-', '')}", "value"),
         State("current-user", "data"),
         State("doctor-search-input", "value"),
         State("url", "pathname")],
        prevent_initial_call=True
    )
    def handle_add_patient(n_clicks, patient_username, current_user, search_term, pathname):
        """Maneja la adiciÃ³n de un paciente especÃ­fico"""
        
        if pathname != '/doctor-dashboard':
            raise dash.exceptions.PreventUpdate
        
        if not n_clicks or not patient_username or not current_user:
            raise dash.exceptions.PreventUpdate
        
        print(f"ðŸ‘¨â€âš•ï¸ AÃ±adiendo paciente {patient_username} al mÃ©dico {current_user}")
        
        # Verificar si ya es paciente
        if current_user in DOCTORS_DB:
            current_patients = DOCTORS_DB[current_user].get("patients", [])
            if patient_username in current_patients:
                print(f"âš ï¸ Paciente {patient_username} ya estÃ¡ en la lista")
                
                # Actualizar resultados de bÃºsqueda
                search_results = search_users_by_name(search_term) if search_term else []
                updated_results = create_search_results_display(search_results, current_user)
                
                return updated_results, dash.no_update
        
        # AÃ±adir paciente
        success = add_patient_to_doctor(current_user, patient_username)
        
        if success:
            print(f"âœ… Paciente {patient_username} aÃ±adido exitosamente")
            
            # 1. Actualizar resultados de bÃºsqueda
            search_results = search_users_by_name(search_term) if search_term else []
            updated_results = create_search_results_display(search_results, current_user)
            
            # 2. Forzar refresco del dashboard
            import time
            refresh_trigger = time.time()
            
            # 3. Mostrar mensaje de Ã©xito temporal
            from dash import callback_context
            if callback_context.triggered_id == button_id:
                # PodrÃ­as agregar un toast o notificaciÃ³n aquÃ­
                pass
            
            return updated_results, refresh_trigger
        
        return dash.no_update, dash.no_update
    
    return handle_add_patient

# FunciÃ³n auxiliar para crear la visualizaciÃ³n de resultados
def create_search_results_display(search_results, current_user):
    """Crea la visualizaciÃ³n de resultados de bÃºsqueda"""
    
    if not search_results:
        return html.Div(
            "No se encontraron pacientes con ese criterio",
            style={'color': '#666', 'fontStyle': 'italic', 'padding': '10px', 'textAlign': 'center'}
        )
    
    # Obtener pacientes actuales del mÃ©dico
    current_patients = []
    if current_user in DOCTORS_DB:
        current_patients = DOCTORS_DB[current_user].get("patients", [])
    
    # Crear lista de resultados
    result_items = []
    for result in search_results:
        username = result["username"]
        full_name = result["full_name"]
        email = result["email"]
        activity_level = result["activity_level"]
        
        # Verificar si ya es paciente de este mÃ©dico
        is_current_patient = username in current_patients
        
        # Crear ID Ãºnico para el botÃ³n
        button_id = f"add-patient-btn-{username.replace('.', '-').replace('@', '-')}"
        
        # Registrar el callback si no existe
        if button_id not in [cb['id'] for cb in add_patient_outputs]:
            add_patient_outputs.append({'id': button_id, 'callback': create_add_patient_callback(button_id)})
        
        # Crear el resultado
        result_item = html.Div(
            style={
                'backgroundColor': '#2b2b2b',
                'borderRadius': '8px',
                'padding': '15px',
                'marginBottom': '10px',
                'border': f'1px solid {HIGHLIGHT_COLOR if not is_current_patient else "#4ecdc4"}'
            },
            children=[
                html.Div(
                    style={
                        'display': 'flex',
                        'justifyContent': 'space-between',
                        'alignItems': 'center',
                        'marginBottom': '10px'
                    },
                    children=[
                        html.Div(
                            style={'flex': '1'},
                            children=[
                                html.Div(
                                    full_name,
                                    style={
                                        'fontWeight': '600',
                                        'color': '#fff',
                                        'fontSize': '1rem'
                                    }
                                ),
                                html.Div(
                                    f"@{username} â€¢ {email}",
                                    style={
                                        'color': '#ccc',
                                        'fontSize': '0.8rem',
                                        'marginTop': '5px'
                                    }
                                )
                            ]
                        ),
                        html.Div(
                            style={
                                'backgroundColor': f'rgba({", ".join(str(int(c * 255)) for c in mpl.colors.to_rgb(HIGHLIGHT_COLOR if not is_current_patient else "#4ecdc4"))}, 0.1)',
                                'padding': '5px 10px',
                                'borderRadius': '12px',
                                'fontSize': '0.8rem',
                                'fontWeight': '500',
                                'color': HIGHLIGHT_COLOR if not is_current_patient else "#4ecdc4"
                            },
                            children=f"Nivel {activity_level}/10"
                        )
                    ]
                ),
                
                html.Button(
    "+ AÃ±adir como paciente",  # SIEMPRE este texto
    id={
        "type": "add-patient-btn",
        "patient-username": username
    },
    n_clicks=0,
    style={
        'width': '100%',
        'padding': '10px',
        'backgroundColor': HIGHLIGHT_COLOR,
        'border': f'1px solid {HIGHLIGHT_COLOR}',
        'borderRadius': '6px',
        'color': '#0a0a0a',
        'fontWeight': '600',
        'cursor': 'pointer',
        'opacity': '1',
        'transition': 'all 0.3s ease'
    },
    disabled=False  # NUNCA deshabilitado
),
                
                # Input oculto con el username
                dcc.Input(
                    id=f"patient-username-{username.replace('.', '-').replace('@', '-')}",
                    type="hidden",
                    value=username
                )
            ]
        )
        result_items.append(result_item)
    
    return html.Div(result_items)

def _authenticate_in_db(identifier, password, db, user_type, entity_label):
    """Autentica por username o email en una base dada, conservando logs actuales."""
    if identifier in db:
        data = db[identifier]
        if data["password"] == password:
            print(f"? Login exitoso como {entity_label}: '{identifier}'")
            return True, {**data, "user_type": user_type}
        print(f"? Contraseña incorrecta para {entity_label} '{identifier}'")
        return True, None

    for db_key, data in db.items():
        if data.get("email") == identifier:
            if data["password"] == password:
                print(f"? Login exitoso por email {entity_label}: '{identifier}' -> '{db_key}'")
                return True, {**data, "user_type": user_type}
            print(f"? Contraseña incorrecta para email {entity_label} '{identifier}'")
            return True, None

    return False, None


def verify_user(username, password):
    """Verifica credenciales en ambas bases de datos (atletas y médicos)"""
    print(f"?? Verificando: '{username}'")

    found, user_data = _authenticate_in_db(username, password, DOCTORS_DB, "doctor", "médico")
    if found:
        return user_data

    found, user_data = _authenticate_in_db(username, password, USERS_DB, "athlete", "atleta")
    if found:
        return user_data

    print(f"? Usuario/email '{username}' no encontrado")
    return None
def get_user_type(username):
    """Obtiene el tipo de usuario (doctor o athlete)"""
    if username in DOCTORS_DB:
        return "doctor"
    elif username in USERS_DB:
        return "athlete"
    else:
        return None


def get_email_owner_type(email):
    """Devuelve el tipo de usuario que ya usa un email, o None si no existe."""
    for user_data in USERS_DB.values():
        if user_data.get("email") == email:
            return "athlete"

    for doctor_data in DOCTORS_DB.values():
        if doctor_data.get("email") == email:
            return "doctor"

    return None

def add_patient_to_doctor(doctor_username, patient_username):
    """AÃ±ade un paciente a la lista de pacientes de un mÃ©dico"""
    if doctor_username in DOCTORS_DB and patient_username in USERS_DB:
        if patient_username not in DOCTORS_DB[doctor_username]["patients"]:
            DOCTORS_DB[doctor_username]["patients"].append(patient_username)
            if save_doctors(DOCTORS_DB):
                print(f"âœ… Paciente '{patient_username}' aÃ±adido al mÃ©dico '{doctor_username}'")
                return True
    print(f"âŒ Error aÃ±adiendo paciente '{patient_username}' al mÃ©dico '{doctor_username}'")
    return False

def remove_patient_from_doctor(doctor_username, patient_username):
    """Elimina un paciente de la lista de pacientes de un mÃ©dico"""
    if doctor_username in DOCTORS_DB:
        if patient_username in DOCTORS_DB[doctor_username]["patients"]:
            DOCTORS_DB[doctor_username]["patients"].remove(patient_username)
            if save_doctors(DOCTORS_DB):
                print(f"âœ… Paciente '{patient_username}' eliminado del mÃ©dico '{doctor_username}'")
                return True
    print(f"âŒ Error eliminando paciente '{patient_username}' del mÃ©dico '{doctor_username}'")
    return False

def get_doctor_patients(doctor_username):
    """Obtiene la lista de pacientes de un mÃ©dico"""
    if doctor_username in DOCTORS_DB:
        return DOCTORS_DB[doctor_username].get("patients", [])
    return []

def search_users_by_name(search_term):
    """Busca usuarios (atletas) por nombre"""
    results = []
    search_term_lower = search_term.lower()
    
    for username, user_data in USERS_DB.items():
        full_name = user_data.get("full_name", "").lower()
        email = user_data.get("email", "").lower()
        
        if (search_term_lower in username.lower() or 
            search_term_lower in full_name or 
            search_term_lower in email):
            results.append({
                "username": username,
                "full_name": user_data.get("full_name", username),
                "email": user_data.get("email", ""),
                "activity_level": user_data.get("activity_level", 5)
            })
    
    return results

# ===============================
# CONFIGURACIÃ“N DE ESTILOS Y VARIABLES
# ===============================
HIGHLIGHT_COLOR = "#00d4ff"
DARK_BACKGROUND = "#0a0a0a"

SPORTS_OPTIONS = [
    {"label": "Correr", "icon": "bi bi-run"},
    {"label": "Ciclismo", "icon": "bi bi-bicycle"},
    {"label": "NataciÃ³n", "icon": "bi bi-swim"},
    {"label": "Gym (Pesas)", "icon": "bi bi-fire"},
    {"label": "CrossFit (HIIT)", "icon": "bi bi-lightning-fill"},
    {"label": "Yoga / Pilates", "icon": "bi bi-yoga"},
    {"label": "FÃºtbol", "icon": "bi bi-trophy"},
    {"label": "Baloncesto", "icon": "bi bi-dribbble"},
    {"label": "Otro / Ninguno", "icon": "bi bi-question-circle"},
]

HEALTH_CONDITIONS = [
    "Diabetes", "HipertensiÃ³n", "Asma", "Problemas cardÃ­acos", 
    "Artritis", "Ninguna"
]

DIET_RESTRICTIONS = [
    "Vegetariano", "Vegano", "Sin gluten", "Sin lactosa", 
    "AlÃ©rgico a frutos secos", "Ninguna"
]

# ===============================
# DATOS DE ENTRENAMIENTOS GUIADOS (ACTUALIZADO)
# ===============================

GUIDED_WORKOUTS = {
    "fuerza": {
        "name": "Entrenamiento de Fuerza",
        "type": "fuerza",
        "body_parts": {
            "piernas": {
                "name": "Piernas",
                "exercises": [
                    {
                        "name": "Saltos de tijera",
                        "description": "Ejercicio cardiovascular para calentamiento",
                        "sets": 1,
                        "reps": "30 segundos",
                        "rest": "10s",
                        "image": "âœ‚ï¸",
                        "instructions": ["Salta abriendo piernas y brazos", "Alterna rÃ¡pidamente", "MantÃ©n el ritmo constante"]
                    },
                    {
                        "name": "Elevaciones de rodillas",
                        "description": "Calentamiento de piernas y core",
                        "sets": 1,
                        "reps": "30 segundos",
                        "rest": "10s",
                        "image": "ðŸ¦µ",
                        "instructions": ["Corre elevando rodillas al pecho", "MantÃ©n espalda recta", "Brazos en movimiento"]
                    },
                    {
                        "name": "Trote con flexiÃ³n de rodilla",
                        "description": "Calentamiento completo",
                        "sets": 1,
                        "reps": "30 segundos",
                        "rest": "10s",
                        "image": "ðŸƒâ€â™‚ï¸",
                        "instructions": ["Trota suavemente", "Flexiona rodillas hacia atrÃ¡s", "Alterna piernas"]
                    },
                    {
                        "name": "Squats",
                        "description": "Ejercicio fundamental para piernas",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "30s",
                        "image": "ðŸª‘",
                        "instructions": ["Pies al ancho de hombros", "Baja como si te sentaras", "Espalda recta", "Rodillas alineadas"]
                    },
                    {
                        "name": "Fire Hydrant izquierdo",
                        "description": "Para glÃºteos y cadera",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "20s",
                        "image": "ðŸ•",
                        "instructions": ["PosiciÃ³n de cuadrupedia", "Eleva pierna izquierda lateral", "MantÃ©n core activado"]
                    },
                    {
                        "name": "Fire Hydrant derecho",
                        "description": "Para glÃºteos y cadera",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "20s",
                        "image": "ðŸ•",
                        "instructions": ["PosiciÃ³n de cuadrupedia", "Eleva pierna derecha lateral", "MantÃ©n core activado"]
                    },
                    {
                        "name": "Zancadas frontales",
                        "description": "Piernas alternas",
                        "sets": 3,
                        "reps": "10-12 por pierna",
                        "rest": "30s",
                        "image": "ðŸ‘£",
                        "instructions": ["Da un paso adelante", "Baja hasta 90 grados", "Alterna piernas", "MantÃ©n equilibrio"]
                    },
                    {
                        "name": "CÃ­rculos con pierna izquierda",
                        "description": "Movilidad y fuerza",
                        "sets": 2,
                        "reps": "15 cÃ­rculos",
                        "rest": "15s",
                        "image": "ðŸŒ€",
                        "instructions": ["Acostado de lado", "CÃ­rculos con pierna extendida", "Controla el movimiento"]
                    },
                    {
                        "name": "CÃ­rculos con pierna derecha",
                        "description": "Movilidad y fuerza",
                        "sets": 2,
                        "reps": "15 cÃ­rculos",
                        "rest": "15s",
                        "image": "ðŸŒ€",
                        "instructions": ["Acostado de lado", "CÃ­rculos con pierna extendida", "Controla el movimiento"]
                    },
                    {
                        "name": "Sentadilla de sumo",
                        "description": "Para aductores y glÃºteos",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "30s",
                        "image": "ðŸ¦€",
                        "instructions": ["Pies mÃ¡s anchos que hombros", "Puntas hacia afuera", "Baja manteniendo espalda recta"]
                    },
                    {
                        "name": "Sentadilla en pared",
                        "description": "IsomÃ©trico para quadriceps",
                        "sets": 2,
                        "reps": "30-45 segundos",
                        "rest": "30s",
                        "image": "ðŸ§±",
                        "instructions": ["Espalda contra la pared", "Piernas a 90 grados", "MantÃ©n la posiciÃ³n"]
                    },
                    {
                        "name": "Levantamiento de pantorrillas",
                        "description": "Para gemelos",
                        "sets": 3,
                        "reps": "15-20 repeticiones",
                        "rest": "20s",
                        "image": "â¬†ï¸",
                        "instructions": ["De pie, eleva talones", "MÃ¡xima extensiÃ³n", "Baja controladamente"]
                    },
                    {
                        "name": "Levantamiento de pantorrilla con salto",
                        "description": "Potencia explosiva",
                        "sets": 2,
                        "reps": "12-15 repeticiones",
                        "rest": "25s",
                        "image": "ðŸ’¥",
                        "instructions": ["Salto explosivo desde gemelos", "Suave aterrizaje", "Ritmo constante"]
                    },
                    {
                        "name": "Sentadilla con salto",
                        "description": "Ejercicio pliomÃ©trico",
                        "sets": 3,
                        "reps": "10-12 repeticiones",
                        "rest": "35s",
                        "image": "ðŸš€",
                        "instructions": ["Sentadilla profunda", "Salto explosivo", "Aterriza suavemente"]
                    },
                    {
                        "name": "Salto de skater",
                        "description": "Lateral y equilibrio",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "30s",
                        "image": "â›¸ï¸",
                        "instructions": ["Salto lateral alternado", "MantÃ©n equilibrio", "Brazos coordinados"]
                    },
                    {
                        "name": "Puente a una pierna",
                        "description": "GlÃºteos y isquios",
                        "sets": 3,
                        "reps": "10-12 por pierna",
                        "rest": "25s",
                        "image": "ðŸŒ‰",
                        "instructions": ["Acostado, una pierna elevada", "Eleva cadera", "MÃ¡xima contracciÃ³n glÃºtea"]
                    },
                    {
                        "name": "Donkey kicks izquierdo",
                        "description": "GlÃºteos especÃ­ficos",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "20s",
                        "image": "ðŸ¦µ",
                        "instructions": ["Cuadrupedia", "Eleva pierna izquierda atrÃ¡s", "Contrae glÃºteo"]
                    },
                    {
                        "name": "Donkey kicks derecho",
                        "description": "GlÃºteos especÃ­ficos",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "20s",
                        "image": "ðŸ¦µ",
                        "instructions": ["Cuadrupedia", "Eleva pierna derecha atrÃ¡s", "Contrae glÃºteo"]
                    }
                ]
            },
            "brazos": {
                "name": "Brazos",
                "exercises": [
                    {
                        "name": "Flexiones de brazos",
                        "description": "Para pectorales y trÃ­ceps",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "30s",
                        "image": "ðŸ’ª",
                        "instructions": ["MantÃ©n cuerpo recto", "Codos cerca del cuerpo", "Baja controladamente"]
                    }
                ]
            },
            "espalda": {
                "name": "Espalda",
                "exercises": [
                    {
                        "name": "Remo con banda",
                        "description": "Para dorsales",
                        "sets": 3,
                        "reps": "12-15 repeticiones",
                        "rest": "30s",
                        "image": "ðŸŽ¯",
                        "instructions": ["Tira de la banda hacia atrÃ¡s", "Contrae dorsales", "MantÃ©n espalda recta"]
                    }
                ]
            }
        }
    },
    "estiramiento": {
        "name": "Rutina de Estiramiento", 
        "type": "estiramiento",
        "body_parts": {
            "full_body": {
                "name": "Estiramiento Completo",
                "exercises": [
                    {
                        "name": "Estiramiento de cuello",
                        "description": "Libera tensiÃ³n cervical",
                        "sets": 1,
                        "reps": "30 segundos por lado",
                        "rest": "10s",
                        "image": "ðŸ‘¤",
                        "instructions": ["Inclina cabeza suavemente", "MantÃ©n 30 segundos", "Alterna lados"]
                    }
                ]
            }
        }
    },
    "calentamiento": {
        "name": "Calentamiento General",
        "type": "calentamiento", 
        "body_parts": {
            "full_body": {
                "name": "Calentamiento Completo",
                "exercises": [
                    {
                        "name": "RotaciÃ³n de hombros",
                        "description": "Prepara articulaciones",
                        "sets": 1,
                        "reps": "30 segundos",
                        "rest": "5s",
                        "image": "ðŸ”„",
                        "instructions": ["Rota hombros hacia adelante", "Luego hacia atrÃ¡s", "Movimiento controlado"]
                    }
                ]
            }
        }
    },
    "cardio": {
        "name": "Entrenamiento Cardiovascular",
        "type": "cardio",
        "body_parts": {
            "full_body": {
                "name": "Cardio Completo",
                "exercises": [
                    {
                        "name": "Correr en el lugar",
                        "description": "Ejercicio cardiovascular bÃ¡sico",
                        "sets": 3,
                        "reps": "60 segundos",
                        "rest": "30s",
                        "image": "ðŸƒâ€â™‚ï¸",
                        "instructions": ["Correr elevando rodillas", "Mantener ritmo constante", "Respirar profundamente"]
                    }
                ]
            }
        }
    },
    "hiit": {
        "name": "Entrenamiento HIIT",
        "type": "hiit",
        "body_parts": {
            "full_body": {
                "name": "HIIT Completo",
                "exercises": [
                    {
                        "name": "Burpees",
                        "description": "Ejercicio completo de cuerpo entero",
                        "sets": 4,
                        "reps": "12-15 repeticiones",
                        "rest": "45s",
                        "image": "ðŸ’¥",
                        "instructions": ["PosiciÃ³n de pie", "Agacharse y apoyar manos", "Salto hacia atrÃ¡s", "FlexiÃ³n", "Salto hacia adelante", "Salto vertical"]
                    }
                ]
            }
        }
    },
    "yoga": {
        "name": "SesiÃ³n de Yoga",
        "type": "yoga",
        "body_parts": {
            "flexibilidad": {
                "name": "Yoga para Flexibilidad",
                "exercises": [
                    {
                        "name": "Saludo al Sol",
                        "description": "Secuencia clÃ¡sica de yoga",
                        "sets": 3,
                        "reps": "5 repeticiones",
                        "rest": "15s",
                        "image": "â˜€ï¸",
                        "instructions": ["Secuencia completa de 12 posturas", "Mantener respiraciÃ³n consciente", "Fluir entre posturas"]
                    }
                ]
            }
        }
    }
}

# ===============================
# FUNCIONES AUXILIARES PARA SALUD
# ===============================
def get_health_score_from_activity_level(activity_level):
    if activity_level <= 2:
        return 1
    elif activity_level <= 4:
        return 2
    elif activity_level <= 6:
        return 3
    elif activity_level <= 8:
        return 4
    else:
        return 5

def get_health_description(health_score):
    descriptions = {
        1: "Actividad baja â€¢ Se recomienda aumentar ejercicio gradualmente",
        2: "Actividad media-baja â€¢ Buen comienzo, sigue progresando",
        3: "Actividad intermedia â€¢ Manteniendo buen ritmo de ejercicio",
        4: "Actividad alta â€¢ Excelente condiciÃ³n fÃ­sica",
        5: "Actividad muy alta â€¢ Nivel atlÃ©tico excepcional"
    }
    return descriptions.get(health_score, "Estado normal â€¢ Manteniendo ritmo")

# ===============================
# ALMACENAMIENTO DE OBJETIVOS
# ===============================
GOALS_FILE = "user_goals.json"

def load_user_goals(username):
    """Carga los objetivos del usuario desde el archivo"""
    if not os.path.exists(GOALS_FILE):
        print(f"ðŸ“‚ Archivo {GOALS_FILE} no encontrado, creando estructura vacÃ­a")
        return {"fitness": [], "health": []}
    
    try:
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            all_goals = json.load(f)
        
        print(f"âœ… Objetivos cargados desde archivo. Usuarios en archivo: {list(all_goals.keys())}")
        
        # Si el usuario existe en el archivo, devolver sus objetivos
        if username in all_goals:
            user_goals = all_goals.get(username, {"fitness": [], "health": []})
            print(f"ðŸ“Š Objetivos encontrados para {username}: {len(user_goals.get('fitness', []))} fitness, {len(user_goals.get('health', []))} health")
            return user_goals
        else:
            # Si el usuario no existe, crear estructura vacÃ­a
            print(f"ðŸ‘¤ Usuario {username} no encontrado en objetivos, creando estructura vacÃ­a")
            return {"fitness": [], "health": []}
            
    except json.JSONDecodeError as e:
        print(f"âŒ Error decodificando JSON en {GOALS_FILE}: {e}")
        # Si el archivo estÃ¡ corrupto, crear uno nuevo
        return {"fitness": [], "health": []}
    except Exception as e:
        print(f"âŒ Error cargando objetivos para {username}: {e}")
        return {"fitness": [], "health": []}

def save_user_goals(username, goals_data):
    """Guarda los objetivos del usuario en el archivo"""
    try:
        all_goals = {}
        if os.path.exists(GOALS_FILE):
            try:
                with open(GOALS_FILE, 'r', encoding='utf-8') as f:
                    all_goals = json.load(f)
                print(f"ðŸ“‚ Archivo existente cargado con {len(all_goals)} usuarios")
            except json.JSONDecodeError:
                print(f"âš ï¸ Archivo {GOALS_FILE} corrupto, creando nuevo")
                all_goals = {}
        
        # Validar que goals_data tenga la estructura correcta
        if not isinstance(goals_data, dict):
            print(f"âŒ Error: goals_data no es un diccionario: {type(goals_data)}")
            goals_data = {"fitness": [], "health": []}
        
        # Asegurar que existan las claves fitness y health
        if "fitness" not in goals_data:
            goals_data["fitness"] = []
        if "health" not in goals_data:
            goals_data["health"] = []
        
        # Actualizar los objetivos del usuario
        all_goals[username] = goals_data
        
        # Guardar en archivo
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_goals, f, indent=2, ensure_ascii=False)
        
        print(f"âœ… Objetivos guardados para {username}: {len(goals_data.get('fitness', []))} fitness, {len(goals_data.get('health', []))} health")
        print(f"ðŸ“‹ Total usuarios en archivo: {len(all_goals)}")
        
        return True
    except Exception as e:
        print(f"âŒ Error guardando objetivos para {username}: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_user_goal(username, goal_type, goal_data):
    """AÃ±ade un nuevo objetivo para el usuario - VERSIÃ“N CORREGIDA"""
    print(f"ðŸŽ¯ Iniciando add_user_goal para {username}, tipo: {goal_type}")
    
    # Validar tipo de objetivo
    if goal_type not in ["fitness", "health"]:
        print(f"âŒ Tipo de objetivo invÃ¡lido: {goal_type}")
        return False
    
    # Cargar objetivos existentes
    goals = load_user_goals(username)
    print(f"ðŸ“Š Objetivos cargados: {len(goals.get('fitness', []))} fitness, {len(goals.get('health', []))} health")
    
    # Generar un ID Ãºnico para el objetivo
    import time
    import random
    goal_id = f"goal_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Crear objeto de objetivo completo con todos los campos necesarios
    complete_goal_data = {
        "id": goal_id,
        "name": goal_data.get("name", "Sin nombre"),
        "description": goal_data.get("description", ""),
        "target": goal_data.get("target", ""),
        "deadline": goal_data.get("deadline", "1_month"),
        "type": goal_data.get("type", goal_type),  # Mantener el tipo original si existe
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "progress": 0,
        "status": "active",
        "completed_at": None,
        "emoji": get_emoji_for_goal(goal_data.get("name", "Sin nombre"))
    }
    
    print(f"ðŸ“ Datos del objetivo a agregar:")
    print(f"   ID: {goal_id}")
    print(f"   Nombre: {complete_goal_data['name']}")
    print(f"   Tipo: {goal_type}")
    print(f"   DescripciÃ³n: {complete_goal_data['description'][:50]}...")
    
    # Agregar a la lista correcta
    if goal_type in goals:
        goals[goal_type].append(complete_goal_data)
        print(f"âœ… Objetivo agregado a lista {goal_type}")
    else:
        # Si la lista no existe, crearla
        goals[goal_type] = [complete_goal_data]
        print(f"âœ… Lista {goal_type} creada y objetivo agregado")
    
    # Guardar los objetivos actualizados
    if save_user_goals(username, goals):
        print(f"âœ… Objetivo '{complete_goal_data['name']}' agregado exitosamente para {username} (ID: {goal_id})")
        
        # Verificar que se guardÃ³ correctamente
        saved_goals = load_user_goals(username)
        print(f"ðŸ“‹ VerificaciÃ³n: {len(saved_goals.get(goal_type, []))} objetivos en {goal_type} despuÃ©s de guardar")
        
        return True
    else:
        print(f"âŒ Error guardando objetivo para {username}")
        return False

def mark_goal_completed(username, goal_id):
    """Marca un objetivo como completado"""
    print(f"ðŸŽ¯ Marcando objetivo como completado: usuario={username}, goal_id={goal_id}")
    
    goals = load_user_goals(username)
    print(f"ðŸ“Š Objetivos cargados para bÃºsqueda: {len(goals.get('fitness', []))} fitness, {len(goals.get('health', []))} health")
    
    # Buscar el objetivo en ambas listas
    for goal_type in ["fitness", "health"]:
        for goal in goals.get(goal_type, []):
            if goal.get("id") == goal_id:
                print(f"âœ… Objetivo encontrado en {goal_type}: {goal.get('name', 'Sin nombre')}")
                goal["status"] = "completed"
                goal["progress"] = 100
                goal["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if save_user_goals(username, goals):
                    print(f"âœ… Objetivo {goal_id} marcado como completado para {username}")
                    return True
                else:
                    print(f"âŒ Error guardando objetivo completado")
                    return False
    
    print(f"âŒ Objetivo {goal_id} no encontrado para {username}")
    return False

def delete_user_goal(username, goal_id):
    """Elimina un objetivo por su ID"""
    print(f"ðŸ—‘ï¸ Eliminando objetivo: usuario={username}, goal_id={goal_id}")
    
    goals = load_user_goals(username)
    
    # Buscar y eliminar en ambas listas (fitness y health)
    for goal_type in ["fitness", "health"]:
        for i, goal in enumerate(goals.get(goal_type, [])):
            if goal.get("id") == goal_id:
                deleted_name = goal.get("name", "Sin nombre")
                print(f"âœ… Objetivo encontrado para eliminar: '{deleted_name}' en {goal_type}")
                
                # Eliminar el objetivo
                goals[goal_type].pop(i)
                
                # Guardar los cambios
                if save_user_goals(username, goals):
                    print(f"ðŸ—‘ï¸ Objetivo '{deleted_name}' ({goal_id}) eliminado exitosamente para {username}")
                    return True
                else:
                    print(f"âŒ Error guardando despuÃ©s de eliminar objetivo")
                    return False
    
    print(f"âŒ Objetivo {goal_id} no encontrado para eliminaciÃ³n")
    return False

def get_user_goals_for_display(username):
    """Obtiene objetivos formateados para mostrar en la interfaz"""
    print(f"ðŸŽ¯ Obteniendo objetivos para mostrar: {username}")
    
    goals = load_user_goals(username)
    
    # Formatear objetivos de fitness
    fitness_goals_formatted = []
    for goal in goals.get("fitness", []):
        goal_data = {
            "id": goal.get("id", f"goal_unknown_{len(fitness_goals_formatted)}"),
            "name": goal.get("name", "Objetivo sin nombre"),
            "target": goal.get("target", ""),
            "progress": goal.get("progress", 0),
            "status": goal.get("status", "active"),
            "emoji": goal.get("emoji", get_emoji_for_goal(goal.get("name", ""))),
            "description": goal.get("description", ""),
            "deadline": goal.get("deadline", ""),
            "created_at": goal.get("created_at", ""),
            "completed_at": goal.get("completed_at", "")
        }
        fitness_goals_formatted.append(goal_data)
    
    # Formatear objetivos de salud
    health_goals_formatted = []
    for goal in goals.get("health", []):
        goal_data = {
            "id": goal.get("id", f"goal_unknown_{len(health_goals_formatted)}"),
            "name": goal.get("name", "Objetivo sin nombre"),
            "target": goal.get("target", ""),
            "progress": goal.get("progress", 0),
            "status": goal.get("status", "active"),
            "emoji": goal.get("emoji", get_emoji_for_goal(goal.get("name", ""))),
            "description": goal.get("description", ""),
            "deadline": goal.get("deadline", ""),
            "created_at": goal.get("created_at", ""),
            "completed_at": goal.get("completed_at", "")
        }
        health_goals_formatted.append(goal_data)
    
    print(f"ðŸ“Š Objetivos formateados para {username}: {len(fitness_goals_formatted)} fitness, {len(health_goals_formatted)} health")
    
    return {
        "fitness": fitness_goals_formatted,
        "health": health_goals_formatted
    }

def get_emoji_for_goal(goal_name):
    """Devuelve un emoji basado en el nombre del objetivo"""
    goal_lower = goal_name.lower()
    
    emoji_map = {
        "peso": "ðŸ“‰",
        "correr": "ðŸƒ",
        "velocidad": "âš¡",
        "resistencia": "ðŸ«",
        "fuerza": "ðŸ’ª",
        "flexibilidad": "ðŸ§˜",
        "cardio": "ðŸ’“",
        "frecuencia": "â¤ï¸",
        "fc": "â¤ï¸",
        "hrv": "ðŸ“Š",
        "recuperaciÃ³n": "ðŸ”„",
        "alimentaciÃ³n": "ðŸŽ",
        "nutriciÃ³n": "ðŸ¥—",
        "sueÃ±o": "ðŸ˜´",
        "agua": "ðŸ’§",
        "hidrataciÃ³n": "ðŸ’§",
        "calorÃ­as": "ðŸ”¥",
        "proteÃ­na": "ðŸ¥©",
        "carbohidrato": "ðŸž",
        "grasa": "ðŸ¥‘",
        "fruta": "ðŸŽ",
        "verdura": "ðŸ¥¦",
        "ejercicio": "ðŸ’ª",
        "deporte": "âš½",
        "yoga": "ðŸ§˜",
        "meditaciÃ³n": "ðŸ§˜â€â™€ï¸",
        "estrÃ©s": "ðŸ˜¥",
        "ansiedad": "ðŸ˜°"
    }
    
    for keyword, emoji in emoji_map.items():
        if keyword in goal_lower:
            return emoji
    
    return "ðŸŽ¯"  # Emoji por defecto

# FunciÃ³n auxiliar para debug
def print_all_goals():
    """Imprime todos los objetivos del archivo para debugging"""
    if not os.path.exists(GOALS_FILE):
        print("ðŸ“‚ Archivo user_goals.json no existe")
        return
    
    try:
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            all_goals = json.load(f)
        
        print("\n" + "="*60)
        print("DEBUG: CONTENIDO COMPLETO DE user_goals.json")
        print("="*60)
        
        for username, goals in all_goals.items():
            print(f"\nðŸ‘¤ Usuario: {username}")
            print(f"  Fitness: {len(goals.get('fitness', []))} objetivos")
            for goal in goals.get('fitness', []):
                print(f"    - {goal.get('name', 'Sin nombre')} (ID: {goal.get('id', 'Sin ID')})")
            
            print(f"  Health: {len(goals.get('health', []))} objetivos")
            for goal in goals.get('health', []):
                print(f"    - {goal.get('name', 'Sin nombre')} (ID: {goal.get('id', 'Sin ID')})")
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"âŒ Error leyendo archivo para debug: {e}")

# ===============================
# FUNCIONES AUXILIARES PARA NUTRICIÃ“N
# ===============================

def estimate_nutrients_from_description(description):
    """Estima macronutrientes basados en la descripciÃ³n de la comida"""
    description_lower = description.lower()
    
    # Inicializar valores base
    carbs = 0
    protein = 0
    fat = 0
    calories = 0
    
    # Palabras clave y sus valores estimados
    food_keywords = {
        'avena': {'carbs': 25, 'protein': 5, 'fat': 3, 'calories': 150},
        'frutas': {'carbs': 15, 'protein': 1, 'fat': 0, 'calories': 60},
        'nueces': {'carbs': 5, 'protein': 4, 'fat': 15, 'calories': 180},
        'cafÃ©': {'carbs': 0, 'protein': 0, 'fat': 0, 'calories': 2},
        'ensalada': {'carbs': 10, 'protein': 3, 'fat': 2, 'calories': 70},
        'pollo': {'carbs': 0, 'protein': 25, 'fat': 5, 'calories': 165},
        'quinoa': {'carbs': 20, 'protein': 4, 'fat': 2, 'calories': 120},
        'vegetales': {'carbs': 10, 'protein': 2, 'fat': 0, 'calories': 50},
        'salmÃ³n': {'carbs': 0, 'protein': 22, 'fat': 13, 'calories': 206},
        'espÃ¡rragos': {'carbs': 3, 'protein': 2, 'fat': 0, 'calories': 20},
        'brÃ³coli': {'carbs': 6, 'protein': 2, 'fat': 0, 'calories': 30},
        'batido proteÃ­na': {'carbs': 5, 'protein': 25, 'fat': 3, 'calories': 150},
        'manzana': {'carbs': 25, 'protein': 0, 'fat': 0, 'calories': 95},
        'yogur griego': {'carbs': 6, 'protein': 10, 'fat': 5, 'calories': 120},
        'almendras': {'carbs': 6, 'protein': 6, 'fat': 14, 'calories': 160},
        'arroz': {'carbs': 45, 'protein': 4, 'fat': 1, 'calories': 205},
        'pasta': {'carbs': 40, 'protein': 8, 'fat': 2, 'calories': 210},
        'huevos': {'carbs': 1, 'protein': 6, 'fat': 5, 'calories': 78},
        'pan': {'carbs': 15, 'protein': 3, 'fat': 1, 'calories': 80},
        'queso': {'carbs': 1, 'protein': 7, 'fat': 9, 'calories': 113},
        'leche': {'carbs': 12, 'protein': 8, 'fat': 5, 'calories': 120},
        'plÃ¡tano': {'carbs': 27, 'protein': 1, 'fat': 0, 'calories': 105},
        'zanahoria': {'carbs': 9, 'protein': 1, 'fat': 0, 'calories': 41},
        'tomate': {'carbs': 4, 'protein': 1, 'fat': 0, 'calories': 22},
        'aguacate': {'carbs': 9, 'protein': 2, 'fat': 15, 'calories': 160},
        'pavo': {'carbs': 0, 'protein': 29, 'fat': 7, 'calories': 189},
        'ternera': {'carbs': 0, 'protein': 26, 'fat': 17, 'calories': 250},
        'pescado': {'carbs': 0, 'protein': 22, 'fat': 10, 'calories': 180},
        'legumbres': {'carbs': 20, 'protein': 9, 'fat': 1, 'calories': 130},
        'lentejas': {'carbs': 20, 'protein': 9, 'fat': 0, 'calories': 116}
    }
    
    # Buscar palabras clave en la descripciÃ³n
    for keyword, values in food_keywords.items():
        if keyword in description_lower:
            carbs += values['carbs']
            protein += values['protein']
            fat += values['fat']
            calories += values['calories']
    
    # Si no se encontraron palabras clave, usar valores por defecto basados en el tipo
    if calories == 0:
        # EstimaciÃ³n basada en el tamaÃ±o de la descripciÃ³n
        word_count = len(description.split())
        if word_count <= 3:
            calories = 200
            carbs = 25
            protein = 10
            fat = 8
        elif word_count <= 6:
            calories = 350
            carbs = 40
            protein = 15
            fat = 12
        else:
            calories = 500
            carbs = 60
            protein = 25
            fat = 18
    
    return {
        'carbs': carbs,
        'protein': protein,
        'fat': fat,
        'calories': calories
    }

def save_user_meal(username, meal_data):
    """Guarda una comida en el archivo de comidas del usuario"""
    MEALS_FILE = f"meals_{username}.json"
    
    try:
        # Cargar comidas existentes
        meals = []
        if os.path.exists(MEALS_FILE):
            with open(MEALS_FILE, 'r', encoding='utf-8') as f:
                meals = json.load(f)
        
        # Agregar nueva comida con ID y timestamp
        meal_data['id'] = f"meal_{int(datetime.now().timestamp())}"
        meal_data['date'] = datetime.now().strftime("%Y-%m-%d")
        meal_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        meals.append(meal_data)
        
        # Guardar
        with open(MEALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(meals, f, indent=2, ensure_ascii=False)
        
        print(f"âœ… Comida guardada para {username}: {meal_data.get('type', 'sin tipo')}")
        return True
    except Exception as e:
        print(f"âŒ Error guardando comida: {e}")
        return False

def load_user_meals(username):
    """Carga las comidas del usuario"""
    MEALS_FILE = f"meals_{username}.json"
    
    if not os.path.exists(MEALS_FILE):
        return []
    
    try:
        with open(MEALS_FILE, 'r', encoding='utf-8') as f:
            meals = json.load(f)
        print(f"ðŸ“‹ Comidas cargadas para {username}: {len(meals)} comidas")
        return meals
    except Exception as e:
        print(f"âŒ Error cargando comidas para {username}: {e}")
        return []

def calculate_daily_totals(meals):
    """Calcula los totales diarios de nutriciÃ³n"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_meals = [meal for meal in meals if meal.get('date') == today]
    
    totals = {
        'calories': 0,
        'carbs': 0,
        'protein': 0,
        'fat': 0
    }
    
    for meal in today_meals:
        totals['calories'] += meal.get('calories', 0)
        totals['carbs'] += meal.get('carbs', 0)
        totals['protein'] += meal.get('protein', 0)
        totals['fat'] += meal.get('fat', 0)
    
    print(f"ðŸ“Š Totales diarios calculados: {totals}")
    return totals

# ===============================
# FUNCIONES AUXILIARES PARA ENTRENAMIENTOS GUIADOS
# ===============================

def get_exercises_for_workout(workout_type, body_parts, duration):
    """Obtiene ejercicios adaptados a la duraciÃ³n seleccionada"""
    if workout_type != "fuerza" or "piernas" not in body_parts:
        return []
    
    # Todos los ejercicios de piernas
    all_exercises = GUIDED_WORKOUTS["fuerza"]["body_parts"]["piernas"]["exercises"].copy()
    
    # Ajustar segÃºn duraciÃ³n
    if duration == 15:
        # Ejercicios clave para 15 min (8 ejercicios)
        selected_indices = [0, 1, 2, 3, 6, 10, 13, 16]
        exercises = [all_exercises[i] for i in selected_indices]
        # Reducir series
        for exercise in exercises:
            if exercise['sets'] > 1:
                exercise['sets'] = max(1, exercise['sets'] - 1)
                
    elif duration == 30:
        # MÃ¡s ejercicios para 30 min (12 ejercicios)
        selected_indices = [0, 1, 2, 3, 4, 5, 6, 9, 10, 13, 16, 17]
        exercises = [all_exercises[i] for i in selected_indices]
        # Ajustar series ligeramente
        for exercise in exercises:
            if exercise['sets'] >= 3:
                exercise['sets'] = 2
        
    elif duration == 45:
        # Casi todos los ejercicios para 45 min (15 ejercicios)
        selected_indices = list(range(len(all_exercises)))[:-2]
        exercises = [all_exercises[i] for i in selected_indices]
        
    else:  # 60 min
        # Todos los ejercicios
        exercises = all_exercises.copy()
    
    # Calcular tiempo estimado por ejercicio
    warmup_time = 180  # 3 minutos de calentamiento
    available_time = (duration * 60) - warmup_time
    
    # Distribuir tiempo entre ejercicios
    base_time_per_exercise = available_time // len(exercises) if exercises else 0
    
    for i, exercise in enumerate(exercises):
        # Ajustar tiempo basado en sets y complejidad
        if "salto" in exercise['name'].lower() or "explosiv" in exercise['description'].lower():
            time_multiplier = 1.3
        elif "estiramiento" in exercise['name'].lower() or "calentamiento" in exercise['name'].lower():
            time_multiplier = 0.7
        else:
            time_multiplier = 1.0
            
        exercise['duration'] = int(base_time_per_exercise * time_multiplier)
        exercise['duration'] = max(40, min(exercise['duration'], 120))  # Entre 40s y 2min
    
    print(f"ðŸ“Š Ejercicios generados: {len(exercises)} ejercicios para {duration} minutos")
    return exercises

def create_exercise_content(exercise, current_index, total_exercises, time_remaining=0):
    """Crea el contenido para mostrar un ejercicio"""
    if time_remaining == 0:
        time_remaining = exercise.get('duration', 60)
    
    minutes = time_remaining // 60
    seconds = time_remaining % 60
    timer_text = f"{minutes:02d}:{seconds:02d}"
    
    return html.Div([
        # Progreso general
        html.Div(
            f"Ejercicio {current_index + 1} de {total_exercises}",
            style={
                'color': HIGHLIGHT_COLOR,
                'fontSize': '1.2rem',
                'fontWeight': '600',
                'marginBottom': '20px',
                'fontFamily': "'Inter', sans-serif"
            }
        ),
        
        # Temporizador
        html.Div(
            timer_text,
            id="exercise-timer",
            style={
                'fontSize': '3.5rem',
                'fontWeight': '700',
                'color': HIGHLIGHT_COLOR,
                'marginBottom': '30px',
                'fontFamily': "'Inter', sans-serif",
                'textShadow': f'0 0 10px {HIGHLIGHT_COLOR}'
            }
        ),
        
        # Emoji del ejercicio
        html.Div(
            exercise['image'],
            style={
                'fontSize': '5rem', 
                'marginBottom': '25px',
                'filter': 'drop-shadow(0 0 10px rgba(0, 212, 255, 0.5))'
            }
        ),
        
        # Nombre del ejercicio
        html.H3(
            exercise['name'],
            style={
                'color': '#fff',
                'fontSize': '2rem',
                'marginBottom': '15px',
                'fontFamily': "'Inter', sans-serif",
                'fontWeight': '700'
            }
        ),
        
        # DescripciÃ³n
        html.P(
            exercise['description'],
            style={
                'color': '#ccc',
                'fontSize': '1.2rem',
                'marginBottom': '25px',
                'fontFamily': "'Inter', sans-serif",
                'maxWidth': '500px',
                'marginLeft': 'auto',
                'marginRight': 'auto',
                'lineHeight': '1.5'
            }
        ),
        
        # Series y repeticiones
        html.Div(
            [
                html.Div(
                    f"ðŸ‹ï¸ Series: {exercise['sets']}",
                    style={
                        'display': 'inline-block',
                        'marginRight': '25px',
                        'padding': '12px 20px',
                        'backgroundColor': 'rgba(0, 212, 255, 0.15)',
                        'borderRadius': '12px',
                        'color': HIGHLIGHT_COLOR,
                        'fontWeight': '600',
                        'fontSize': '1.1rem'
                    }
                ),
                html.Div(
                    f"ðŸ”„ Repeticiones: {exercise['reps']}",
                    style={
                        'display': 'inline-block',
                        'padding': '12px 20px',
                        'backgroundColor': 'rgba(0, 212, 255, 0.15)',
                        'borderRadius': '12px',
                        'color': HIGHLIGHT_COLOR,
                        'fontWeight': '600',
                        'fontSize': '1.1rem'
                    }
                )
            ],
            style={'marginBottom': '30px'}
        ),
        
        # Instrucciones
        html.Div(
            [
                html.H4(
                    "ðŸ“‹ Instrucciones:",
                    style={
                        'color': HIGHLIGHT_COLOR,
                        'marginBottom': '20px',
                        'fontFamily': "'Inter', sans-serif",
                        'fontSize': '1.3rem'
                    }
                ),
                html.Ul([
                    html.Li(
                        instruction,
                        style={
                            'color': '#ccc',
                            'marginBottom': '12px',
                            'textAlign': 'left',
                            'fontFamily': "'Inter', sans-serif",
                            'fontSize': '1.1rem',
                            'lineHeight': '1.6',
                            'paddingLeft': '10px'
                        }
                    ) for instruction in exercise['instructions']
                ],
                style={
                    'maxWidth': '500px',
                    'marginLeft': 'auto',
                    'marginRight': 'auto',
                    'textAlign': 'left'
                })
            ],
            style={'marginBottom': '30px'}
        ),
        
        # Barra de progreso del ejercicio
        html.Div(
            html.Div(
                id="exercise-progress-bar",
                style={
                    'width': '0%',
                    'height': '10px',
                    'backgroundColor': HIGHLIGHT_COLOR,
                    'borderRadius': '5px',
                    'transition': 'width 1s linear',
                    'boxShadow': f'0 0 10px {HIGHLIGHT_COLOR}'
                }
            ),
            style={
                'width': '100%',
                'height': '10px',
                'backgroundColor': '#2b2b2b',
                'borderRadius': '5px',
                'marginBottom': '20px'
            }
        ),
        
        # Tiempo de descanso (si aplica)
        html.Div(
            f"â±ï¸ Descanso: {exercise['rest']}",
            id="rest-time-indicator",
            style={
                'color': '#ffd166',
                'fontSize': '1.1rem',
                'fontWeight': '500',
                'fontFamily': "'Inter', sans-serif",
                'opacity': '0.8'
            }
        )
    ])

# ===============================
# PROCESAMIENTO ECG 
# ===============================
def find_peaks_simple(signal, min_distance=50, threshold=0.3):
    peaks = []
    signal_length = len(signal)
    
    if threshold is None:
        threshold = np.mean(signal) + 0.5 * np.std(signal)
    
    for i in range(min_distance, signal_length - min_distance):
        is_peak = True
        for j in range(1, min_distance):
            if (i - j >= 0 and signal[i] <= signal[i - j]) or \
               (i + j < signal_length and signal[i] <= signal[i + j]):
                is_peak = False
                break
        
        if is_peak and signal[i] > threshold:
            if not peaks or (i - peaks[-1]) >= min_distance:
                peaks.append(i)
    
    return np.array(peaks)

def load_ecg_and_compute_bpm(filepath="ecg_example.csv"):
    try:
        import os
        if not os.path.exists(filepath):
            print(f"Archivo {filepath} no encontrado, generando datos de ejemplo...")
            # Generar datos de ejemplo mÃ¡s realistas
            t_example = np.linspace(0, 10, 1000)
            # Crear una seÃ±al ECG mÃ¡s realista con picos R
            ecg_example = np.zeros_like(t_example)
            
            # Frecuencia cardÃ­aca de ~72 BPM = 1.2 Hz
            heart_rate = 1.2  
            
            for i, t in enumerate(t_example):
                # Onda P
                if i % 83 < 10:  # Cada ~83 puntos para 72 BPM
                    ecg_example[i] += 0.25 * np.sin(2 * np.pi * 5 * t)
                # Complejo QRS (pico R)
                if i % 83 == 41:  # Pico R en el medio
                    ecg_example[i] += 1.5
                # Onda T
                if 45 <= i % 83 < 65:
                    ecg_example[i] += 0.3 * np.sin(2 * np.pi * 2 * (t - 0.5))
            
            # Agregar algo de ruido
            ecg_example += 0.1 * np.random.normal(size=len(ecg_example))
            
            # Encontrar picos (cada ~83 puntos para 72 BPM)
            peaks = np.array([i for i in range(41, 1000, 83) if i < len(ecg_example)])
            bpm = 72
            
            return t_example, ecg_example, bpm, peaks
        
        # CARGAR TU ARCHIVO CSV REAL
        df = pd.read_csv(filepath)
        
        print(f"Archivo cargado: {len(df)} puntos de datos")
        print(f"Columnas: {df.columns.tolist()}")
        
        if "Time" not in df.columns or "ECG" not in df.columns:
            print("ERROR: El archivo CSV no tiene las columnas 'Time' y 'ECG'")
            raise ValueError("Columnas requeridas no encontradas")
            
        t = df["Time"].values
        ecg = df["ECG"].values

        print(f"Rango de tiempo: {t[0]:.2f} a {t[-1]:.2f} segundos")
        print(f"Rango de ECG: {np.min(ecg):.4f} a {np.max(ecg):.4f}")

        # Procesamiento de seÃ±al - NORMALIZAR para mejor detecciÃ³n
        ecg_clean = ecg - np.mean(ecg)
        
        # Aplicar filtro pasa-banda simple para mejorar la seÃ±al
        from scipy import signal
        
        # DiseÃ±ar filtro pasa-banda (0.5-40 Hz tÃ­pico para ECG)
        fs = 1 / (t[1] - t[0]) if len(t) > 1 else 250  # Frecuencia de muestreo estimada
        nyquist = fs / 2
        
        # Filtro Butterworth pasa-banda
        lowcut = 0.5
        highcut = 40.0
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = signal.butter(3, [low, high], btype='band')
        ecg_filtered = signal.filtfilt(b, a, ecg_clean)
        
        # Normalizar la seÃ±al filtrada
        ecg_range = np.max(ecg_filtered) - np.min(ecg_filtered)
        if ecg_range > 0:
            ecg_normalized = (ecg_filtered - np.min(ecg_filtered)) / ecg_range
        else:
            ecg_normalized = ecg_filtered
        
        print(f"SeÃ±al normalizada - Rango: {np.min(ecg_normalized):.4f} a {np.max(ecg_normalized):.4f}")

        # Encontrar picos con parÃ¡metros optimizados
        min_distance = int(0.4 * fs)  # Al menos 400ms entre latidos (150 BPM mÃ¡ximo)
        threshold = np.percentile(ecg_normalized, 85)  # Usar percentil 85 como threshold
        
        print(f"ParÃ¡metros detecciÃ³n - Min distance: {min_distance}, Threshold: {threshold:.4f}")
        
        peaks = find_peaks_simple(ecg_normalized, min_distance=min_distance, threshold=threshold)

        print(f"Picos detectados: {len(peaks)}")

        # Calcular BPM
        if len(peaks) > 1:
            rr_intervals = np.diff(t[peaks])
            if len(rr_intervals) > 0 and np.mean(rr_intervals) > 0:
                bpm = 60 / np.mean(rr_intervals)
                print(f"BPM calculado: {bpm:.1f} (de {len(rr_intervals)} intervalos RR)")
            else:
                bpm = 72
                print("Usando BPM por defecto (72) - problemas con intervalos RR")
        else:
            bpm = 72
            print(f"Usando BPM por defecto (72) - solo {len(peaks)} picos detectados")

        return t, ecg_filtered, bpm, peaks
        
    except Exception as e:
        print(f"Error loading ECG: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback a datos de ejemplo
        t_example = np.linspace(0, 10, 1000)
        ecg_example = (
            np.sin(2 * np.pi * 1.2 * t_example) + 
            0.5 * np.sin(2 * np.pi * 5 * t_example) +
            0.3 * np.sin(2 * np.pi * 0.5 * t_example)
        )
        
        # Agregar picos R artificiales
        for i in range(41, 1000, 83):
            if i < len(ecg_example):
                ecg_example[i] += 2.0
                
        peaks = np.array([i for i in range(41, 1000, 83) if i < len(ecg_example)])
        return t_example, ecg_example, 72, peaks

# ===============================
# HTML INDEX STRING
# ===============================
app.index_string = f'''
<!DOCTYPE html>
<html>
<head>
    {{%metas%}}
    <title>{{%title%}}</title>
    {{%favicon%}}
    {{%css%}}
    <!-- Agregar Bootstrap Icons CDN -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    
    <!-- SCRIPT CLIENTSIDE PARA DEBUGGING -->
    <script>
        window.clientside = window.clientside || {{}};
        
        // FunciÃ³n para debugging de pÃ¡ginas
        window.clientside.get_current_page = function(pathname) {{
            console.log('ðŸ“± Current page:', pathname);
            return pathname;
        }}
        
        // FunciÃ³n para verificar elementos del DOM
        window.clientside.check_element_exists = function(elementId) {{
            const element = document.getElementById(elementId);
            const exists = element !== null;
            console.log(`ðŸ” Element ${{elementId}} exists: ${{exists}}`);
            return exists;
        }}
        
        // FunciÃ³n para prevenir errores de callbacks
        window.clientside.safe_callback_trigger = function() {{
            console.log('ðŸ›¡ï¸ Safe callback trigger activated');
            return true;
        }}
        
        // Inicializar cuando la pÃ¡gina carga
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('ðŸš€ Athletica app loaded');
        }});
    </script>
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;900&display=swap');
        
        html, body {{ 
            height: 100%; 
            margin: 0; 
            padding: 0; 
            font-family: 'Inter', sans-serif; 
            color: #fff; 
            background-color: {DARK_BACKGROUND}; 
        }}
        #page-content {{ animation: fadeIn 0.6s ease-out; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(15px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        .Select-control {{
            background-color: #2b2b2b !important;
            border: 1px solid #444 !important;
            color: white !important;
        }}

        .Select-menu-outer {{
            background-color: #2b2b2b !important;
            border: 1px solid #444 !important;
            color: white !important;
        }}

        .Select-value-label {{
            color: white !important;
        }}

        .Select-input > input {{
            color: white !important;
        }}

        .Select-placeholder {{
            color: #ccc !important;
        }}

        .Select-option {{
            background-color: #2b2b2b !important;
            color: white !important;
        }}

        .Select-option.is-focused {{
            background-color: #3a3a3a !important;
            color: white !important;
        }}

        .Select-option.is-selected {{
            background-color: rgba(0, 212, 255, 0.2) !important;
            color: {HIGHLIGHT_COLOR} !important;
        }}

        .dbc-row-selectable .Select-control {{
            background-color: #2b2b2b !important;
            border: 1px solid #444 !important;
            color: white !important;
        }}

        .welcome-container {{
            position: relative;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 40px 20px;
            overflow: hidden;
            background-color: {DARK_BACKGROUND};
        }}
        .header-content {{
            margin-bottom: 50px;
            max-width: 800px;
            position: relative;
            z-index: 10;
        }}
        .logo-placeholder {{
            width: 80px; height: 80px; 
            margin: 0 auto 15px;
            background-color: rgba(0, 212, 255, 0.1); 
            border-radius: 50%;
            border: 2px solid {HIGHLIGHT_COLOR};
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 3rem;
            color: {HIGHLIGHT_COLOR};
        }}
        .main-title {{
            font-size: 4.8rem; 
            font-weight: 900;
            color: {HIGHLIGHT_COLOR};
            letter-spacing: 5px;
            text-shadow: 0 0 25px rgba(0, 224, 255, 0.7), 0 0 5px {HIGHLIGHT_COLOR};
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 1.25rem; 
            color: #ccc;
            margin-bottom: 30px;
            font-weight: 500;
        }}

        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            max-width: 1000px;
            width: 100%;
            margin: 0 auto 50px;
            position: relative;
        }}
        .feature-card {{
            background: #141414; 
            border-radius: 18px;
            padding: 30px;
            transition: all 0.3s ease;
            text-align: left;
            border: 1px solid rgba(0, 212, 255, 0.1); 
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
            height: 100%;
        }}
        .feature-card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2); 
            background: #1c1c1c;
        }}
        .icon {{ 
            font-size: 2.5rem; 
            color: {HIGHLIGHT_COLOR}; 
            margin-bottom: 15px; 
        }}
        .card-title {{ 
            font-size: 1.3rem;
            font-weight: 700; 
            color: white; 
            margin-bottom: 8px; 
        }}
        .card-text {{ 
            font-size: 1rem; 
            color: #a0a0a0; 
            margin: 0; 
            font-weight: 300; 
            line-height: 1.5; 
        }}

        .button-section {{ margin-bottom: 20px; }}
        .btn-start, .dcc-link-button {{
            font-size: 1.1rem;
            padding: 14px 40px;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            text-decoration: none !important;
            display: inline-block;
        }}
        .btn-primary-action {{
            background: {HIGHLIGHT_COLOR};
            color: #0b0b0b !important;
            border: 2px solid {HIGHLIGHT_COLOR};
        }}
        .btn-primary-action:hover {{
            background: #00b4d8;
            color: #000;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 224, 255, 0.5);
        }}
        .btn-secondary-action {{
            background: transparent;
            color: {HIGHLIGHT_COLOR} !important;
            border: 2px solid {HIGHLIGHT_COLOR};
        }}
        .btn-secondary-action:hover {{
            background: rgba(0, 212, 255, 0.1);
            color: white !important;
            transform: translateY(-2px);
        }}
        .privacy {{ 
            margin-top: 20px; 
            font-size: 0.85rem; 
            color: #888; 
            font-weight: 300;
            background: rgba(0, 212, 255, 0.05); 
            padding: 10px 20px;
            border-radius: 50px;
            border: 1px solid rgba(0, 212, 255, 0.1);
        }}

       .auth-container {{
        height: auto;  /* Cambiado de 100vh a auto */
        min-height: 100vh;  /* AÃ±adido para asegurar altura mÃ­nima */
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: {DARK_BACKGROUND};
        padding: 40px 20px;  /* AÃ±adido padding */
    }}
    
    .auth-wrapper {{
    background-color: #1a1a1a;
    border-radius: 18px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9);
    width: 1200px;
    max-width: 95%;
    height: auto;
    min-height: 700px;
    max-height: 95vh;  /* Altura mÃ¡xima del 95% de la pantalla */
    display: flex;
    overflow: hidden;
    border: 1px solid rgba(0, 224, 255, 0.1);
}}

/* Estilos para la barra de scroll personalizada */
.auth-form-side::-webkit-scrollbar {{
    width: 8px;
}}

.auth-form-side::-webkit-scrollbar-track {{
    background: #1a1a1a;
    border-radius: 10px;
}}

.auth-form-side::-webkit-scrollbar-thumb {{
    background: rgba(0, 212, 255, 0.3);
    border-radius: 10px;
}}

.auth-form-side::-webkit-scrollbar-thumb:hover {{
    background: rgba(0, 212, 255, 0.5);
}}
    
   .auth-form-side {{
    width: 55%;
    padding: 60px 70px;
    display: flex;
    flex-direction: column;
    background-color: #1a1a1a;
    overflow-y: auto;  /* Mantener scroll */
    overflow-x: hidden; /* Evitar scroll horizontal */
    height: 100%; /* Usar altura completa */
}}

.auth-form-content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 600px; /* Altura mÃ­nima */
}}
    
    .auth-toggle-side {{
        width: 45%;
        background: linear-gradient(145deg, #004c7c, #0093e9); 
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 50px;
        text-align: center;
        transition: background 0.5s ease;
    }}

        .auth-form-side h2 {{
            margin-bottom: 2rem;
            color: #fff;
            font-weight: 700;
            letter-spacing: 1px;
            font-size: 2rem;
        }}
        .input-group {{
        position: relative;
        margin-bottom: 20px;
        width: 100%;
    }}
    
    .auth-input {{
        width: 100%;
        padding: 12px 40px 12px 40px;
        background-color: #2b2b2b;
        border: 1px solid #444;
        border-radius: 10px;
        color: white;
        font-size: 1rem;
        transition: border-color 0.3s;
        box-sizing: border-box;
    }}
        .auth-input:focus {{
            border-color: {HIGHLIGHT_COLOR};
            outline: none;
            box-shadow: 0 0 5px rgba(0, 224, 255, 0.5);
        }}
        .auth-btn {{
        width: 100%;
        background-color: {HIGHLIGHT_COLOR};
        border: none;
        font-weight: 600;
        padding: 14px;  /* Aumentado padding */
        border-radius: 10px;
        margin-top: 20px;
        transition: 0.3s;
        color: #0b0b0b;
        font-size: 1.1rem;
        cursor: pointer;
        box-sizing: border-box;
    }}
        .auth-btn:hover {{
            background-color: #00b4d8;
            box-shadow: 0 4px 15px rgba(0,212,255,0.4);
            transform: translateY(-2px);
        }}
        .auth-toggle-side h2 {{ font-size: 2.2rem; margin-bottom: 15px; font-weight: 700; }}
        .auth-toggle-side p {{ margin-bottom: 30px; opacity: 0.85; }}
        .toggle-btn-promo {{
            padding: 10px 30px;
            background-color: transparent;
            border: 2px solid white;
            color: white;
            border-radius: 50px;
            font-weight: bold;
            transition: background 0.3s ease;
        }}
        .toggle-btn-promo:hover {{
            background-color: rgba(255, 255, 255, 0.15);
        }}
        .forgot-password {{
            color: {HIGHLIGHT_COLOR};
            margin-top: 8px;
            font-size: 0.9rem;
            cursor: pointer;
            align-self: flex-start;
            text-decoration: none;
            transition: text-decoration 0.3s;
        }}
        .forgot-password:hover {{
            text-decoration: underline;
        }}
        .accept-terms {{ color: #ccc; margin-top: 10px; }}
        .dcc-link-button {{ 
            text-align: center;
        }}

        .onboarding-container {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: {DARK_BACKGROUND};
            padding: 30px 20px;
        }}
        .onboarding-card {{
            background-color: #1a1a1a;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9);
            width: 850px;
            max-width: 100%;
            padding: 40px;
            margin-top: 40px;
            border: 1px solid rgba(0, 224, 255, 0.1);
        }}
        .onboarding-header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .step-title {{
            color: {HIGHLIGHT_COLOR};
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .step-subtitle {{
            color: #ccc;
            font-size: 1.1rem;
            font-weight: 300;
        }}
        .progress-bar-container {{
            height: 8px;
            background: #2b2b2b;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #007c9c);
            transition: width 0.5s ease-in-out;
        }}
        .form-group-card {{
            background-color: #141414;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #2b2b2b;
        }}
        .radio-card-group {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .radio-card {{
            background: #2b2b2b;
            color: #ccc;
            padding: 20px 10px !important;
            border-radius: 10px;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
            border: 2px solid #2b2b2b;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 100px !important;
        }}
        .radio-card:hover {{
            border-color: #444;
            background: #3a3a3a;
        }}
        .radio-card-checked {{
            border-color: {HIGHLIGHT_COLOR};
            background: rgba(0, 212, 255, 0.1);
            color: {HIGHLIGHT_COLOR};
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
        }}
        .radio-card .bi {{
            font-size: 1.8rem !important;
            margin-bottom: 8px !important;
            display: block !important;
            color: inherit !important;
            transition: transform 0.2s ease !important;
        }}
        .radio-card:hover .bi {{
            transform: scale(1.1) !important;
        }}

        .onboarding-input {{
            background-color: #2b2b2b;
            border: 1px solid #444;
            border-radius: 10px;
            color: white; 
            padding: 12px;
            width: 100%;
            transition: border-color 0.3s;
        }}
        .onboarding-input:focus {{
            border-color: {HIGHLIGHT_COLOR};
            outline: none;
            box-shadow: 0 0 5px rgba(0, 224, 255, 0.5);
        }}
        
        @media (max-width: 768px) {{
            .main-title {{ font-size: 3rem; letter-spacing: 3px; }}
            .subtitle {{ font-size: 1rem; }}
            .welcome-container {{ padding: 20px; }}
            .header-content {{ margin-bottom: 30px; }}
            .auth-wrapper {{ height: auto; flex-direction: column; }}
            .auth-form-side, .auth-toggle-side {{ width: 100%; padding: 30px; }}
            .auth-toggle-side {{ order: -1; }} 
            .onboarding-card {{ padding: 20px; margin-top: 20px; }}
            .step-title {{ font-size: 2rem; }}
            .radio-card {{
                min-height: 80px !important;
                padding: 15px 8px !important;
            }}
            .radio-card .bi {{
                font-size: 1.5rem !important;
            }}
        }}
        
        /* Estilos adicionales para debugging */
        .debug-info {{
            position: fixed;
            bottom: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: #00ff00;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8rem;
            z-index: 9999;
            display: none;
        }}
    </style>
</head>
<body>
    <!-- Debug info (opcional, puedes comentarlo en producciÃ³n) -->
    <div class="debug-info" id="debug-info">
        Loading...
    </div>
    
    {{%app_entry%}}
    <footer>
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
    </footer>
    
    <!-- Script adicional para manejar errores de callbacks -->
    <script>
        // Interceptar errores de callbacks
        window.addEventListener('error', function(e) {{
            if (e.message && e.message.includes('nonexistent object') && e.message.includes('Input')) {{
                console.warn('âš ï¸ Error de callback interceptado:', e.message);
                // Prevenir que el error se propague
                e.preventDefault();
                e.stopPropagation();
                return false;
            }}
        }});
        
        // Verificar elementos periÃ³dicamente
        setInterval(function() {{
            const debugInfo = document.getElementById('debug-info');
            if (debugInfo) {{
                const path = window.location.pathname;
                debugInfo.textContent = `Page: ${{path}} | Time: ${{new Date().toLocaleTimeString()}}`;
                
                // Verificar elementos problemÃ¡ticos
                const problemElements = ['onboarding-next-btn-visual', 'onboarding-prev-btn-visual'];
                problemElements.forEach(id => {{
                    const el = document.getElementById(id);
                    if (el && path !== '/onboarding') {{
                        console.warn(`âš ï¸ Elemento ${{id}} existe en pÃ¡gina incorrecta: ${{path}}`);
                    }}
                }});
            }}
        }}, 5000);
        
        // FunciÃ³n para verificar si un elemento deberÃ­a existir
        function shouldElementExist(elementId, currentPath) {{
            const onboardingElements = ['onboarding-next-btn-visual', 'onboarding-prev-btn-visual', 'onboarding-content'];
            if (onboardingElements.includes(elementId)) {{
                return currentPath === '/onboarding';
            }}
            return true;
        }}
    </script>
</body>
</html>
'''
# ===============================
# CLIENTSIDE CALLBACKS SIMPLIFICADOS (SIN DUMMY)
# ===============================

# Callback clientside para prevenir errores de onboarding (botÃ³n siguiente)
app.clientside_callback(
    """
    function(n_clicks, pathname) {
        // Verificar que estamos en onboarding antes de procesar clics
        if (pathname !== '/onboarding') {
            console.warn('âš ï¸ Callback prevenido (next): no estamos en onboarding');
            return window.dash_clientside.no_update;
        }
        return n_clicks;
    }
    """,
    Output('onboarding-next-btn-visual', 'n_clicks', allow_duplicate=True),
    Input('onboarding-next-btn-visual', 'n_clicks'),
    State('url', 'pathname'),
    prevent_initial_call=True
)

# Callback clientside para prevenir errores de onboarding (botÃ³n anterior)
app.clientside_callback(
    """
    function(n_clicks, pathname) {
        if (pathname !== '/onboarding') {
            console.warn('âš ï¸ Callback prevenido (prev): no estamos en onboarding');
            return window.dash_clientside.no_update;
        }
        return n_clicks;
    }
    """,
    Output('onboarding-prev-btn-visual', 'n_clicks', allow_duplicate=True),
    Input('onboarding-prev-btn-visual', 'n_clicks'),
    State('url', 'pathname'),
    prevent_initial_call=True
)

# ===============================
# WELCOME LAYOUT
# ===============================
welcome_layout = html.Div(
    [
        html.Div(
            className="header-content",
            children=[
                html.H1("ATHLETICA", className="main-title"),
                html.H4("Tu guÃ­a definitiva para la salud y el bienestar. Transforma tus datos en hÃ¡bitos.", className="subtitle"),
            ]
        ),
        
        html.Div(
            [
                html.Div([
                    html.I(className="bi bi-calendar-check icon"), 
                    html.P("Seguimiento Inteligente de HÃ¡bitos", className="card-title"),
                    html.P("Registra tu actividad diaria, sueÃ±o y nutriciÃ³n. Recibe consejos para construir rutinas saludables.", className="card-text")
                ], className="feature-card"),

                html.Div([
                    html.I(className="bi bi-activity icon"),
                    html.P("Monitoreo de Bienestar y EnergÃ­a", className="card-title"),
                    html.P("Analiza tu rendimiento y niveles de fatiga para saber cuÃ¡ndo esforzarte y cuÃ¡ndo descansar.", className="card-text")
                ], className="feature-card"),

                html.Div([
                    html.I(className="bi bi-bar-chart-line icon"),
                    html.P("Reportes de Progreso Sencillos", className="card-title"),
                    html.P("Visualiza tu evoluciÃ³n en el tiempo con grÃ¡ficos fÃ¡ciles de entender. Celebra tus logros.", className="card-text")
                ], className="feature-card"),
            ],
            className="features-grid"
        ),

        html.Div(
            [
                dcc.Link(
                    dbc.Button("Comenzar", color="primary", className="btn-start btn-primary-action"),
                    href="/login",
                    className="mx-3 dcc-link-button"
                ),
                dcc.Link(
                    dbc.Button("Crear cuenta", color="secondary", className="btn-start btn-secondary-action"),
                    href="/register",
                    className="mx-3 dcc-link-button"
                ),
            ],
            className="button-section"
        ),

        html.P("Datos cifrados de extremo a extremo Â· Cumplimiento GDPR estricto", className="privacy"),
    ],
    className="welcome-container"
)

# ===============================
# LOGIN LAYOUT 
# ===============================
login_layout = html.Div(
    className="auth-container",
    children=[
        # DIVS DE DIAGNÃ“STICO (OCULTOS)
        html.Div(id="current-user-debug", style={"display": "none"}),
        html.Div(id="onboarding-completed-debug", style={"display": "none"}),
        
        html.Div(
            className="auth-wrapper",
            children=[
                html.Div(
                    className="auth-form-side",
                    children=[
                        html.H2("Iniciar SesiÃ³n"),
                        html.Div(className="input-group", children=[
                            html.Span(html.I(className="bi bi-person-fill"), className="input-icon"),
                            dcc.Input(
                                id="login-username", 
                                type="text", 
                                placeholder="Usuario o Email",
                                className="auth-input",
                                style={
                                    'width': '100%', 
                                    'padding': '12px 40px 12px 40px',
                                    'backgroundColor': '#2b2b2b',
                                    'border': '1px solid #444',
                                    'borderRadius': '10px',
                                    'color': 'white', 
                                    'fontSize': '1rem'
                                }
                            )
                        ]),
                        html.Div(className="input-group", children=[
                            html.Span(html.I(className="bi bi-lock-fill"), className="input-icon"),
                            dcc.Input(
                                id="login-password", 
                                type="password", 
                                placeholder="ContraseÃ±a",
                                className="auth-input",
                                style={
                                    'width': '100%', 
                                    'padding': '12px 40px 12px 40px',
                                    'backgroundColor': '#2b2b2b',
                                    'border': '1px solid #444',
                                    'borderRadius': '10px',
                                    'color': 'white', 
                                    'fontSize': '1rem'
                                }
                            ),
                        ]),
                        html.A("Â¿Olvidaste tu contraseÃ±a?", href="#", className="forgot-password"),
                        dbc.Button("Entrar a Athletica", id="login-btn", className="auth-btn"),
                        html.Div(id="login-message", className="text-warning mt-2"),
                    ]
                ),

                html.Div(
                    className="auth-toggle-side",
                    children=[
                        html.H2("Â¿AÃºn no te has unido?"),
                        html.P("RegÃ­strate para comenzar tu transformaciÃ³n con el anÃ¡lisis de rendimiento mÃ¡s avanzado."),
                        dcc.Link(
                            dbc.Button("Crear una cuenta", className="toggle-btn-promo"),
                            href="/register",
                            style={'text-decoration': 'none'}
                        ),
                    ]
                )
            ]
        )
    ]
)

# ===============================
# REGISTER LAYOUT (CON SCROLL VERTICAL)
# ===============================
register_layout = html.Div(
    className="auth-container",
    children=[
        html.Div(
            className="auth-wrapper",
            children=[
                # LADO IZQUIERDO: PromociÃ³n (sin scroll)
                html.Div(
                    className="auth-toggle-side",
                    children=[
                        html.H2("Â¡Bienvenido/a!"),
                        html.P("Si ya tienes una cuenta, inicia sesiÃ³n para continuar optimizando tu rendimiento."),
                        dcc.Link(
                            dbc.Button("Iniciar SesiÃ³n", className="toggle-btn-promo"),
                            href="/login",
                            style={'text-decoration': 'none'}
                        ),
                    ]
                ),

                # LADO DERECHO: Formulario de registro (CON SCROLL)
                html.Div(
                    className="auth-form-side",
                    children=[
                        # CONTENEDOR PRINCIPAL CON TODO EL FORMULARIO
                        html.Div(
                            style={
                                'width': '100%',
                                'minHeight': '600px'  # Altura mÃ­nima
                            },
                            children=[
                                html.H2("Crear Cuenta", style={'marginBottom': '30px'}),
                                
                                # SECCIÃ“N DE TIPO DE USUARIO
                                html.Div(
                                    style={
                                        'marginBottom': '30px',
                                        'border': '1px solid rgba(0, 212, 255, 0.2)',
                                        'borderRadius': '12px',
                                        'padding': '20px',
                                        'backgroundColor': 'rgba(0, 212, 255, 0.05)'
                                    },
                                    children=[
                                        html.P(
                                            "Tipo de Usuario",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'fontWeight': '600',
                                                'marginBottom': '20px',
                                                'textTransform': 'uppercase',
                                                'letterSpacing': '0.5px',
                                                'fontSize': '1rem'
                                            }
                                        ),
                                        
                                        # CONTENEDOR DE BOTONES LATERAL
                                        html.Div(
                                            style={
                                                'display': 'flex',
                                                'flexDirection': 'row',
                                                'gap': '15px',
                                                'justifyContent': 'center',
                                                'alignItems': 'center',
                                                'marginBottom': '15px'
                                            },
                                            children=[
                                                # BotÃ³n Atleta
                                                html.Button(
                                                    [
                                                        html.Div("ðŸƒ", style={'fontSize': '1.8rem', 'marginBottom': '8px'}),
                                                        html.Div([
                                                            html.H4("Atleta", style={'color': '#fff', 'marginBottom': '5px', 'fontSize': '1.1rem'}),
                                                            html.P("Monitoriza tu salud", 
                                                                   style={'color': '#ccc', 'fontSize': '0.85rem', 'margin': '0'})
                                                        ])
                                                    ],
                                                    id="btn-reg-type-athlete",
                                                    n_clicks=0,
                                                    style={
                                                        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                        'border': '2px solid rgba(0, 212, 255, 0.3)',
                                                        'borderRadius': '10px',
                                                        'padding': '15px',
                                                        'cursor': 'pointer',
                                                        'transition': 'all 0.3s ease',
                                                        'color': 'white',
                                                        'textAlign': 'center',
                                                        'flex': '1',
                                                        'minWidth': '140px',
                                                        'maxWidth': '160px',
                                                        'minHeight': '100px',
                                                        'display': 'flex',
                                                        'flexDirection': 'column',
                                                        'justifyContent': 'center',
                                                        'alignItems': 'center'
                                                    }
                                                ),
                                                
                                                # BotÃ³n MÃ©dico
                                                html.Button(
                                                    [
                                                        html.Div("ðŸ‘¨â€âš•ï¸", style={'fontSize': '1.8rem', 'marginBottom': '8px'}),
                                                        html.Div([
                                                            html.H4("MÃ©dico", style={'color': '#fff', 'marginBottom': '5px', 'fontSize': '1.1rem'}),
                                                            html.P("Accede a datos", 
                                                                   style={'color': '#ccc', 'fontSize': '0.85rem', 'margin': '0'})
                                                        ])
                                                    ],
                                                    id="btn-reg-type-doctor",
                                                    n_clicks=0,
                                                    style={
                                                        'backgroundColor': 'rgba(78, 205, 196, 0.1)',
                                                        'border': '2px solid rgba(78, 205, 196, 0.3)',
                                                        'borderRadius': '10px',
                                                        'padding': '15px',
                                                        'cursor': 'pointer',
                                                        'transition': 'all 0.3s ease',
                                                        'color': 'white',
                                                        'textAlign': 'center',
                                                        'flex': '1',
                                                        'minWidth': '140px',
                                                        'maxWidth': '160px',
                                                        'minHeight': '100px',
                                                        'display': 'flex',
                                                        'flexDirection': 'column',
                                                        'justifyContent': 'center',
                                                        'alignItems': 'center'
                                                    }
                                                )
                                            ]
                                        ),
                                        
                                        # Input oculto que almacena el valor real
                                        dcc.Input(
                                            id="reg-user-type",
                                            type="hidden",
                                            value="athlete"
                                        ),
                                        
                                        # Indicador de selecciÃ³n
                                        html.Div(
                                            id="reg-type-indicator",
                                            style={
                                                'marginTop': '15px',
                                                'padding': '8px 12px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                'borderRadius': '6px',
                                                'textAlign': 'center',
                                                'fontSize': '0.9rem',
                                                'color': HIGHLIGHT_COLOR
                                            },
                                            children="Seleccionado: Atleta"
                                        )
                                    ]
                                ),
                                
                                # FORMULARIO COMPLETO
                                html.Div(
                                    style={'width': '100%'},
                                    children=[
                                        # Nombre de Usuario
                                        html.Div(className="input-group", children=[
                                            html.Span(html.I(className="bi bi-person-fill"), className="input-icon"),
                                            dcc.Input(
                                                id="reg-username", 
                                                type="text", 
                                                placeholder="Nombre de Usuario",
                                                className="auth-input"
                                            )
                                        ]),
                                        
                                        # Email
                                        html.Div(className="input-group", children=[
                                            html.Span(html.I(className="bi bi-envelope-fill"), className="input-icon"),
                                            dcc.Input(
                                                id="reg-email", 
                                                type="email", 
                                                placeholder="Email",
                                                className="auth-input"
                                            )
                                        ]),
                                        
                                        # ContraseÃ±a
                                        html.Div(className="input-group", children=[
                                            html.Span(html.I(className="bi bi-lock-fill"), className="input-icon"),
                                            dcc.Input(
                                                id="reg-password", 
                                                type="password", 
                                                placeholder="ContraseÃ±a",
                                                className="auth-input"
                                            )
                                        ]),
                                        
                                        # Confirmar ContraseÃ±a
                                        html.Div(className="input-group", children=[
                                            html.Span(html.I(className="bi bi-lock-fill"), className="input-icon"),
                                            dcc.Input(
                                                id="reg-password2", 
                                                type="password", 
                                                placeholder="Confirmar ContraseÃ±a",
                                                className="auth-input"
                                            )
                                        ]),
                                        
                                        # Checkbox de tÃ©rminos y condiciones
                                        html.Div(className="input-group", children=[
                                            html.Div(
                                                style={
                                                    'display': 'flex',
                                                    'alignItems': 'center',
                                                    'marginTop': '10px',
                                                    'marginBottom': '20px'
                                                },
                                                children=[
                                                    dcc.Checklist(
                                                        id="accept-terms",
                                                        options=[{'label': 'Acepto los tÃ©rminos y condiciones', 'value': 'Acepto'}],
                                                        value=[],
                                                        style={'display': 'flex', 'alignItems': 'center'},
                                                        inputStyle={
                                                            'marginRight': '10px',
                                                            'width': '18px',
                                                            'height': '18px',
                                                            'cursor': 'pointer'
                                                        },
                                                        labelStyle={
                                                            'color': '#ccc',
                                                            'fontSize': '0.95rem',
                                                            'cursor': 'pointer'
                                                        }
                                                    )
                                                ]
                                            )
                                        ]),
                                        
                                        # BotÃ³n de registro
                                        dbc.Button(
                                            "Registrarse en Athletica", 
                                            id="register-btn", 
                                            className="auth-btn",
                                            style={
                                                'width': '100%',
                                                'backgroundColor': HIGHLIGHT_COLOR,
                                                'border': 'none',
                                                'fontWeight': '600',
                                                'padding': '14px',
                                                'borderRadius': '10px',
                                                'marginTop': '10px',
                                                'marginBottom': '20px',  # Espacio extra abajo
                                                'transition': '0.3s',
                                                'color': '#0b0b0b',
                                                'fontSize': '1.1rem'
                                            }
                                        ),
                                        
                                        # Mensaje de registro (con suficiente espacio)
                                        html.Div(
                                            id="register-message", 
                                            className="text-warning mt-2", 
                                            style={
                                                'marginTop': '15px',
                                                'marginBottom': '40px',  # Espacio extra para scroll
                                                'minHeight': '50px'  # Altura mÃ­nima
                                            }
                                        ),
                                        
                                        # ESPACIO EXTRA PARA ASEGURAR QUE HAY SCROLL
                                        html.Div(
                                            style={
                                                'height': '50px',
                                                'visibility': 'hidden'
                                            }
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# ===============================
# DOCTOR DASHBOARD LAYOUT
# ===============================
doctor_dashboard_layout = html.Div(
    id="doctor-container",
    className="doctor-container",
    style={
        'backgroundColor': DARK_BACKGROUND,
        'minHeight': '100vh',
        'color': 'white',
        'fontFamily': 'Inter, sans-serif'
    },
    children=[

        # ===============================
        # HEADER
        # ===============================
        html.Div(
            id="doctor-header",
            className="doctor-header",
            style={
                'backgroundColor': '#1a1a1a',
                'padding': '15px 40px',
                'borderBottom': '1px solid rgba(0, 212, 255, 0.1)',
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center'
            },
            children=[
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center'},
                    children=[
                        html.Div(
                            style={
                                'width': '40px',
                                'height': '40px',
                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                'borderRadius': '10px',
                                'border': f'2px solid {HIGHLIGHT_COLOR}',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginRight': '15px'
                            },
                            children=html.Span(
                                "A",
                                style={
                                    'color': HIGHLIGHT_COLOR,
                                    'fontWeight': 'bold',
                                    'fontSize': '1.2rem'
                                }
                            )
                        ),
                        html.H1(
                            "ATHLETICA",
                            style={
                                'color': HIGHLIGHT_COLOR,
                                'fontSize': '1.8rem',
                                'fontWeight': '900',
                                'letterSpacing': '2px',
                                'textShadow': '0 0 15px rgba(0, 224, 255, 0.5)',
                                'margin': '0'
                            }
                        )
                    ]
                ),

                html.Div(
                    style={
                        'flex': '1',
                        'height': '1px',
                        'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                        'margin': '0 30px'
                    }
                ),

                html.Div(
                    style={'display': 'flex', 'alignItems': 'center'},
                    children=[
                        html.Div(
                            style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'},
                            children=[
                                html.Div(
                                    id="doctor-profile-avatar",
                                    style={
                                        'width': '45px',
                                        'height': '45px',
                                        'backgroundColor': '#4ecdc4',
                                        'borderRadius': '50%',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.2rem'
                                    }
                                ),
                                html.Div(
                                    style={'textAlign': 'right'},
                                    children=[
                                        html.Div(
                                            id="doctor-profile-name",
                                            style={
                                                'fontWeight': '600',
                                                'fontSize': '1rem',
                                                'color': '#fff'
                                            }
                                        ),
                                        html.Div(
                                            "MÃ©dico",
                                            style={
                                                'fontSize': '0.8rem',
                                                'color': '#4ecdc4'
                                            }
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),

        # ===============================
        # BODY (SIDEBAR + MAIN)
        # ===============================
        html.Div(
            style={'display': 'flex'},
            children=[

                # ===============================
                # SIDEBAR
                # ===============================
                html.Div(
                    style={
                        'width': '300px',
                        'padding': '30px',
                        'borderRight': '1px solid rgba(0, 212, 255, 0.1)',
                        'backgroundColor': '#141414'
                    },
                    children=[

                        html.H4(
                            "NavegaciÃ³n MÃ©dico",
                            style={
                                'color': '#4ecdc4',
                                'marginBottom': '20px',
                                'fontSize': '1.1rem'
                            }
                        ),

                        html.Button(
                            "Dashboard",
                            id="nav-dashboard-doctor",
                            n_clicks=0,
                            style={
                                'width': '100%',
                                'padding': '12px',
                                'backgroundColor': 'rgba(78, 205, 196, 0.1)',
                                'borderRadius': '10px',
                                'border': 'none',
                                'color': '#4ecdc4',
                                'textAlign': 'left',
                                'marginBottom': '10px',
                                'fontFamily': "'Inter', sans-serif",
                                'cursor': 'pointer',
                                'transition': 'all 0.3s ease'
                            }
                        ),

                        html.Button(
                            "Mis Pacientes",
                            id="nav-pacientes-doctor",
                            n_clicks=0,
                            style={
                                'width': '100%',
                                'padding': '12px',
                                'backgroundColor': 'transparent',
                                'borderRadius': '10px',
                                'border': 'none',
                                'color': '#ccc',
                                'textAlign': 'left',
                                'marginBottom': '10px',
                                'fontFamily': "'Inter', sans-serif",
                                'cursor': 'pointer',
                                'transition': 'all 0.3s ease'
                            }
                        ),

                        html.Hr(style={'margin': '30px 0', 'borderColor': '#2b2b2b'}),

                        html.H4(
                            "Buscar Pacientes",
                            style={'color': HIGHLIGHT_COLOR, 'marginBottom': '15px'}
                        ),

                        dcc.Input(
                            id="doctor-search-input",
                            type="text",
                            placeholder="Nombre, usuario o email...",
                            style={
                                'width': '100%',
                                'padding': '12px 15px',
                                'backgroundColor': '#2b2b2b',
                                'border': '1px solid #444',
                                'borderRadius': '8px',
                                'color': 'white',
                                'fontSize': '1rem',
                                'fontFamily': "'Inter', sans-serif",
                                'marginBottom': '15px'
                            }
                        ),

                        html.Button(
                            "Buscar",
                            id="doctor-search-btn",
                            n_clicks=0,
                            style={
                                'width': '100%',
                                'padding': '12px',
                                'backgroundColor': HIGHLIGHT_COLOR,
                                'border': 'none',
                                'borderRadius': '8px',
                                'fontWeight': '600',
                                'color': '#0a0a0a',
                                'fontFamily': "'Inter', sans-serif",
                                'cursor': 'pointer',
                                'transition': 'all 0.3s ease',
                                'marginBottom': '20px'
                            }
                        ),

                        html.Div(
                            id="doctor-search-results", 
                            style={
                                'marginTop': '20px',
                                'maxHeight': '300px',
                                'overflowY': 'auto'
                            }
                        )
                    ]
                ),

                # ===============================
                # MAIN CONTENT
                # ===============================
                html.Div(
                    className="doctor-main",
                    style={
                        'flex': '1',
                        'padding': '40px',
                        'overflowY': 'auto'
                    },
                    children=[
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'marginBottom': '20px'
                            },
                            children=[
                                html.H2(
                                    "Panel de Control MÃ©dico",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'margin': '0',
                                        'fontSize': '2.2rem'
                                    }
                                ),
                                html.Div(
                                    children=f"Ãšltima actualizaciÃ³n: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                    style={'color': '#aaa', 'fontSize': '0.9rem'}
                                )
                            ]
                        ),

                        html.P(
                            "Bienvenido/a al panel de control mÃ©dico. AquÃ­ puedes gestionar tus pacientes, ver sus datos de salud y monitorizar su progreso.",
                            style={
                                'color': '#ccc', 
                                'fontSize': '1.1rem',
                                'marginBottom': '30px',
                                'maxWidth': '800px'
                            }
                        ),

                        # DespuÃ©s de la secciÃ³n de bÃºsqueda, agrega:
                        html.Hr(style={'margin': '30px 0', 'borderColor': '#2b2b2b'}),

                        # EstadÃ­sticas de pacientes
                        html.Div(
                            style={
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '10px',
                                'padding': '20px',
                                'marginBottom': '20px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                            },
                            children=[
                                html.H4(
                                    "ðŸ“Š EstadÃ­sticas de Pacientes", 
                                    style={
                                        'color': HIGHLIGHT_COLOR, 
                                        'marginBottom': '15px',
                                        'fontSize': '1.3rem'
                                    }
                                ),
                                html.Div(
                                    style={
                                        'display': 'grid',
                                        'gridTemplateColumns': 'repeat(4, 1fr)',
                                        'gap': '15px'
                                    },
                                    children=[
                                        html.Div(
                                            style={'textAlign': 'center'},
                                            children=[
                                                html.Div(
                                                    id="doctor-patient-count", 
                                                    style={
                                                        'fontSize': '1.8rem', 
                                                        'fontWeight': '700', 
                                                        'color': HIGHLIGHT_COLOR,
                                                        'marginBottom': '5px'
                                                    }
                                                ),
                                                html.Div("Total", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                            ]
                                        ),
                                        html.Div(
                                            style={'textAlign': 'center'},
                                            children=[
                                                html.Div(
                                                    id="doctor-active-patients-count", 
                                                    style={
                                                        'fontSize': '1.8rem', 
                                                        'fontWeight': '700', 
                                                        'color': '#4ecdc4',
                                                        'marginBottom': '5px'
                                                    }
                                                ),
                                                html.Div("Activos", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                            ]
                                        ),
                                        html.Div(
                                            style={'textAlign': 'center'},
                                            children=[
                                                html.Div(
                                                    id="doctor-avg-activity", 
                                                    style={
                                                        'fontSize': '1.8rem', 
                                                        'fontWeight': '700', 
                                                        'color': '#ffd166',
                                                        'marginBottom': '5px'
                                                    }
                                                ),
                                                html.Div("Actividad Prom.", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                            ]
                                        ),
                                        html.Div(
                                            style={'textAlign': 'center'},
                                            children=[
                                                html.Div(
                                                    id="doctor-risk-patients", 
                                                    style={
                                                        'fontSize': '1.8rem', 
                                                        'fontWeight': '700', 
                                                        'color': '#ff6b6b',
                                                        'marginBottom': '5px'
                                                    }
                                                ),
                                                html.Div("En Riesgo", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),

                        html.H4(
                            "Mis Pacientes", 
                            style={
                                'color': HIGHLIGHT_COLOR, 
                                'marginTop': '30px',
                                'marginBottom': '15px',
                                'fontSize': '1.5rem'
                            }
                        ),
                        html.Div(
                            "AquÃ­ puedes ver a todos tus pacientes. Haz doble clic en cualquier tarjeta para ver sus datos detallados.",
                            style={
                                'color': '#ccc', 
                                'marginBottom': '20px',
                                'fontSize': '1rem'
                            }
                        ),

                        # Contenedor de pacientes (se llenarÃ¡ dinÃ¡micamente)
                        html.Div(
                            id="doctor-patients-grid",
                            style={
                                'display': 'grid',
                                'gridTemplateColumns': 'repeat(auto-fill, minmax(350px, 1fr))',
                                'gap': '20px',
                                'marginTop': '20px'
                            }
                        ),

                        # Div de debug (opcional, puedes comentarlo en producciÃ³n)
                        html.Div(
                            id="doctor-debug-info",
                            style={
                                'marginTop': '40px',
                                'padding': '15px',
                                'backgroundColor': 'rgba(0, 0, 0, 0.2)',
                                'borderRadius': '8px',
                                'border': '1px solid #444',
                                'fontSize': '0.85rem'
                            }
                        )
                    ]
                )
            ]
        )
    ]
)

# ===============================
# BODY (SIDEBAR + MAIN)
# ===============================
html.Div(
 style={'display': 'flex'},
 children=[

     # ===============================
     # SIDEBAR
     # ===============================
     html.Div(
         style={
             'width': '300px',
             'padding': '30px',
             'borderRight': '1px solid rgba(0, 212, 255, 0.1)'
         },
         children=[

             html.H4(
                 "NavegaciÃ³n MÃ©dico",
                 style={
                     'color': '#4ecdc4',
                     'marginBottom': '20px',
                     'fontSize': '1.1rem'
                 }
             ),

             html.Button(
                 "Dashboard",
                 id="nav-dashboard-doctor",
                 n_clicks=0,
                 style={
                     'width': '100%',
                     'padding': '12px',
                     'backgroundColor': 'rgba(78, 205, 196, 0.1)',
                     'borderRadius': '10px',
                     'border': 'none',
                     'color': '#4ecdc4',
                     'textAlign': 'left',
                     'marginBottom': '10px'
                 }
             ),

             html.Button(
                 "Mis Pacientes",
                 id="nav-pacientes-doctor",
                 n_clicks=0,
                 style={
                     'width': '100%',
                     'padding': '12px',
                     'backgroundColor': 'transparent',
                     'borderRadius': '10px',
                     'border': 'none',
                     'color': '#ccc',
                     'textAlign': 'left',
                     'marginBottom': '10px'
                 }
             ),

             html.Hr(style={'margin': '30px 0'}),

             html.H4(
                 "Buscar Pacientes",
                 style={'color': HIGHLIGHT_COLOR}
             ),

             dcc.Input(
                 id="doctor-search-input",
                 type="text",
                 placeholder="Nombre, usuario o email...",
                 style={
                     'width': '100%',
                     'padding': '10px',
                     'marginBottom': '10px'
                 }
             ),

             html.Button(
                 "Buscar",
                 id="doctor-search-btn",
                 style={
                     'width': '100%',
                     'padding': '10px',
                     'backgroundColor': HIGHLIGHT_COLOR,
                     'border': 'none',
                     'borderRadius': '8px',
                     'fontWeight': '600'
                 }
             ),

             html.Div(
                 id="doctor-search-results",
                 style={'marginTop': '20px'}
             )
         ]
     ),

     # ===============================
     # MAIN CONTENT
     # ===============================
     html.Div(
         className="doctor-main",
         style={
             'flex': '1',
             'padding': '40px',
             'overflowY': 'auto'
         },
         children=[
             html.H2(
                 "Panel de Control MÃ©dico",
                 style={
                     'color': HIGHLIGHT_COLOR,
                     'marginBottom': '20px'
                 }
             ),

             html.Div(
                 f"Ãšltima actualizaciÃ³n: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                 style={
                     'color': '#aaa',
                     'marginBottom': '30px'
                 }
             ),

             html.Div(id="doctor-patients-grid")
         ]
     )
 ]
)

# ===============================
# ONBOARDING LAYOUT
# ===============================

def onboarding_step_1(user_name="Usuario/a"):
    return html.Div([
        html.H3(f"Â¡Hola, {user_name}!", className="text-white-50 mb-4 fs-3"),
        html.P("PrepÃ¡rate para crear tu plan personalizado. Necesitamos que respondas a 5 preguntas para optimizar tus resultados.", className="step-subtitle"),
        html.P("Haz clic en Siguiente para comenzar con tus datos biomÃ©tricos.", className="text-white-50 mt-4"),
    ], className="text-center p-4")

def onboarding_step_2():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.P("Estatura (cm)", className="text-white-50 mb-1"),
                dcc.Input(id="input-height", type="number", placeholder="175", min=100, max=250, className="onboarding-input")
            ], md=6),
            dbc.Col([
                html.P("Peso (kg)", className="text-white-50 mb-1"),
                dcc.Input(id="input-weight", type="number", placeholder="65", min=30, max=300, className="onboarding-input")
            ], md=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.P("Edad (aÃ±os)", className="text-white-50 mb-1"),
                dcc.Input(id="input-age", type="number", placeholder="28", min=1, max=100, className="onboarding-input")
            ], md=6),
            dbc.Col([
                html.P("GÃ©nero", className="text-white-50 mb-1"),
                dcc.Dropdown(
                    id="input-gender",
                    options=[
                        {'label': 'Femenino', 'value': 'F'},
                        {'label': 'Masculino', 'value': 'M'},
                        {'label': 'Otro', 'value': 'O'}
                    ],
                    value='F',
                    clearable=False,
                    className="dbc dbc-row-selectable",
                    style={'backgroundColor': '#2b2b2b', 'color': 'white', 'border': '1px solid #444'}
                )
            ], md=6),
        ], className="mb-4"),
        
        html.Div(id="step-2-error", className="text-warning mb-3"),
    ], className="p-4")

def onboarding_step_3():
    sport_cards = []
    
    for sport in SPORTS_OPTIONS:
        base_class = "radio-card"
        sport_cards.append(
            html.Div([
                html.I(className=sport["icon"], style={'fontSize': '1.8rem', 'marginBottom': '8px'}),  # Icono mÃ¡s grande
                html.P(sport["label"], className="mb-0", style={'fontSize': '0.95rem', 'fontWeight': '500'})
            ], className=base_class, id={"type": "sport-card", "index": sport["label"]})
        )

    return html.Div([
        html.P("Â¿QuÃ© deportes practicas? (Selecciona todos los que apliquen)", className="text-white-50 mb-3"),
        html.Div(sport_cards, className="radio-card-group mb-4", id="sport-selection-container"),

        html.P("Nivel de actividad semanal (1-10)", className="text-white-50 mb-2 mt-4"),
        dcc.Slider(
            id='input-activity-level',
            min=1, max=10, step=1, value=5,
            marks={
                1: '1', 2: '2', 3: '3', 4: '4', 5: '5',
                6: '6', 7: '7', 8: '8', 9: '9', 10: '10'
            },
            className="mb-4 text-white-50",
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        
        html.Div(id="activity-level-indicator", className="mb-4", style={'textAlign': 'center'}),

        html.P("Objetivo principal", className="text-white-50 mb-2"),
        dcc.Dropdown(
            id="input-main-goal",
            options=[
                {'label': 'Mejorar rendimiento (Resistencia/Velocidad)', 'value': 'PERFORMANCE'},
                {'label': 'PÃ©rdida de peso (DefiniciÃ³n)', 'value': 'WEIGHT_LOSS'},
                {'label': 'Aumento de masa muscular (Volumen)', 'value': 'MUSCLE_GAIN'},
                {'label': 'Mejorar el bienestar general y la salud', 'value': 'WELLNESS'},
            ],
            value='PERFORMANCE',
            clearable=False,
            className="dbc dbc-row-selectable",
            style={'backgroundColor': '#2b2b2b', 'color': 'white', 'border': '1px solid #444'}
        ),
        
        html.Div(id="step-3-error", className="text-warning mb-3"),
    ], className="p-4")

def onboarding_step_4():
    health_options = [{'label': condition, 'value': condition} for condition in HEALTH_CONDITIONS]

    return html.Div([
        html.P("Enfermedades relevantes (Marca si aplica)", className="text-white-50 mb-2"),
        dbc.Checklist(
            id="input-health-conditions",
            options=health_options,
            value=["Ninguna"],
            inline=False,
            className="mb-4 text-white",
            inputStyle={"marginRight": "8px"},
            labelStyle={"fontSize": "1rem", "fontWeight": "300", "color": "#ccc", "marginRight": "20px"}
        ),
        
        html.P("Lesiones actuales (opcional)", className="text-white-50 mb-1 mt-4"),
        dbc.Row([
            dbc.Col(dcc.Input(id="input-injury-location", type="text", placeholder="Ej: Rodilla derecha", className="onboarding-input"), md=6),
            dbc.Col(dcc.Input(id="input-injury-severity", type="text", placeholder="Gravedad: Baja / Media / Alta", className="onboarding-input"), md=6),
        ], className="mb-4"),

        html.P("MedicaciÃ³n o suplementaciÃ³n relevante (opcional)", className="text-white-50 mb-1"),
        dcc.Input(id="input-medication", type="text", placeholder="Suplementos, medicamentos para entrenamientos...", className="onboarding-input"),
        
        html.Div(id="step-4-error", className="text-warning mb-3"),
    ], className="p-4")

def onboarding_step_5():
    diet_options = [{'label': restriction, 'value': restriction} for restriction in DIET_RESTRICTIONS]

    return html.Div([
        html.H4("SueÃ±o y NutriciÃ³n", className="text-white mb-3"),
        html.P("Horas de sueÃ±o promedio", className="text-white-50 mb-1"),
        dcc.Input(id="input-sleep-hours", type="number", placeholder="7.5", min=4, max=12, step=0.5, className="onboarding-input mb-4"),
        
        html.P("Restricciones alimentarias", className="text-white-50 mb-2"),
        dbc.Checklist(
            id="input-diet-restrictions",
            options=diet_options,
            value=["Ninguna"],
            inline=True,
            className="mb-4 text-white",
            inputStyle={"marginRight": "8px"},
            labelStyle={"fontSize": "0.95rem", "fontWeight": "300", "color": "#ccc", "marginRight": "20px"}
        ),

        html.H4("Preferencias y Dispositivos", className="text-white mb-3 mt-4"),
        html.P("Intensidad preferida de entrenamiento", className="text-white-50 mb-2"),
        dbc.RadioItems(
            id="input-intensity",
            options=[
                {'label': 'Leve', 'value': 'LOW'},
                {'label': 'Moderada', 'value': 'MEDIUM'},
                {'label': 'Alta', 'value': 'HIGH'},
            ],
            value='MEDIUM',
            inline=True,
            className="mb-4 text-white",
            inputStyle={"marginRight": "8px"},
            labelStyle={"fontSize": "0.95rem", "fontWeight": '300', "color": "#ccc", "marginRight": "20px"}
        ),

        html.P("Conectar dispositivo (opcional)", className="text-white-50 mb-2"),
        dbc.Row([
            dbc.Col(dbc.Button([html.I(className="bi bi-apple me-2"), "Apple Health / Watch"], outline=True, color="secondary", className="w-100"), md=6, className="mb-2"),
            dbc.Col(dbc.Button([html.I(className="bi bi-watch me-2"), "Garmin / Wearable"], outline=True, color="secondary", className="w-100"), md=6, className="mb-2"),
        ], className="mb-5"),
        
        html.Div(id="step-5-error", className="text-warning mb-3"),
    ], className="p-4")

onboarding_layout = html.Div(
    className="onboarding-container",
    children=[
        html.Div(
            className="onboarding-card",
            children=[
                html.Div(
                    className="onboarding-header",
                    children=[
                        html.H3(id="onboarding-current-step-title", className="step-title"),
                        html.P(id="onboarding-current-step-subtitle", className="step-subtitle"),
                        html.Div(className="progress-bar-container", children=[
                            html.Div(id="onboarding-progress-bar", className="progress-bar", style={"width": "0%"})
                        ]),
                    ]
                ),

                html.Div(id="onboarding-content"),

                html.Div(
                    [
                        dbc.Button("Anterior", id="onboarding-prev-btn-visual", color="secondary", outline=True, className="me-3"),
                        dbc.Button("Siguiente", id="onboarding-next-btn-visual", color="primary", className="auth-btn"),
                    ],
                    className="d-flex justify-content-between mt-4", 
                    id="onboarding-nav-container"
                )
            ]
        ),
    ]
)

# ===============================
# FUNCIÃ“N PARA CREAR LAYOUT DE INICIO (VERSIÃ“N CORREGIDA)
# ===============================

def create_inicio_layout(show_doctor_indicator=False, patient_username=None):
    """Crea el layout de inicio, con opciÃ³n para mostrar indicador mÃ©dico"""
    
    # Determinar el tÃ­tulo basado en si es vista mÃ©dica o normal
    if show_doctor_indicator and patient_username:
        main_title = f"Vista de Paciente: {patient_username}"
        description = f"EstÃ¡s viendo los datos del paciente {patient_username}. Se muestra su resumen deportivo: objetivos semanales, frecuencia cardÃ­aca en tiempo real, calorÃ­as consumidas y capacidad aerÃ³bica."
    else:
        main_title = "Resumen Semanal"
        description = "Se muestra tu resumen deportivo: objetivos semanales, frecuencia cardÃ­aca en tiempo real, calorÃ­as consumidas y capacidad aerÃ³bica."
    
    return html.Div(
        id="inicio-container",
        className="inicio-container",
        style={
            'backgroundColor': DARK_BACKGROUND,
            'minHeight': '100vh',
            'color': 'white',
            'fontFamily': 'Inter, sans-serif'
        },
        children=[
            # HEADER PRINCIPAL
            html.Div(
                id="inicio-header",
                className="inicio-header",
                style={
                    'backgroundColor': '#1a1a1a',
                    'padding': '15px 40px',
                    'borderBottom': '1px solid rgba(0, 212, 255, 0.1)',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center'
                },
                children=[
                    html.Div(
                        style={'display': 'flex', 'alignItems': 'center'},
                        children=[
                            html.Div(
                                style={
                                    'width': '40px',
                                    'height': '40px',
                                    'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                    'borderRadius': '10px',
                                    'border': f'2px solid {HIGHLIGHT_COLOR}',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'marginRight': '15px'
                                },
                                children=html.Span("A", style={'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.2rem'})
                            ),
                            html.H1(
                                "ATHLETICA",
                                style={
                                    'color': HIGHLIGHT_COLOR,
                                    'fontSize': '1.8rem',
                                    'fontWeight': '900',
                                    'letterSpacing': '2px',
                                    'textShadow': f'0 0 15px rgba(0, 224, 255, 0.5)',
                                    'margin': '0'
                                }
                            )
                        ]
                    ),
                    
                    html.Div(
                        style={
                            'flex': '1',
                            'height': '1px',
                            'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                            'margin': '0 30px'
                        }
                    ),
                    
                    html.Div(
                        style={'display': 'flex', 'alignItems': 'center', 'gap': '20px'},
                        children=[
                            html.Div(
                                style={
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'gap': '10px',
                                    'cursor': 'pointer'
                                },
                                children=[
                                    html.Div(
                                        id="user-profile-avatar",
                                        style={
                                            'width': '45px',
                                            'height': '45px',
                                            'backgroundColor': HIGHLIGHT_COLOR,
                                            'borderRadius': '50%',
                                            'border': f'2px solid {HIGHLIGHT_COLOR}',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'color': '#0a0a0a',
                                            'fontWeight': 'bold',
                                            'fontSize': '1.2rem'
                                        }
                                    ),
                                    html.Div(
                                        style={'textAlign': 'right'},
                                        children=[
                                            html.Div(
                                                id="user-profile-name",
                                                style={
                                                    'fontWeight': '600',
                                                    'fontSize': '1rem',
                                                    'color': '#fff'
                                                }
                                            ),
                                            html.Div(
                                                id="user-profile-type",
                                                style={
                                                    'fontSize': '0.8rem',
                                                    'color': HIGHLIGHT_COLOR,
                                                    'fontWeight': '500'
                                                }
                                            )
                                        ]
                                    )
                                ]
                            ),
                        ]
                    )
                ]
            ),

            # CUERPO PRINCIPAL (Sidebar + Contenido)
            html.Div(
                style={
                    'display': 'flex',
                    'minHeight': 'calc(100vh - 100px)'
                },
                children=[
                    # ===== SIDEBAR (SIEMPRE VISIBLE) =====
                    html.Div(
                        id="inicio-sidebar",
                        className="inicio-sidebar",
                        style={
                            'width': '280px',
                            'backgroundColor': '#141414',
                            'padding': '25px 20px',
                            'borderRight': '1px solid rgba(0, 212, 255, 0.1)',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'gap': '30px'
                        },
                        children=[
                            # Perfil de usuario
                            html.Div(
                                style={
                                    'padding': '20px',
                                    'backgroundColor': '#1a1a1a',
                                    'borderRadius': '15px',
                                    'border': '1px solid rgba(0, 212, 255, 0.1)',
                                    'textAlign': 'center'
                                },
                                children=[
                                    html.Div(
                                        id="sidebar-user-avatar",
                                        style={
                                            'width': '70px',
                                            'height': '70px',
                                            'backgroundColor': HIGHLIGHT_COLOR,
                                            'borderRadius': '50%',
                                            'border': f'3px solid {HIGHLIGHT_COLOR}',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'color': '#0a0a0a',
                                            'fontWeight': 'bold',
                                            'fontSize': '1.8rem',
                                            'margin': '0 auto 15px'
                                        }
                                    ),
                                    
                                    html.Div(
                                        id="sidebar-user-fullname",
                                        style={
                                            'fontSize': '1.3rem',
                                            'fontWeight': '700',
                                            'color': '#ffffff',
                                            'marginBottom': '5px'
                                        }
                                    ),
                                    
                                    html.Div(
                                        id="sidebar-user-level",
                                        style={
                                            'fontSize': '0.9rem',
                                            'color': HIGHLIGHT_COLOR,
                                            'fontWeight': '500',
                                            'marginBottom': '20px'
                                        }
                                    ),
                                    
                                    html.Div(
                                        style={
                                            'height': '1px',
                                            'backgroundColor': 'rgba(255, 255, 255, 0.1)',
                                            'margin': '15px 0'
                                        }
                                    ),
                                    
                                    html.Div(
                                        "Estado de Salud",
                                        style={
                                            'fontSize': '1rem',
                                            'fontWeight': '600',
                                            'color': '#ffffff',
                                            'marginBottom': '15px',
                                            'textAlign': 'center'
                                        }
                                    ),
                                    
                                    html.Div(
                                        id="health-status-dots",
                                        style={
                                            'display': 'flex',
                                            'justifyContent': 'center',
                                            'gap': '8px',
                                            'marginBottom': '12px'
                                        }
                                    ),
                                    
                                    html.Div(
                                        id="health-status-description",
                                        style={
                                            'fontSize': '0.8rem',
                                            'color': '#cccccc',
                                            'textAlign': 'center',
                                            'lineHeight': '1.4'
                                        }
                                    )
                                ]
                            ),
                            
                            # NavegaciÃ³n (diferente para mÃ©dicos y atletas)
                            html.Div(
                                children=[
                                    html.H4(
                                        "NavegaciÃ³n",
                                        style={
                                            'color': HIGHLIGHT_COLOR,
                                            'marginBottom': '20px',
                                            'marginTop': '25px',
                                            'fontSize': '1.1rem',
                                            'fontWeight': '600',
                                            'paddingLeft': '10px'
                                        }
                                    ),
                                    html.Div(
                                        style={'display': 'flex', 'flexDirection': 'column', 'gap': '8px'},
                                        children=[
                                            # BotÃ³n Dashboard MÃ©dico (SOLO para mÃ©dicos)
                                            html.Button(
                                                [
                                                    html.I(className="bi bi-hospital", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                    html.Span("Dashboard MÃ©dico", style={'fontSize': '0.95rem', 'fontWeight': '500'})
                                                ],
                                                id="nav-dashboard-doctor",
                                                n_clicks=0,
                                                style={
                                                    'display': 'flex',
                                                    'alignItems': 'center',
                                                    'padding': '12px 15px',
                                                    'backgroundColor': 'transparent',
                                                    'borderRadius': '10px',
                                                    'cursor': 'pointer',
                                                    'transition': 'all 0.3s ease',
                                                    'border': '1px solid transparent',
                                                    'color': '#ccc',
                                                    'textAlign': 'left',
                                                    'fontFamily': "'Inter', sans-serif",
                                                    'border': 'none'
                                                }
                                            ),
                                            
                                            # BotÃ³n Inicio
                                            html.Button(
                                                [
                                                    html.I(className="bi bi-house-door", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                    html.Span("Inicio", style={'fontSize': '0.95rem', 'fontWeight': '500'})
                                                ],
                                                id="nav-inicio-inicio",
                                                n_clicks=0,
                                                style={
                                                    'display': 'flex',
                                                    'alignItems': 'center',
                                                    'padding': '12px 15px',
                                                    'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                    'borderRadius': '10px',
                                                    'cursor': 'pointer',
                                                    'transition': 'all 0.3s ease',
                                                    'border': f'1px solid {HIGHLIGHT_COLOR}',
                                                    'color': HIGHLIGHT_COLOR,
                                                    'textAlign': 'left',
                                                    'fontFamily': "'Inter', sans-serif",
                                                    'border': 'none'
                                                }
                                            ),
                                            
                                            # BotÃ³n MÃ©tricas
                                            html.Button(
                                                [
                                                    html.I(className="bi bi-graph-up", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                    html.Span("MÃ©tricas", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                                ],
                                                id="nav-metricas-inicio",
                                                n_clicks=0,
                                                style={
                                                    'display': 'flex',
                                                    'alignItems': 'center',
                                                    'padding': '12px 15px',
                                                    'backgroundColor': 'transparent',
                                                    'borderRadius': '10px',
                                                    'cursor': 'pointer',
                                                    'transition': 'all 0.3s ease',
                                                    'border': '1px solid transparent',
                                                    'color': '#ccc',
                                                    'textAlign': 'left',
                                                    'fontFamily': "'Inter', sans-serif",
                                                    'border': 'none'
                                                }
                                            ),
                                            
                                            # BotÃ³n Objetivos
                                            html.Button(
                                                [
                                                    html.I(className="bi bi-bullseye", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                    html.Span("Objetivos", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                                ],
                                                id="nav-objetivos-inicio",
                                                n_clicks=0,
                                                style={
                                                    'display': 'flex',
                                                    'alignItems': 'center',
                                                    'padding': '12px 15px',
                                                    'backgroundColor': 'transparent',
                                                    'borderRadius': '10px',
                                                    'cursor': 'pointer',
                                                    'transition': 'all 0.3s ease',
                                                    'border': '1px solid transparent',
                                                    'color': '#ccc',
                                                    'textAlign': 'left',
                                                    'fontFamily': "'Inter', sans-serif",
                                                    'border': 'none'
                                                }
                                            ),
                                            
                                            # BotÃ³n NutriciÃ³n
                                            html.Button(
                                                [
                                                    html.I(className="bi bi-egg-fried", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                    html.Span("NutriciÃ³n", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                                ],
                                                id="nav-nutricion-inicio",
                                                n_clicks=0,
                                                style={
                                                    'display': 'flex',
                                                    'alignItems': 'center',
                                                    'padding': '12px 15px',
                                                    'backgroundColor': 'transparent',
                                                    'borderRadius': '10px',
                                                    'cursor': 'pointer',
                                                    'transition': 'all 0.3s ease',
                                                    'border': '1px solid transparent',
                                                    'color': '#ccc',
                                                    'textAlign': 'left',
                                                    'fontFamily': "'Inter', sans-serif",
                                                    'border': 'none'
                                                }
                                            ),
                                            
                                            # BotÃ³n Entrenamientos
                                            html.Button(
                                                [
                                                    html.I(className="bi bi-activity", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                    html.Span("Entrenamientos", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                                ],
                                                id="nav-entrenamientos-inicio",
                                                n_clicks=0,
                                                style={
                                                    'display': 'flex',
                                                    'alignItems': 'center',
                                                    'padding': '12px 15px',
                                                    'backgroundColor': 'transparent',
                                                    'borderRadius': '10px',
                                                    'cursor': 'pointer',
                                                    'transition': 'all 0.3s ease',
                                                    'border': '1px solid transparent',
                                                    'color': '#ccc',
                                                    'textAlign': 'left',
                                                    'fontFamily': "'Inter', sans-serif",
                                                    'border': 'none'
                                                }
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # ===== CONTENIDO PRINCIPAL =====
                    html.Div(
                        className="inicio-main",
                        style={
                            'flex': '1',
                            'padding': '30px',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'gap': '25px'
                        },
                        children=[
                            # Header principal
                            html.Div(
                                style={
                                    'display': 'flex',
                                    'justifyContent': 'space-between',
                                    'alignItems': 'center',
                                    'marginBottom': '10px'
                                },
                                children=[
                                    html.H2(
                                        main_title,
                                        style={
                                            'color': HIGHLIGHT_COLOR,
                                            'fontSize': '2rem',
                                            'fontWeight': '700',
                                            'margin': '0'
                                        }
                                    ),
                                    html.Div(
                                        style={
                                            'color': '#ccc',
                                            'fontSize': '1rem'
                                        },
                                        children=f"Ãšltima actualizaciÃ³n: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                                    )
                                ]
                            ),
                            
                            # INDICADOR DE VISTA MÃ‰DICA (SOLO VISIBLE PARA MÃ‰DICOS VIENDO PACIENTES)
                            html.Div(
                                id="doctor-view-indicator",
                                style={
                                    'display': 'block' if show_doctor_indicator else 'none',  # Controlado por parÃ¡metro
                                    'marginBottom': '20px'
                                },
                                children=[
                                    html.Div(
                                        style={
                                            'backgroundColor': 'rgba(78, 205, 196, 0.1)',
                                            'borderRadius': '10px',
                                            'padding': '20px',
                                            'border': '1px solid #4ecdc4'
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    'display': 'flex',
                                                    'justifyContent': 'space-between',
                                                    'alignItems': 'center'
                                                },
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.I(className="bi bi-person-badge me-2", 
                                                                   style={'color': '#4ecdc4', 'fontSize': '1.2rem'}),
                                                            "Viendo paciente: ",
                                                            html.Strong(patient_username, 
                                                                       style={'color': '#4ecdc4', 'marginLeft': '5px'})
                                                        ],
                                                        style={'color': '#fff', 'fontSize': '1.1rem'}
                                                    ),
                                                    html.Button(
                                                        [
                                                            html.I(className="bi bi-arrow-left me-2"),
                                                            "Volver a Mi Dashboard"
                                                        ], 
                                                        id="btn-back-to-doctor-dashboard",
                                                        n_clicks=0,
                                                        style={
                                                            'backgroundColor': '#4ecdc4',
                                                            'border': 'none',
                                                            'color': '#0a0a0a',
                                                            'padding': '10px 20px',
                                                            'borderRadius': '8px',
                                                            'cursor': 'pointer',
                                                            'fontWeight': '600',
                                                            'transition': 'all 0.3s ease',
                                                            'fontSize': '1rem',
                                                            'fontFamily': "'Inter', sans-serif"
                                                        }
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            
                            # DescripciÃ³n
                            html.P(
                                description,
                                style={
                                    'color': '#ccc', 
                                    'fontSize': '1.1rem',
                                    'marginBottom': '30px',
                                    'maxWidth': '800px',
                                    'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                    'padding': '15px 20px',
                                    'borderRadius': '10px',
                                    'border': '1px solid rgba(0, 212, 255, 0.1)'
                                }
                            ),
                            
                            # SecciÃ³n 1: Objetivos Semanales
                            html.Div(
                                style={
                                    'backgroundColor': '#1a1a1a',
                                    'borderRadius': '15px',
                                    'padding': '25px',
                                    'border': '1px solid rgba(0, 212, 255, 0.1)',
                                    'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                                },
                                children=[
                                    html.H3(
                                        "Objetivos Semanales",
                                        style={
                                            'color': HIGHLIGHT_COLOR,
                                            'marginBottom': '25px',
                                            'fontSize': '1.5rem'
                                        }
                                    ),
                                    
                                    html.Div(
                                        style={
                                            'display': 'grid',
                                            'gridTemplateColumns': 'repeat(3, 1fr)',
                                            'gap': '20px'
                                        },
                                        children=[
                                            # Cardio
                                            html.Div(
                                                style={'textAlign': 'center'},
                                                children=[
                                                    html.Div(
                                                        style={
                                                            'display': 'flex',
                                                            'justifyContent': 'space-between',
                                                            'marginBottom': '10px'
                                                        },
                                                        children=[
                                                            html.Span("Cardio", style={'fontWeight': '600', 'fontSize': '1.1rem'}),
                                                            html.Span("4 de 8", style={'color': HIGHLIGHT_COLOR, 'fontWeight': '600', 'fontSize': '1.1rem'})
                                                        ]
                                                    ),
                                                    html.Div(
                                                        style={
                                                            'height': '8px',
                                                            'backgroundColor': '#2b2b2b',
                                                            'borderRadius': '4px',
                                                            'overflow': 'hidden',
                                                            'marginBottom': '5px'
                                                        },
                                                        children=html.Div(
                                                            style={
                                                                'width': '50%',  # 4/8 = 50%
                                                                'height': '100%',
                                                                'backgroundColor': HIGHLIGHT_COLOR,
                                                                'borderRadius': '4px'
                                                            }
                                                        )
                                                    ),
                                                    html.Div(
                                                        "4 de 8 sesiones completadas",
                                                        style={
                                                            'color': '#ccc',
                                                            'fontSize': '0.9rem'
                                                        }
                                                    )
                                                ]
                                            ),
                                            
                                            # Fuerza
                                            html.Div(
                                                style={'textAlign': 'center'},
                                                children=[
                                                    html.Div(
                                                        style={
                                                            'display': 'flex',
                                                            'justifyContent': 'space-between',
                                                            'marginBottom': '10px'
                                                        },
                                                        children=[
                                                            html.Span("Fuerza", style={'fontWeight': '600', 'fontSize': '1.1rem'}),
                                                            html.Span("2 de 3", style={'color': HIGHLIGHT_COLOR, 'fontWeight': '600', 'fontSize': '1.1rem'})
                                                        ]
                                                    ),
                                                    html.Div(
                                                        style={
                                                            'height': '8px',
                                                            'backgroundColor': '#2b2b2b',
                                                            'borderRadius': '4px',
                                                            'overflow': 'hidden',
                                                            'marginBottom': '5px'
                                                        },
                                                        children=html.Div(
                                                            style={
                                                                'width': '67%',  # 2/3 â‰ˆ 67%
                                                                'height': '100%',
                                                                'backgroundColor': HIGHLIGHT_COLOR,
                                                                'borderRadius': '4px'
                                                            }
                                                        )
                                                    ),
                                                    html.Div(
                                                        "2 de 3 sesiones completadas",
                                                        style={
                                                            'color': '#ccc',
                                                            'fontSize': '0.9rem'
                                                        }
                                                    )
                                                ]
                                            ),
                                            
                                            # Flexibilidad
                                            html.Div(
                                                style={'textAlign': 'center'},
                                                children=[
                                                    html.Div(
                                                        style={
                                                            'display': 'flex',
                                                            'justifyContent': 'space-between',
                                                            'marginBottom': '10px'
                                                        },
                                                        children=[
                                                            html.Span("Flexibilidad", style={'fontWeight': '600', 'fontSize': '1.1rem'}),
                                                            html.Span("2/3", style={'color': HIGHLIGHT_COLOR, 'fontWeight': '600', 'fontSize': '1.1rem'})
                                                        ]
                                                    ),
                                                    html.Div(
                                                        style={
                                                            'height': '8px',
                                                            'backgroundColor': '#2b2b2b',
                                                            'borderRadius': '4px',
                                                            'overflow': 'hidden',
                                                            'marginBottom': '5px'
                                                        },
                                                        children=html.Div(
                                                            style={
                                                                'width': '67%',  # 2/3 â‰ˆ 67%
                                                                'height': '100%',
                                                                'backgroundColor': HIGHLIGHT_COLOR,
                                                                'borderRadius': '4px'
                                                            }
                                                        )
                                                    ),
                                                    html.Div(
                                                        "2 de 3 sesiones completadas",
                                                        style={
                                                            'color': '#ccc',
                                                            'fontSize': '0.9rem'
                                                        }
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            
                            # SecciÃ³n 2: MÃ©tricas principales (3 columnas)
                            html.Div(
                                style={
                                    'display': 'grid',
                                    'gridTemplateColumns': '2fr 1fr 1fr',
                                    'gap': '25px'
                                },
                                children=[
                                    # Columna 1: ECG (ancha)
                                    html.Div(
                                        style={
                                            'backgroundColor': '#1a1a1a',
                                            'borderRadius': '15px',
                                            'padding': '25px',
                                            'border': '1px solid rgba(0, 212, 255, 0.1)',
                                            'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)',
                                            'gridColumn': 'span 2'
                                        },
                                        children=[
                                            html.H3(
                                                "Frecuencia CardÃ­aca en Tiempo Real",
                                                style={
                                                    'margin': '0 0 15px 0',
                                                    'fontSize': '1.3rem',
                                                    'color': HIGHLIGHT_COLOR,
                                                    'textAlign': 'center'
                                                }
                                            ),
                                            
                                            html.Div(
                                                [
                                                    html.Div(
                                                        "60 bpm",
                                                        id="current-bpm",
                                                        style={
                                                            'fontSize': '3rem',
                                                            'fontWeight': '700',
                                                            'color': '#fff',
                                                            'textAlign': 'center',
                                                            'marginBottom': '10px'
                                                        }
                                                    ),
                                                    html.Div(
                                                        "Normal",
                                                        id="bpm-status",
                                                        style={
                                                            'color': HIGHLIGHT_COLOR,
                                                            'fontSize': '1.2rem',
                                                            'fontWeight': '500',
                                                            'textAlign': 'center',
                                                            'marginBottom': '20px'
                                                        }
                                                    ),
                                                    html.Div(
                                                        "SeÃ±al ECG en Tiempo Real",
                                                        style={
                                                            'color': '#ccc',
                                                            'fontSize': '0.9rem',
                                                            'textAlign': 'center',
                                                            'marginBottom': '15px'
                                                        }
                                                    )
                                                ]
                                            ),
                                            
                                            dcc.Graph(
                                                id='ecg-graph',
                                                config={'displayModeBar': False},
                                                style={'height': '200px'}
                                            ),
                                            
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Span("MÃ¡x: ", style={'color': '#ccc'}),
                                                            html.Span("70 bpm", id="max-bpm", style={'color': '#ff6b6b', 'fontWeight': '600'})
                                                        ],
                                                        style={'display': 'inline-block', 'marginRight': '20px'}
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Span("MÃ­n: ", style={'color': '#ccc'}),
                                                            html.Span("48 bpm", id="min-bpm", style={'color': '#4ecdc4', 'fontWeight': '600'})
                                                    ],
                                                        style={'display': 'inline-block', 'marginRight': '20px'}
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Span("Promedio: ", style={'color': '#ccc'}),
                                                            html.Span("60 bpm", id="avg-bpm", style={'color': HIGHLIGHT_COLOR, 'fontWeight': '600'})
                                                        ],
                                                        style={'display': 'inline-block'}
                                                    )
                                                ],
                                                style={
                                                    'textAlign': 'center',
                                                    'marginTop': '15px',
                                                    'padding': '10px',
                                                    'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                    'borderRadius': '8px'
                                                }
                                            )
                                        ]
                                    ),
                                    
                                    # Columna 2: CalorÃ­as
                                    html.Div(
                                        style={
                                            'backgroundColor': '#1a1a1a',
                                            'borderRadius': '15px',
                                            'padding': '25px',
                                            'border': '1px solid rgba(0, 212, 255, 0.1)',
                                            'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                                        },
                                        children=[
                                            html.H3("CalorÃ­as", style={'margin': '0 0 15px 0', 'fontSize': '1.1rem', 'color': '#ccc'}),
                                            html.Div("2,847", style={'fontSize': '2.5rem', 'fontWeight': '700', 'color': '#fff', 'marginBottom': '5px'}),
                                            html.Div("Objetivo: 3,000 kcal", style={'color': HIGHLIGHT_COLOR, 'fontSize': '1rem', 'fontWeight': '500'})
                                        ]
                                    ),
                                    
                                    # Columna 3: VOâ‚‚ Max
                                    html.Div(
                                        style={
                                            'backgroundColor': '#1a1a1a',
                                            'borderRadius': '15px',
                                            'padding': '25px',
                                            'border': '1px solid rgba(0, 212, 255, 0.1)',
                                            'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                                        },
                                        children=[
                                            html.H3("VOâ‚‚ Max", style={'margin': '0 0 15px 0', 'fontSize': '1.1rem', 'color': '#ccc'}),
                                            html.Div("48.2", style={'fontSize': '2.5rem', 'fontWeight': '700', 'color': '#fff', 'marginBottom': '5px'}),
                                            html.Div("ml/(kgÂ·min) + Excelente", style={'color': '#ccc', 'fontSize': '0.9rem', 'marginBottom': '10px'}),
                                            html.Div("+23 vs max anterior", style={'color': HIGHLIGHT_COLOR, 'fontSize': '1rem', 'fontWeight': '500'})
                                        ]
                                    )
                                ]
                            ),
                            
                            # Resumen de salud
                            html.Div(
                                style={
                                    'marginTop': '20px',
                                    'padding': '15px',
                                    'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                    'borderRadius': '10px',
                                    'border': '1px solid rgba(0, 212, 255, 0.1)',
                                    'textAlign': 'center'
                                },
                                children=[
                                    html.Div(
                                        id="health-summary-text",
                                        style={
                                            'color': HIGHLIGHT_COLOR,
                                            'fontSize': '0.9rem',
                                            'fontWeight': '500'
                                        }
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Layout por defecto (sin indicador mÃ©dico)
inicio_layout = create_inicio_layout()

def create_patient_view_layout(patient_username):
    """Crea el layout para ver datos de un paciente especÃ­fico"""
    
    if patient_username in USERS_DB:
        patient_data = USERS_DB[patient_username]
        patient_name = patient_data.get("full_name", patient_username)
        activity_level = patient_data.get("activity_level", 5)
        
        # Crear layout especial para vista de paciente
        return create_inicio_layout(
            show_doctor_indicator=True,
            patient_username=patient_username
        )
    else:
        # Si el paciente no existe, volver al inicio normal
        return create_inicio_layout(show_doctor_indicator=False)

# ===============================
# MÃ‰TRICAS LAYOUT (SOLO GRÃFICAS AVANZADAS)
# ===============================
metricas_layout = html.Div(
    id="metricas-container",
    className="metricas-container",
    style={
        'backgroundColor': DARK_BACKGROUND,
        'minHeight': '100vh',
        'color': 'white',
        'fontFamily': 'Inter, sans-serif'
    },
    children=[
        html.Div(
            id="metricas-header",
            className="metricas-header",
            style={
                'backgroundColor': '#1a1a1a',
                'padding': '15px 40px',
                'borderBottom': '1px solid rgba(0, 212, 255, 0.1)',
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center'
            },
            children=[
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center'},
                    children=[
                        html.Div(
                            style={
                                'width': '40px',
                                'height': '40px',
                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                'borderRadius': '10px',
                                'border': f'2px solid {HIGHLIGHT_COLOR}',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginRight': '15px'
                            },
                            children=html.Span("A", style={'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.2rem'})
                        ),
                        html.H1(
                            "ATHLETICA",
                            style={
                                'color': HIGHLIGHT_COLOR,
                                'fontSize': '1.8rem',
                                'fontWeight': '900',
                                'letterSpacing': '2px',
                                'textShadow': f'0 0 15px rgba(0, 224, 255, 0.5)',
                                'margin': '0'
                            }
                        )
                    ]
                ),
                
                html.Div(
                    style={
                        'flex': '1',
                        'height': '1px',
                        'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                        'margin': '0 30px'
                    }
                ),
                
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'gap': '20px'},
                    children=[
                        html.Div(
                            style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'gap': '10px',
                                'cursor': 'pointer'
                            },
                            children=[
                                html.Div(
                                    id="metricas-user-profile-avatar",
                                    style={
                                        'width': '45px',
                                        'height': '45px',
                                        'backgroundColor': HIGHLIGHT_COLOR,
                                        'borderRadius': '50%',
                                        'border': f'2px solid {HIGHLIGHT_COLOR}',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.2rem'
                                    }
                                ),
                                html.Div(
                                    style={'textAlign': 'right'},
                                    children=[
                                        html.Div(
                                            id="metricas-user-profile-name",
                                            style={
                                                'fontWeight': '600',
                                                'fontSize': '1rem',
                                                'color': '#fff'
                                            }
                                        ),
                                        html.Div(
                                            "Atleta",
                                            style={
                                                'fontSize': '0.8rem',
                                                'color': HIGHLIGHT_COLOR,
                                                'fontWeight': '500'
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),
                    ]
                )
            ]
        ),

        html.Div(
            style={
                'display': 'flex',
                'minHeight': 'calc(100vh - 100px)'
            },
            children=[
                html.Div(
                    id="metricas-sidebar",
                    className="metricas-sidebar",
                    style={
                        'width': '280px',
                        'backgroundColor': '#141414',
                        'padding': '25px 20px',
                        'borderRight': '1px solid rgba(0, 212, 255, 0.1)',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '30px'
                    },
                    children=[
                        html.Div(
                            style={
                                'padding': '20px',
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'textAlign': 'center'
                            },
                            children=[
                                html.Div(
                                    id="metricas-sidebar-user-avatar",
                                    style={
                                        'width': '70px',
                                        'height': '70px',
                                        'backgroundColor': HIGHLIGHT_COLOR,
                                        'borderRadius': '50%',
                                        'border': f'3px solid {HIGHLIGHT_COLOR}',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.8rem',
                                        'margin': '0 auto 15px'
                                    }
                                ),
                                
                                html.Div(
                                    id="metricas-sidebar-user-fullname",
                                    style={
                                        'fontSize': '1.3rem',
                                        'fontWeight': '700',
                                        'color': '#ffffff',
                                        'marginBottom': '5px'
                                    }
                                ),
                                
                                html.Div(
                                    id="metricas-sidebar-user-level",
                                    style={
                                        'fontSize': '0.9rem',
                                        'color': HIGHLIGHT_COLOR,
                                        'fontWeight': '500',
                                        'marginBottom': '20px'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'height': '1px',
                                        'backgroundColor': 'rgba(255, 255, 255, 0.1)',
                                        'margin': '15px 0'
                                    }
                                ),
                                
                                html.Div(
                                    "Estado de Salud",
                                    style={
                                        'fontSize': '1rem',
                                        'fontWeight': '600',
                                        'color': '#ffffff',
                                        'marginBottom': '15px',
                                        'textAlign': 'center'
                                    }
                                ),
                                
                                html.Div(
                                    id="metricas-health-status-dots",
                                    style={
                                        'display': 'flex',
                                        'justifyContent': 'center',
                                        'gap': '8px',
                                        'marginBottom': '12px'
                                    }
                                ),
                                
                                html.Div(
                                    id="metricas-health-status-description",
                                    style={
                                        'fontSize': '0.8rem',
                                        'color': '#cccccc',
                                        'textAlign': 'center',
                                        'lineHeight': '1.4'
                                    }
                                )
                            ]
                        ),
                        
                        html.Div(
                            children=[
                                html.H4(
                                    "NavegaciÃ³n",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'marginBottom': '20px',
                                        'marginTop': '25px',
                                        'fontSize': '1.1rem',
                                        'fontWeight': '600',
                                        'paddingLeft': '10px'
                                    }
                                ),
                                html.Div(
                                    style={'display': 'flex', 'flexDirection': 'column', 'gap': '8px'},
                                    children=[
                                        html.Button(
                                            [
                                                html.I(className="bi bi-house-door", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Inicio", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-inicio-metricas",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-graph-up", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("MÃ©tricas", style={'fontSize': '0.95rem', 'fontWeight': '500'})
                                            ],
                                            id="nav-metricas-metricas",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': f'1px solid {HIGHLIGHT_COLOR}',
                                                'color': HIGHLIGHT_COLOR,
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-bullseye", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Objetivos", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-objetivos-metricas",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-egg-fried", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("NutriciÃ³n", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-nutricion-metricas",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),

                                        html.Button(
                                            [
                                                html.I(className="bi bi-activity", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Entrenamientos", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-entrenamientos-metricas",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                
                # CONTENIDO PRINCIPAL PARA MÃ‰TRICAS (SOLO GRÃFICAS AVANZADAS)
                html.Div(
                    className="metricas-main",
                    style={
                        'flex': '1',
                        'padding': '30px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '25px',
                        'overflowY': 'auto'
                    },
                    children=[
                        # Header de mÃ©tricas
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'marginBottom': '10px'
                            },
                            children=[
                                html.H2(
                                    "AnÃ¡lisis de Rendimiento",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'fontSize': '2rem',
                                        'fontWeight': '700',
                                        'margin': '0'
                                    }
                                ),
                                html.Div(
                                    style={
                                        'color': '#ccc',
                                        'fontSize': '1rem'
                                    },
                                    children=f"Ãšltima actualizaciÃ³n: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                                )
                            ]
                        ),
                        
                        # DescripciÃ³n
                        html.P(
                            "AnÃ¡lisis avanzado de mÃ©tricas deportivas utilizando inteligencia artificial para optimizar el rendimiento atlÃ©tico.",
                            style={
                                'color': '#ccc', 
                                'fontSize': '1.1rem',
                                'marginBottom': '30px',
                                'maxWidth': '800px'
                            }
                        ),
                        
                        # PRIMERA GRÃFICA IMPRESIONANTE: AnÃ¡lisis de Intensidad vs RecuperaciÃ³n
                        html.Div(
                            style={
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'padding': '30px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'boxShadow': '0 8px 30px rgba(0, 0, 0, 0.4)',
                                'marginBottom': '25px'
                            },
                            children=[
                                html.Div(
                                    style={
                                        'display': 'flex',
                                        'justifyContent': 'space-between',
                                        'alignItems': 'center',
                                        'marginBottom': '20px'
                                    },
                                    children=[
                                        html.H3(
                                            "ðŸ“ˆ AnÃ¡lisis de Intensidad vs RecuperaciÃ³n",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'margin': '0',
                                                'fontSize': '1.5rem'
                                            }
                                        ),
                                        html.Div(
                                            "Ãšltimos 30 dÃ­as",
                                            style={
                                                'color': '#ccc',
                                                'fontSize': '0.9rem',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                'padding': '8px 15px',
                                                'borderRadius': '20px',
                                                'fontWeight': '500'
                                            }
                                        )
                                    ]
                                ),
                                
                                html.P(
                                    "RelaciÃ³n entre dÃ­as de entrenamiento de alta intensidad y dÃ­as de recuperaciÃ³n activa. "
                                    "El equilibrio Ã³ptimo garantiza progreso sin sobreentrenamiento.",
                                    style={'color': '#aaa', 'marginBottom': '25px', 'fontSize': '1rem'}
                                ),
                                
                                # GRÃFICA 1 CON CONFIGURACIÃ“N SIMPLIFICADA
                                dcc.Graph(
                                    id='intensity-recovery-chart',
                                    config={
                                        'displayModeBar': True,
                                        'displaylogo': False,
                                        'modeBarButtons': [
                                            ['zoom2d'],  # Solo botÃ³n de zoom
                                            ['toImage']  # Solo botÃ³n de descargar
                                        ],
                                        'toImageButtonOptions': {
                                            'format': 'png',
                                            'filename': 'intensidad_recuperacion',
                                            'height': 600,
                                            'width': 1000,
                                            'scale': 1
                                        }
                                    },
                                    style={'height': '400px'}
                                ),
                                
                                html.Div(
                                    style={
                                        'display': 'flex',
                                        'justifyContent': 'space-between',
                                        'marginTop': '20px',
                                        'flexWrap': 'wrap',
                                        'gap': '15px'
                                    },
                                    children=[
                                        html.Div(
                                            style={
                                                'textAlign': 'center',
                                                'padding': '15px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.08)',
                                                'borderRadius': '12px',
                                                'flex': '1',
                                                'minWidth': '200px'
                                            },
                                            children=[
                                                html.Div(
                                                    "87%",
                                                    style={
                                                        'fontSize': '2.5rem',
                                                        'fontWeight': '700',
                                                        'color': HIGHLIGHT_COLOR,
                                                        'marginBottom': '5px'
                                                    }
                                                ),
                                                html.Div(
                                                    "Eficiencia de RecuperaciÃ³n",
                                                    style={'color': '#ccc', 'fontSize': '0.9rem'}
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            style={
                                                'textAlign': 'center',
                                                'padding': '15px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.08)',
                                                'borderRadius': '12px',
                                                'flex': '1',
                                                'minWidth': '200px'
                                            },
                                            children=[
                                                html.Div(
                                                    "2.4%",
                                                    style={
                                                        'fontSize': '2.5rem',
                                                        'fontWeight': '700',
                                                        'color': '#4ecdc4',
                                                        'marginBottom': '5px'
                                                    }
                                                ),
                                                html.Div(
                                                    "Mejora Semanal Promedio",
                                                    style={'color': '#ccc', 'fontSize': '0.9rem'}
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            style={
                                                'textAlign': 'center',
                                                'padding': '15px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.08)',
                                                'borderRadius': '12px',
                                                'flex': '1',
                                                'minWidth': '200px'
                                            },
                                            children=[
                                                html.Div(
                                                    "15",
                                                    style={
                                                        'fontSize': '2.5rem',
                                                        'fontWeight': '700',
                                                        'color': '#ffd166',
                                                        'marginBottom': '5px'
                                                    }
                                                ),
                                                html.Div(
                                                    "DÃ­as Ã“ptimos Consecutivos",
                                                    style={'color': '#ccc', 'fontSize': '0.9rem'}
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # SEGUNDA Y TERCERA GRÃFICA: Lado a lado
                        html.Div(
                            style={
                                'display': 'grid',
                                'gridTemplateColumns': 'repeat(2, 1fr)',
                                'gap': '25px',
                                'marginBottom': '25px'
                            },
                            children=[
                                # SEGUNDA GRÃFICA: Heatmap de Rendimiento Semanal
                                html.Div(
                                    style={
                                        'backgroundColor': '#1a1a1a',
                                        'borderRadius': '15px',
                                        'padding': '30px',
                                        'border': '1px solid rgba(0, 212, 255, 0.1)',
                                        'boxShadow': '0 8px 30px rgba(0, 0, 0, 0.4)'
                                    },
                                    children=[
                                        html.H3(
                                            "ðŸ”¥ Heatmap de Rendimiento Semanal",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'margin': '0 0 15px 0',
                                                'fontSize': '1.4rem'
                                            }
                                        ),
                                        
                                        html.P(
                                            "DistribuciÃ³n de intensidad a lo largo de la semana. Los colores mÃ¡s cÃ¡lidos indican mayor intensidad de entrenamiento.",
                                            style={'color': '#aaa', 'marginBottom': '25px', 'fontSize': '0.95rem'}
                                        ),
                                        
                                        # GRÃFICA 2 CON CONFIGURACIÃ“N SIMPLIFICADA
                                        dcc.Graph(
                                            id='performance-heatmap',
                                            config={
                                                'displayModeBar': True,
                                                'displaylogo': False,
                                                'modeBarButtons': [
                                                    ['zoom2d'],  # Solo botÃ³n de zoom
                                                    ['toImage']  # Solo botÃ³n de descargar
                                                ],
                                                'toImageButtonOptions': {
                                                    'format': 'png',
                                                    'filename': 'heatmap_rendimiento',
                                                    'height': 500,
                                                    'width': 800,
                                                    'scale': 1
                                                }
                                            },
                                            style={'height': '350px'}
                                        ),
                                        
                                        html.Div(
                                            style={
                                                'display': 'flex',
                                                'justifyContent': 'center',
                                                'gap': '20px',
                                                'marginTop': '20px'
                                            },
                                            children=[
                                                html.Div(
                                                    style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'},
                                                    children=[
                                                        html.Div(style={
                                                            'width': '20px',
                                                            'height': '20px',
                                                            'backgroundColor': '#0a2a38',
                                                            'borderRadius': '4px'
                                                        }),
                                                        html.Span("Baja Intensidad", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                                    ]
                                                ),
                                                html.Div(
                                                    style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'},
                                                    children=[
                                                        html.Div(style={
                                                            'width': '20px',
                                                            'height': '20px',
                                                            'backgroundColor': '#006d8f',
                                                            'borderRadius': '4px'
                                                        }),
                                                        html.Span("Media", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                                    ]
                                                ),
                                                html.Div(
                                                    style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'},
                                                    children=[
                                                        html.Div(style={
                                                            'width': '20px',
                                                            'height': '20px',
                                                            'backgroundColor': HIGHLIGHT_COLOR,
                                                            'borderRadius': '4px'
                                                        }),
                                                        html.Span("Alta Intensidad", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                
                                # TERCERA GRÃFICA: Radar de Competencias AtlÃ©ticas
                                html.Div(
                                    style={
                                        'backgroundColor': '#1a1a1a',
                                        'borderRadius': '15px',
                                        'padding': '30px',
                                        'border': '1px solid rgba(0, 212, 255, 0.1)',
                                        'boxShadow': '0 8px 30px rgba(0, 0, 0, 0.4)'
                                    },
                                    children=[
                                        html.H3(
                                            "ðŸŽ¯ Radar de Competencias AtlÃ©ticas",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'margin': '0 0 15px 0',
                                                'fontSize': '1.4rem'
                                            }
                                        ),
                                        
                                        html.P(
                                            "Perfil completo de capacidades fÃ­sicas comparado con atletas de Ã©lite de tu categorÃ­a.",
                                            style={'color': '#aaa', 'marginBottom': '25px', 'fontSize': '0.95rem'}
                                        ),
                                        
                                        # GRÃFICA 3 CON CONFIGURACIÃ“N SIMPLIFICADA
                                        dcc.Graph(
                                            id='athletic-radar-chart',
                                            config={
                                                'displayModeBar': True,
                                                'displaylogo': False,
                                                'modeBarButtons': [
                                                    ['zoom2d'],  # Solo botÃ³n de zoom
                                                    ['toImage']  # Solo botÃ³n de descargar
                                                ],
                                                'toImageButtonOptions': {
                                                    'format': 'png',
                                                    'filename': 'radar_competencias',
                                                    'height': 500,
                                                    'width': 800,
                                                    'scale': 1
                                                }
                                            },
                                            style={'height': '350px'}
                                        ),
                                        
                                        html.Div(
                                            style={
                                                'display': 'flex',
                                                'justifyContent': 'space-between',
                                                'marginTop': '20px'
                                            },
                                            children=[
                                                html.Div(
                                                    style={'textAlign': 'center'},
                                                    children=[
                                                        html.Div(
                                                            "92%",
                                                            style={
                                                                'fontSize': '1.8rem',
                                                                'fontWeight': '700',
                                                                'color': '#4ecdc4',
                                                                'marginBottom': '5px'
                                                            }
                                                        ),
                                                        html.Div(
                                                            "Resistencia",
                                                            style={'color': '#ccc', 'fontSize': '0.9rem'}
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    style={'textAlign': 'center'},
                                                    children=[
                                                        html.Div(
                                                            "88%",
                                                            style={
                                                                'fontSize': '1.8rem',
                                                                'fontWeight': '700',
                                                                'color': '#ffd166',
                                                                'marginBottom': '5px'
                                                            }
                                                        ),
                                                        html.Div(
                                                            "Fuerza",
                                                            style={'color': '#ccc', 'fontSize': '0.9rem'}
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    style={'textAlign': 'center'},
                                                    children=[
                                                        html.Div(
                                                            "95%",
                                                            style={
                                                                'fontSize': '1.8rem',
                                                                'fontWeight': '700',
                                                                'color': HIGHLIGHT_COLOR,
                                                                'marginBottom': '5px'
                                                            }
                                                        ),
                                                        html.Div(
                                                            "Velocidad",
                                                            style={'color': '#ccc', 'fontSize': '0.9rem'}
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # Insights generados por IA
                        html.Div(
                            style={
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'padding': '30px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'boxShadow': '0 8px 30px rgba(0, 0, 0, 0.4)'
                            },
                            children=[
                                html.H3(
                                    "ðŸ¤– Insights Generados por IA",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'margin': '0 0 20px 0',
                                        'fontSize': '1.5rem'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'display': 'grid',
                                        'gridTemplateColumns': 'repeat(3, 1fr)',
                                        'gap': '20px'
                                    },
                                    children=[
                                        html.Div(
                                            style={
                                                'padding': '20px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                                'borderRadius': '12px',
                                                'borderLeft': f'4px solid {HIGHLIGHT_COLOR}'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'alignItems': 'center',
                                                        'gap': '10px',
                                                        'marginBottom': '10px'
                                                    },
                                                    children=[
                                                        html.I(className="bi bi-lightning-charge", style={'color': HIGHLIGHT_COLOR, 'fontSize': '1.2rem'}),
                                                        html.H4(
                                                            "Pico de Rendimiento",
                                                            style={'color': '#fff', 'margin': '0', 'fontSize': '1.1rem'}
                                                        )
                                                    ]
                                                ),
                                                html.P(
                                                    "Tu mejor momento de entrenamiento es entre 18:00-20:00 hrs. La potencia mÃ¡xima aumenta un 15% en esta ventana.",
                                                    style={'color': '#ccc', 'fontSize': '0.95rem', 'lineHeight': '1.5'}
                                                )
                                            ]
                                        ),
                                        
                                        html.Div(
                                            style={
                                                'padding': '20px',
                                                'backgroundColor': 'rgba(78, 205, 196, 0.05)',
                                                'borderRadius': '12px',
                                                'borderLeft': '4px solid #4ecdc4'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'alignItems': 'center',
                                                        'gap': '10px',
                                                        'marginBottom': '10px'
                                                    },
                                                    children=[
                                                        html.I(className="bi bi-shield-check", style={'color': '#4ecdc4', 'fontSize': '1.2rem'}),
                                                        html.H4(
                                                            "RecuperaciÃ³n Ã“ptima",
                                                            style={'color': '#fff', 'margin': '0', 'fontSize': '1.1rem'}
                                                        )
                                                    ]
                                                ),
                                                html.P(
                                                    "El sueÃ±o profundo ha aumentado un 22% tras ajustar el horario de entrenamiento vespertino.",
                                                    style={'color': '#ccc', 'fontSize': '0.95rem', 'lineHeight': '1.5'}
                                                )
                                            ]
                                        ),
                                        
                                        html.Div(
                                            style={
                                                'padding': '20px',
                                                'backgroundColor': 'rgba(255, 209, 102, 0.05)',
                                                'borderRadius': '12px',
                                                'borderLeft': '4px solid #ffd166'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'alignItems': 'center',
                                                        'gap': '10px',
                                                        'marginBottom': '10px'
                                                    },
                                                    children=[
                                                        html.I(className="bi bi-graph-up-arrow", style={'color': '#ffd166', 'fontSize': '1.2rem'}),
                                                        html.H4(
                                                            "ProyecciÃ³n",
                                                            style={'color': '#fff', 'margin': '0', 'fontSize': '1.1rem'}
                                                        )
                                                    ]
                                                ),
                                                html.P(
                                                    "Con la progresiÃ³n actual, alcanzarÃ¡s el percentil 95 de atletas de tu categorÃ­a en 6 semanas.",
                                                    style={'color': '#ccc', 'fontSize': '0.95rem', 'lineHeight': '1.5'}
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# ===============================
# OBJETIVOS LAYOUT 
# ===============================

objetivos_layout = html.Div(
    id="objetivos-container",
    className="objetivos-container",
    style={
        'backgroundColor': DARK_BACKGROUND,
        'minHeight': '100vh',
        'color': 'white',
        'fontFamily': 'Inter, sans-serif'
    },
    children=[
        # Header (igual que en inicio)
        html.Div(
            id="objetivos-header",
            className="objetivos-header",
            style={
                'backgroundColor': '#1a1a1a',
                'padding': '15px 40px',
                'borderBottom': '1px solid rgba(0, 212, 255, 0.1)',
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center'
            },
            children=[
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center'},
                    children=[
                        html.Div(
                            style={
                                'width': '40px',
                                'height': '40px',
                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                'borderRadius': '10px',
                                'border': f'2px solid {HIGHLIGHT_COLOR}',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginRight': '15px'
                            },
                            children=html.Span("A", style={'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.2rem'})
                        ),
                        html.H1(
                            "ATHLETICA",
                            style={
                                'color': HIGHLIGHT_COLOR,
                                'fontSize': '1.8rem',
                                'fontWeight': '900',
                                'letterSpacing': '2px',
                                'textShadow': f'0 0 15px rgba(0, 224, 255, 0.5)',
                                'margin': '0'
                            }
                        )
                    ]
                ),
                
                html.Div(
                    style={
                        'flex': '1',
                        'height': '1px',
                        'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                        'margin': '0 30px'
                    }
                ),
                
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'gap': '20px'},
                    children=[
                        html.Div(
                            style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'gap': '10px',
                                'cursor': 'pointer'
                            },
                            children=[
                                html.Div(
                                    id="objetivos-user-profile-avatar",
                                    style={
                                        'width': '45px',
                                        'height': '45px',
                                        'backgroundColor': HIGHLIGHT_COLOR,
                                        'borderRadius': '50%',
                                        'border': f'2px solid {HIGHLIGHT_COLOR}',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.2rem'
                                    }
                                ),
                                html.Div(
                                    style={'textAlign': 'right'},
                                    children=[
                                        html.Div(
                                            id="objetivos-user-profile-name",
                                            style={
                                                'fontWeight': '600',
                                                'fontSize': '1rem',
                                                'color': '#fff'
                                            }
                                        ),
                                        html.Div(
                                            "Atleta",
                                            style={
                                                'fontSize': '0.8rem',
                                                'color': HIGHLIGHT_COLOR,
                                                'fontWeight': '500'
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),
                    ]
                )
            ]
        ),

        # Cuerpo principal con sidebar y contenido
        html.Div(
            style={
                'display': 'flex',
                'minHeight': 'calc(100vh - 100px)'
            },
            children=[
                # Sidebar (igual que en inicio)
                html.Div(
                    id="objetivos-sidebar",
                    className="objetivos-sidebar",
                    style={
                        'width': '280px',
                        'backgroundColor': '#141414',
                        'padding': '25px 20px',
                        'borderRight': '1px solid rgba(0, 212, 255, 0.1)',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '30px'
                    },
                    children=[
                        html.Div(
                            style={
                                'padding': '20px',
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'textAlign': 'center'
                            },
                            children=[
                                html.Div(
                                    id="objetivos-sidebar-user-avatar",
                                    style={
                                        'width': '70px',
                                        'height': '70px',
                                        'backgroundColor': HIGHLIGHT_COLOR,
                                        'borderRadius': '50%',
                                        'border': f'3px solid {HIGHLIGHT_COLOR}',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.8rem',
                                        'margin': '0 auto 15px'
                                    }
                                ),
                                
                                html.Div(
                                    id="objetivos-sidebar-user-fullname",
                                    style={
                                        'fontSize': '1.3rem',
                                        'fontWeight': '700',
                                        'color': '#ffffff',
                                        'marginBottom': '5px'
                                    }
                                ),
                                
                                html.Div(
                                    id="objetivos-sidebar-user-level",
                                    style={
                                        'fontSize': '0.9rem',
                                        'color': HIGHLIGHT_COLOR,
                                        'fontWeight': '500',
                                        'marginBottom': '20px'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'height': '1px',
                                        'backgroundColor': 'rgba(255, 255, 255, 0.1)',
                                        'margin': '15px 0'
                                    }
                                ),
                                
                                html.Div(
                                    "Estado de Salud",
                                    style={
                                        'fontSize': '1rem',
                                        'fontWeight': '600',
                                        'color': '#ffffff',
                                        'marginBottom': '15px',
                                        'textAlign': 'center'
                                    }
                                ),
                                
                                html.Div(
                                    id="objetivos-health-status-dots",
                                    style={
                                        'display': 'flex',
                                        'justifyContent': 'center',
                                        'gap': '8px',
                                        'marginBottom': '12px'
                                    }
                                ),
                                
                                html.Div(
                                    id="objetivos-health-status-description",
                                    style={
                                        'fontSize': '0.8rem',
                                        'color': '#cccccc',
                                        'textAlign': 'center',
                                        'lineHeight': '1.4'
                                    }
                                )
                            ]
                        ),
                        
                        # NavegaciÃ³n
                        html.Div(
                            children=[
                                html.H4(
                                    "NavegaciÃ³n",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'marginBottom': '20px',
                                        'marginTop': '25px',
                                        'fontSize': '1.1rem',
                                        'fontWeight': '600',
                                        'paddingLeft': '10px'
                                    }
                                ),
                                html.Div(
                                    style={'display': 'flex', 'flexDirection': 'column', 'gap': '8px'},
                                    children=[
                                        html.Button(
                                            [
                                                html.I(className="bi bi-house-door", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Inicio", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-inicio-objetivos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-graph-up", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("MÃ©tricas", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-metricas-objetivos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-bullseye", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Objetivos", style={'fontSize': '0.95rem', 'fontWeight': '500'})
                                            ],
                                            id="nav-objetivos-objetivos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': f'1px solid {HIGHLIGHT_COLOR}',
                                                'color': HIGHLIGHT_COLOR,
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-egg-fried", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("NutriciÃ³n", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-nutricion-objetivos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-activity", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Entrenamientos", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-entrenamientos-objetivos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                
                # CONTENIDO PRINCIPAL DE OBJETIVOS
                html.Div(
                    className="objetivos-main",
                    style={
                        'flex': '1',
                        'padding': '40px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '30px',
                        'overflowY': 'auto'
                    },
                    children=[
                        # TÃ­tulo principal
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'marginBottom': '10px'
                            },
                            children=[
                                html.H2(
                                    "ðŸŽ¯ Objetivos Semanales",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'fontSize': '2.5rem',
                                        'fontWeight': '700',
                                        'margin': '0'
                                    }
                                ),
                                
                            ]
                        ),
                        
                        # SecciÃ³n de Objetivos Semanales
                        html.Div(
                            style={
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'padding': '30px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'boxShadow': '0 8px 30px rgba(0, 0, 0, 0.4)'
                            },
                            children=[
                                # TÃ­tulo de la secciÃ³n
                                html.H3(
                                    "Objetivos Semanales",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'fontSize': '1.8rem',
                                        'marginBottom': '30px',
                                        'borderBottom': '2px solid rgba(0, 212, 255, 0.3)',
                                        'paddingBottom': '15px'
                                    }
                                ),
                                
                                # Tarjetas de progreso
                                html.Div(
                                    style={
                                        'display': 'grid',
                                        'gridTemplateColumns': 'repeat(3, 1fr)',
                                        'gap': '30px'
                                    },
                                    children=[
                                        # Cardio
                                        html.Div(
                                            style={
                                                'backgroundColor': '#141414',
                                                'borderRadius': '12px',
                                                'padding': '25px',
                                                'border': f'1px solid {HIGHLIGHT_COLOR}',
                                                'boxShadow': f'0 0 15px rgba(0, 212, 255, 0.2)'
                                            },
                                            children=[
                                                html.H4(
                                                    "ðŸ’“ Cardio",
                                                    style={
                                                        'color': HIGHLIGHT_COLOR,
                                                        'fontSize': '1.5rem',
                                                        'marginBottom': '15px',
                                                        'display': 'flex',
                                                        'alignItems': 'center',
                                                        'gap': '10px'
                                                    }
                                                ),
                                                
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.Span(
                                                            "Progreso:",
                                                            style={'color': '#ccc', 'fontSize': '1.1rem'}
                                                        ),
                                                        html.Span(
                                                            "80%",
                                                            style={'color': HIGHLIGHT_COLOR, 'fontSize': '1.5rem', 'fontWeight': '700'}
                                                        )
                                                    ]
                                                ),
                                                
                                                # Barra de progreso
                                                html.Div(
                                                    style={
                                                        'height': '12px',
                                                        'backgroundColor': '#2b2b2b',
                                                        'borderRadius': '6px',
                                                        'overflow': 'hidden',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=html.Div(
                                                        style={
                                                            'width': '80%',
                                                            'height': '100%',
                                                            'backgroundColor': HIGHLIGHT_COLOR,
                                                            'borderRadius': '6px',
                                                            'boxShadow': f'0 0 10px {HIGHLIGHT_COLOR}'
                                                        }
                                                    )
                                                ),
                                                
                                                # Detalles del objetivo
                                                html.Div(
                                                    style={
                                                        'color': '#ccc',
                                                        'fontSize': '1rem',
                                                        'marginTop': '15px',
                                                        'paddingTop': '15px',
                                                        'borderTop': '1px solid #2b2b2b'
                                                    },
                                                    children=[
                                                        html.P("âœ… 4 de 5 sesiones completadas", style={'margin': '5px 0'}),
                                                        html.P("ðŸŽ¯ Objetivo: 5 sesiones de cardio", style={'margin': '5px 0'}),
                                                        html.P("ðŸ“… PrÃ³xima: MaÃ±ana 8:00 AM", style={'margin': '5px 0', 'color': HIGHLIGHT_COLOR})
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # Fuerza
                                        html.Div(
                                            style={
                                                'backgroundColor': '#141414',
                                                'borderRadius': '12px',
                                                'padding': '25px',
                                                'border': '1px solid #ffd166',
                                                'boxShadow': '0 0 15px rgba(255, 209, 102, 0.2)'
                                            },
                                            children=[
                                                html.H4(
                                                    "ðŸ’ª Fuerza",
                                                    style={
                                                        'color': '#ffd166',
                                                        'fontSize': '1.5rem',
                                                        'marginBottom': '15px',
                                                        'display': 'flex',
                                                        'alignItems': 'center',
                                                        'gap': '10px'
                                                    }
                                                ),
                                                
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.Span(
                                                            "Progreso:",
                                                            style={'color': '#ccc', 'fontSize': '1.1rem'}
                                                        ),
                                                        html.Span(
                                                            "67%",
                                                            style={'color': '#ffd166', 'fontSize': '1.5rem', 'fontWeight': '700'}
                                                        )
                                                    ]
                                                ),
                                                
                                                # Barra de progreso
                                                html.Div(
                                                    style={
                                                        'height': '12px',
                                                        'backgroundColor': '#2b2b2b',
                                                        'borderRadius': '6px',
                                                        'overflow': 'hidden',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=html.Div(
                                                        style={
                                                            'width': '67%',
                                                            'height': '100%',
                                                            'backgroundColor': '#ffd166',
                                                            'borderRadius': '6px',
                                                            'boxShadow': '0 0 10px #ffd166'
                                                        }
                                                    )
                                                ),
                                                
                                                # Detalles del objetivo
                                                html.Div(
                                                    style={
                                                        'color': '#ccc',
                                                        'fontSize': '1rem',
                                                        'marginTop': '15px',
                                                        'paddingTop': '15px',
                                                        'borderTop': '1px solid #2b2b2b'
                                                    },
                                                    children=[
                                                        html.P("âœ… 2 de 3 sesiones completadas", style={'margin': '5px 0'}),
                                                        html.P("ðŸŽ¯ Objetivo: 3 sesiones de fuerza", style={'margin': '5px 0'}),
                                                        html.P("ðŸ“… PrÃ³xima: Hoy 19:00 PM", style={'margin': '5px 0', 'color': '#ffd166'})
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # Flexibilidad
                                        html.Div(
                                            style={
                                                'backgroundColor': '#141414',
                                                'borderRadius': '12px',
                                                'padding': '25px',
                                                'border': '1px solid #4ecdc4',
                                                'boxShadow': '0 0 15px rgba(78, 205, 196, 0.2)'
                                            },
                                            children=[
                                                html.H4(
                                                    "ðŸ§˜ Flexibilidad",
                                                    style={
                                                        'color': '#4ecdc4',
                                                        'fontSize': '1.5rem',
                                                        'marginBottom': '15px',
                                                        'display': 'flex',
                                                        'alignItems': 'center',
                                                        'gap': '10px'
                                                    }
                                                ),
                                                
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.Span(
                                                            "Progreso:",
                                                            style={'color': '#ccc', 'fontSize': '1.1rem'}
                                                        ),
                                                        html.Span(
                                                            "75%",
                                                            style={'color': '#4ecdc4', 'fontSize': '1.5rem', 'fontWeight': '700'}
                                                        )
                                                    ]
                                                ),
                                                
                                                # Barra de progreso
                                                html.Div(
                                                    style={
                                                        'height': '12px',
                                                        'backgroundColor': '#2b2b2b',
                                                        'borderRadius': '6px',
                                                        'overflow': 'hidden',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=html.Div(
                                                        style={
                                                            'width': '75%',
                                                            'height': '100%',
                                                            'backgroundColor': '#4ecdc4',
                                                            'borderRadius': '6px',
                                                            'boxShadow': '0 0 10px #4ecdc4'
                                                        }
                                                    )
                                                ),
                                                
                                                # Detalles del objetivo
                                                html.Div(
                                                    style={
                                                        'color': '#ccc',
                                                        'fontSize': '1rem',
                                                        'marginTop': '15px',
                                                        'paddingTop': '15px',
                                                        'borderTop': '1px solid #2b2b2b'
                                                    },
                                                    children=[
                                                        html.P("âœ… 3 de 4 sesiones completadas", style={'margin': '5px 0'}),
                                                        html.P("ðŸŽ¯ Objetivo: 4 sesiones de flexibilidad", style={'margin': '5px 0'}),
                                                        html.P("ðŸ“… PrÃ³xima: MaÃ±ana 7:00 AM", style={'margin': '5px 0', 'color': '#4ecdc4'})
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                
                                # Separador
                                html.Hr(style={'borderColor': '#2b2b2b', 'margin': '40px 0'}),
                                
                                # SecciÃ³n de Objetivos de Fitness (DINÃMICA)
                                html.Div(
                                    id="fitness-goals-container",
                                    children=[
                                        html.H3(
                                            "ðŸ‹ï¸ Objetivos de Fitness",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'fontSize': '1.8rem',
                                                'marginBottom': '25px'
                                            }
                                        ),
                                        
                                        # Lista de objetivos de fitness (se actualizarÃ¡ dinÃ¡micamente)
                                        html.Ul(
                                            id="fitness-goals-list",
                                            style={'listStyleType': 'none', 'padding': '0'},
                                            children=[
                                                # Los objetivos se cargarÃ¡n aquÃ­ dinÃ¡micamente
                                            ]
                                        )
                                    ]
                                ),
                                
                                # Separador
                                html.Hr(style={'borderColor': '#2b2b2b', 'margin': '40px 0'}),
                                
                                # SecciÃ³n de Objetivos de Salud (DINÃMICA)
                                html.Div(
                                    id="health-goals-container",
                                    children=[
                                        html.H3(
                                            "â¤ï¸ Objetivos de Salud",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'fontSize': '1.8rem',
                                                'marginBottom': '25px'
                                            }
                                        ),
                                        
                                        # Lista de objetivos de salud (se actualizarÃ¡ dinÃ¡micamente)
                                        html.Ul(
                                            id="health-goals-list",
                                            style={'listStyleType': 'none', 'padding': '0'},
                                            children=[
                                                # Los objetivos se cargarÃ¡n aquÃ­ dinÃ¡micamente
                                            ]
                                        )
                                    ]
                                ),
                                
                                # BotÃ³n para agregar nuevo objetivo
                                html.Div(
                                    style={
                                        'marginTop': '40px',
                                        'textAlign': 'center'
                                    },
                                    children=dbc.Button(
                                        [
                                            html.I(className="bi bi-plus-circle me-2"),
                                            "Agregar Nuevo Objetivo"
                                        ],
                                        id="btn-agregar-objetivo",
                                        className="auth-btn",
                                        style={
                                            'backgroundColor': HIGHLIGHT_COLOR,
                                            'border': 'none',
                                            'fontWeight': '600',
                                            'padding': '15px 30px',
                                            'borderRadius': '12px',
                                            'fontSize': '1.1rem',
                                            'color': '#0a0a0a',
                                            'transition': 'all 0.3s ease'
                                        }
                                    )
                                )
                            ]
                        ),
                        
                        # Resumen de progreso general
                        html.Div(
                            style={
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'padding': '25px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                            },
                            children=[
                                html.H3(
                                    "ðŸ“ˆ Progreso General",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'marginBottom': '20px',
                                        'fontSize': '1.5rem'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'display': 'grid',
                                        'gridTemplateColumns': 'repeat(3, 1fr)',
                                        'gap': '20px'
                                    },
                                    children=[
                                        html.Div(
                                            style={'textAlign': 'center'},
                                            children=[
                                                html.Div(
                                                    id="progreso-total-percent",  # AÃ‘ADE ESTE ID
                                                    children="74%",  # CAMBIA ESTO
                                                    style={
                                                        'fontSize': '2.5rem',
                                                        'fontWeight': '700',
                                                        'color': HIGHLIGHT_COLOR,
                                                        'marginBottom': '10px'
                                                    }
                                                ),
                                                html.Div(
                                                    "Progreso Total",
                                                    style={'color': '#ccc', 'fontSize': '1rem'}
                                                )
                                            ]
                                        ),
                                        
                                        html.Div(
                                            style={'textAlign': 'center'},
                                            children=[
                                                html.Div(
                                                    id="objetivos-activos-count",  # AÃ‘ADE ESTE ID
                                                    children="9",  # CAMBIA ESTO
                                                    style={
                                                        'fontSize': '2.5rem',
                                                        'fontWeight': '700',
                                                        'color': '#4ecdc4',
                                                        'marginBottom': '10px'
                                                    }
                                                ),
                                                html.Div(
                                                    "Objetivos Activos",
                                                    style={'color': '#ccc', 'fontSize': '1rem'}
                                                )
                                            ]
                                        ),
                                        
                                        html.Div(
                                            style={'textAlign': 'center'},
                                            children=[
                                                html.Div(
                                                    "23",
                                                    style={
                                                        'fontSize': '2.5rem',
                                                        'fontWeight': '700',
                                                        'color': '#ffd166',
                                                        'marginBottom': '10px'
                                                    }
                                                ),
                                                html.Div(
                                                    "DÃ­as Consecutivos",
                                                    style={'color': '#ccc', 'fontSize': '1rem'}
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # MODAL PARA AGREGAR NUEVOS OBJETIVOS (AGREGADO) - VERSIÃ“N CORREGIDA
                        dbc.Modal(
                            [
                                dbc.ModalHeader(
                                    html.H4("ðŸŽ¯ Agregar Nuevo Objetivo", style={'color': HIGHLIGHT_COLOR}),
                                    close_button=True,
                                    style={'backgroundColor': '#1a1a1a', 'borderBottom': '1px solid #2b2b2b'}
                                ),
                                dbc.ModalBody(
                                    style={'backgroundColor': '#1a1a1a', 'color': 'white'},
                                    children=[
                                        # Paso 1: Elegir tipo de objetivo
                                        html.Div(
                                            id="choose-goal-type",
                                            children=[
                                                html.P("Â¿QuÃ© tipo de objetivo quieres agregar?", 
                                                       style={'color': '#ccc', 'marginBottom': '20px', 'fontSize': '1.1rem'}),
                                                
                                                html.Div(
                                                    style={
                                                        'display': 'grid',
                                                        'gridTemplateColumns': 'repeat(2, 1fr)',
                                                        'gap': '20px',
                                                        'marginBottom': '30px'
                                                    },
                                                    children=[
                                                        # OpciÃ³n Salud - AÃ‘ADIDO n_clicks=0
                                                 
                                                    html.Button(
                                                     [
                                                        html.Div("â¤ï¸", style={'fontSize': '2.5rem', 'marginBottom': '10px'}),
                                                        html.H5("Salud", style={'color': HIGHLIGHT_COLOR, 'marginBottom': '5px'}),
                                                        html.P("Frecuencia cardÃ­aca, sueÃ±o, HRV, etc.", 
                                                        style={'color': '#ccc', 'fontSize': '0.9rem'})
                                                    ],
                                                        id="btn-health-goal",
                                                        n_clicks=0,
                                                        style={
                                                        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                        'border': '1px solid rgba(0, 212, 255, 0.3)',
                                                        'borderRadius': '12px',
                                                        'padding': '20px',
                                                        'cursor': 'pointer',
                                                        'transition': 'all 0.3s ease',
                                                        'color': 'white',
                                                        'textAlign': 'center'
                                                            }
                                                    ),

# OpciÃ³n Fitness - AÃ‘ADIDO n_clicks=0 CORREGIDO
html.Button(
    [
        html.Div("ðŸ’ª", style={'fontSize': '2.5rem', 'marginBottom': '10px'}),
        html.H5("Fitness", style={'color': '#ffd166', 'marginBottom': '5px'}),
        html.P("Peso, correr, fuerza, flexibilidad", 
               style={'color': '#ccc', 'fontSize': '0.9rem'})
    ],
    id="btn-fitness-goal",
    n_clicks=0,  # Â¡AGREGADO!
    style={
        'backgroundColor': 'rgba(255, 209, 102, 0.1)',
        'border': '1px solid rgba(255, 209, 102, 0.3)',
        'borderRadius': '12px',
        'padding': '20px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'color': 'white',
        'textAlign': 'center'
    }
)
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # Paso 2: Formulario para escribir el objetivo (inicialmente oculto)
                                        html.Div(
                                            id="goal-form-container",
                                            style={'display': 'none'},
                                            children=[
                                                html.Div(
                                                    id="goal-type-header",
                                                    style={
                                                        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                        'padding': '15px',
                                                        'borderRadius': '10px',
                                                        'marginBottom': '20px',
                                                        'display': 'flex',
                                                        'alignItems': 'center',
                                                        'gap': '10px'
                                                    },
                                                    children=[
                                                        html.Span("â¤ï¸", id="goal-type-icon", style={'fontSize': '1.5rem'}),
                                                        html.Div(
                                                            [
                                                                html.Div("Objetivo de:", style={'color': '#ccc', 'fontSize': '0.9rem'}),
                                                                html.Div("Salud", id="goal-type-text", style={'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.1rem'})
                                                            ]
                                                        )
                                                    ]
                                                ),
                                                
                                                # Formulario
                                                html.Div(
                                                    style={'marginBottom': '20px'},
                                                    children=[
                                                        html.Label("Nombre del objetivo", 
                                                                  style={'color': '#ccc', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                                        dcc.Input(
                                                            id="goal-name-input",
                                                            type="text",
                                                            placeholder="Ej: Reducir frecuencia cardÃ­aca en reposo",
                                                            style={
                                                                'width': '100%',
                                                                'padding': '12px 15px',
                                                                'backgroundColor': '#2b2b2b',
                                                                'border': '1px solid #444',
                                                                'borderRadius': '8px',
                                                                'color': 'white',
                                                                'fontSize': '1rem'
                                                            }
                                                        )
                                                    ]
                                                ),
                                                
                                                html.Div(
                                                    style={'marginBottom': '20px'},
                                                    children=[
                                                        html.Label("DescripciÃ³n (opcional)", 
                                                                  style={'color': '#ccc', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                                        dcc.Textarea(
                                                            id="goal-description-input",
                                                            placeholder="Describe tu objetivo con mÃ¡s detalle...",
                                                            style={
                                                                'width': '100%',
                                                                'height': '100px',
                                                                'padding': '12px 15px',
                                                                'backgroundColor': '#2b2b2b',
                                                                'border': '1px solid #444',
                                                                'borderRadius': '8px',
                                                                'color': 'white',
                                                                'fontSize': '1rem',
                                                                'resize': 'vertical'
                                                            }
                                                        )
                                                    ]
                                                ),
                                                
                                                html.Div(
                                                    style={
                                                        'display': 'grid',
                                                        'gridTemplateColumns': 'repeat(2, 1fr)',
                                                        'gap': '15px',
                                                        'marginBottom': '25px'
                                                    },
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.Label("Valor objetivo", 
                                                                          style={'color': '#ccc', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                                                dcc.Input(
                                                                    id="goal-target-input",
                                                                    type="text",
                                                                    placeholder="Ej: 65 bpm",
                                                                    style={
                                                                        'width': '100%',
                                                                        'padding': '12px 15px',
                                                                        'backgroundColor': '#2b2b2b',
                                                                        'border': '1px solid #444',
                                                                        'borderRadius': '8px',
                                                                        'color': 'white',
                                                                        'fontSize': '1rem'
                                                                    }
                                                                )
                                                            ]
                                                        ),
                                                        
                                                        html.Div(
                                                            children=[
                                                                html.Label("Plazo", 
                                                                          style={'color': '#ccc', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                                                dcc.Dropdown(
                                                                    id="goal-deadline-dropdown",
                                                                    options=[
                                                                        {'label': '1 semana', 'value': '1_week'},
                                                                        {'label': '2 semanas', 'value': '2_weeks'},
                                                                        {'label': '1 mes', 'value': '1_month'},
                                                                        {'label': '3 meses', 'value': '3_months'},
                                                                        {'label': '6 meses', 'value': '6_months'}
                                                                    ],
                                                                    placeholder="Selecciona un plazo",
                                                                    style={
                                                                        'backgroundColor': '#2b2b2b',
                                                                        'color': 'white',
                                                                        'border': '1px solid #444'
                                                                    },
                                                                    className="dbc dbc-row-selectable"
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                ),
                                                
                                                # BotÃ³n para volver atrÃ¡s
                                                html.Div(
                                                    style={'textAlign': 'center', 'marginTop': '20px'},
                                                    children=html.Button(
                                                        "â† Volver a elegir tipo",
                                                        id="btn-back-to-choose",
                                                        style={
                                                            'backgroundColor': 'transparent',
                                                            'border': '1px solid #444',
                                                            'color': '#ccc',
                                                            'padding': '10px 20px',
                                                            'borderRadius': '8px',
                                                            'cursor': 'pointer',
                                                            'fontSize': '0.9rem',
                                                            'transition': 'all 0.3s ease'
                                                        }
                                                    )
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                dbc.ModalFooter(
                                    style={'backgroundColor': '#1a1a1a', 'borderTop': '1px solid #2b2b2b'},
                                    children=[
                                        dbc.Button(
                                            "Cancelar",
                                            id="btn-cancel-goal",
                                            color="secondary",
                                            className="me-2",
                                            style={'borderRadius': '8px'}
                                        ),
                                        dbc.Button(
                                            "Agregar Objetivo",
                                            id="btn-submit-goal",
                                            color="primary",
                                            style={'backgroundColor': HIGHLIGHT_COLOR, 'borderColor': HIGHLIGHT_COLOR, 'borderRadius': '8px'}
                                        )
                                    ]
                                )
                            ],
                            id="modal-add-goal",
                            size="lg",
                            is_open=False,
                            centered=True,
                            backdrop=True,
                            style={'backgroundColor': 'rgba(0,0,0,0.7)'}
                        )
                    ]
                )
            ]
        )
    ]
)

# ===============================
# NUTRICIÃ“N LAYOUT (COMPLETO - BASADO EN LA IMAGEN)
# ===============================

nutricion_layout = html.Div(
    id="nutricion-container",
    className="nutricion-container",
    style={
        'backgroundColor': DARK_BACKGROUND,
        'minHeight': '100vh',
        'color': 'white',
        'fontFamily': 'Inter, sans-serif'
    },
    children=[
        # Header (igual que en otras pÃ¡ginas)
        html.Div(
            id="nutricion-header",
            className="nutricion-header",
            style={
                'backgroundColor': '#1a1a1a',
                'padding': '15px 40px',
                'borderBottom': '1px solid rgba(0, 212, 255, 0.1)',
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center'
            },
            children=[
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center'},
                    children=[
                        html.Div(
                            style={
                                'width': '40px',
                                'height': '40px',
                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                'borderRadius': '10px',
                                'border': f'2px solid {HIGHLIGHT_COLOR}',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginRight': '15px'
                            },
                            children=html.Span("A", style={'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.2rem'})
                        ),
                        html.H1(
                            "ATHLETICA",
                            style={
                                'color': HIGHLIGHT_COLOR,
                                'fontSize': '1.8rem',
                                'fontWeight': '900',
                                'letterSpacing': '2px',
                                'textShadow': f'0 0 15px rgba(0, 224, 255, 0.5)',
                                'margin': '0'
                            }
                        )
                    ]
                ),
                
                html.Div(
                    style={
                        'flex': '1',
                        'height': '1px',
                        'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                        'margin': '0 30px'
                    }
                ),
                
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'gap': '20px'},
                    children=[
                        html.Div(
                            style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'gap': '10px',
                                'cursor': 'pointer'
                            },
                            children=[
                                html.Div(
                                    id="nutricion-user-profile-avatar",
                                    style={
                                        'width': '45px',
                                        'height': '45px',
                                        'backgroundColor': HIGHLIGHT_COLOR,
                                        'borderRadius': '50%',
                                        'border': f'2px solid {HIGHLIGHT_COLOR}',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.2rem'
                                    }
                                ),
                                html.Div(
                                    style={'textAlign': 'right'},
                                    children=[
                                        html.Div(
                                            id="nutricion-user-profile-name",
                                            style={
                                                'fontWeight': '600',
                                                'fontSize': '1rem',
                                                'color': '#fff'
                                            }
                                        ),
                                        html.Div(
                                            "Atleta",
                                            style={
                                                'fontSize': '0.8rem',
                                                'color': HIGHLIGHT_COLOR,
                                                'fontWeight': '500'
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),
                    ]
                )
            ]
        ),

        # Cuerpo principal con sidebar y contenido
        html.Div(
            style={
                'display': 'flex',
                'minHeight': 'calc(100vh - 100px)'
            },
            children=[
                # Sidebar (igual que en otras pÃ¡ginas)
                html.Div(
                    id="nutricion-sidebar",
                    className="nutricion-sidebar",
                    style={
                        'width': '280px',
                        'backgroundColor': '#141414',
                        'padding': '25px 20px',
                        'borderRight': '1px solid rgba(0, 212, 255, 0.1)',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '30px'
                    },
                    children=[
                        html.Div(
                            style={
                                'padding': '20px',
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'textAlign': 'center'
                            },
                            children=[
                                html.Div(
                                    id="nutricion-sidebar-user-avatar",
                                    style={
                                        'width': '70px',
                                        'height': '70px',
                                        'backgroundColor': HIGHLIGHT_COLOR,
                                        'borderRadius': '50%',
                                        'border': f'3px solid {HIGHLIGHT_COLOR}',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.8rem',
                                        'margin': '0 auto 15px'
                                    }
                                ),
                                
                                html.Div(
                                    id="nutricion-sidebar-user-fullname",
                                    style={
                                        'fontSize': '1.3rem',
                                        'fontWeight': '700',
                                        'color': '#ffffff',
                                        'marginBottom': '5px'
                                    }
                                ),
                                
                                html.Div(
                                    id="nutricion-sidebar-user-level",
                                    style={
                                        'fontSize': '0.9rem',
                                        'color': HIGHLIGHT_COLOR,
                                        'fontWeight': '500',
                                        'marginBottom': '20px'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'height': '1px',
                                        'backgroundColor': 'rgba(255, 255, 255, 0.1)',
                                        'margin': '15px 0'
                                    }
                                ),
                                
                                html.Div(
                                    "Estado de Salud",
                                    style={
                                        'fontSize': '1rem',
                                        'fontWeight': '600',
                                        'color': '#ffffff',
                                        'marginBottom': '15px',
                                        'textAlign': 'center'
                                    }
                                ),
                                
                                html.Div(
                                    id="nutricion-health-status-dots",
                                    style={
                                        'display': 'flex',
                                        'justifyContent': 'center',
                                        'gap': '8px',
                                        'marginBottom': '12px'
                                    }
                                ),
                                
                                html.Div(
                                    id="nutricion-health-status-description",
                                    style={
                                        'fontSize': '0.8rem',
                                        'color': '#cccccc',
                                        'textAlign': 'center',
                                        'lineHeight': '1.4'
                                    }
                                )
                            ]
                        ),
                        
                        # NavegaciÃ³n
                        html.Div(
                            children=[
                                html.H4(
                                    "NavegaciÃ³n",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'marginBottom': '20px',
                                        'marginTop': '25px',
                                        'fontSize': '1.1rem',
                                        'fontWeight': '600',
                                        'paddingLeft': '10px'
                                    }
                                ),
                                html.Div(
                                    style={'display': 'flex', 'flexDirection': 'column', 'gap': '8px'},
                                    children=[
                                        html.Button(
                                            [
                                                html.I(className="bi bi-house-door", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Inicio", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-inicio-nutricion",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-graph-up", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("MÃ©tricas", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-metricas-nutricion",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-bullseye", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Objetivos", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-objetivos-nutricion",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-egg-fried", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("NutriciÃ³n", style={'fontSize': '0.95rem', 'fontWeight': '500'})
                                            ],
                                            id="nav-nutricion-nutricion",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': f'1px solid {HIGHLIGHT_COLOR}',
                                                'color': HIGHLIGHT_COLOR,
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),

                                        html.Button(
                                            [
                                                html.I(className="bi bi-activity", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Entrenamientos", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-entrenamientos-nutricion",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                
                # CONTENIDO PRINCIPAL DE NUTRICIÃ“N (BASADO EN LA IMAGEN)
                html.Div(
                    className="nutricion-main",
                    style={
                        'flex': '1',
                        'padding': '40px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '30px',
                        'overflowY': 'auto'
                    },
                    children=[
                        # TÃ­tulo principal
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'marginBottom': '10px'
                            },
                            children=[
                                html.H2(
                                    "ðŸ¥— NutriciÃ³n y AlimentaciÃ³n",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'fontSize': '2.5rem',
                                        'fontWeight': '700',
                                        'margin': '0'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'color': '#ccc',
                                        'fontSize': '1rem'
                                    },
                                    children=f"Hoy, {datetime.now().strftime('%d/%m/%Y')}"
                                )
                            ]
                        ),
                        
                        # Resumen de calorÃ­as (Parte superior)
                        html.Div(
                            style={
                                'display': 'grid',
                                'gridTemplateColumns': 'repeat(4, 1fr)',
                                'gap': '25px',
                                'marginBottom': '30px'
                            },
                            children=[
                                # Total de calorÃ­as
                                html.Div(
                                    style={
                                        'backgroundColor': '#1a1a1a',
                                        'borderRadius': '15px',
                                        'padding': '25px',
                                        'border': '1px solid rgba(0, 212, 255, 0.1)',
                                        'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)',
                                        'gridColumn': 'span 2',
                                        'textAlign': 'center'
                                    },
                                    children=[
                                        html.H3(
                                            id="calorias-total",
                                            children="2847",
                                            style={
                                                'fontSize': '4rem',
                                                'fontWeight': '700',
                                                'color': HIGHLIGHT_COLOR,
                                                'marginBottom': '10px'
                                            }
                                        ),
                                        html.Div(
                                            "de 3000 kcal objetivo",
                                            style={
                                                'color': '#ccc',
                                                'fontSize': '1.2rem',
                                                'marginBottom': '15px'
                                            }
                                        ),
                                        html.Div(
                                            html.Div(
                                                style={
                                                    'width': '75%',  # 2847/3800 â‰ˆ 75%
                                                    'height': '100%',
                                                    'backgroundColor': HIGHLIGHT_COLOR,
                                                    'borderRadius': '5px',
                                                    'transition': 'width 0.5s ease'
                                                }
                                            ),
                                            style={
                                                'width': '100%',
                                                'height': '10px',
                                                'backgroundColor': '#2b2b2b',
                                                'borderRadius': '5px',
                                                'overflow': 'hidden'
                                            }
                                        )
                                    ]
                                ),
                                
                                # Carbohidratos
                                html.Div(
                                    style={
                                        'backgroundColor': '#1a1a1a',
                                        'borderRadius': '15px',
                                        'padding': '25px',
                                        'border': '1px solid rgba(0, 212, 255, 0.1)',
                                        'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)',
                                        'textAlign': 'center'
                                    },
                                    children=[
                                        html.H3(
                                            id="carbohidratos-total",
                                            children="180g",
                                            style={
                                                'fontSize': '2.5rem',
                                                'fontWeight': '700',
                                                'color': '#4ecdc4',
                                                'marginBottom': '10px'
                                            }
                                        ),
                                        html.Div(
                                            "Carbohidratos",
                                            style={
                                                'color': '#ccc',
                                                'fontSize': '1.1rem'
                                            }
                                        )
                                    ]
                                ),
                                
                                # ProteÃ­nas
                                html.Div(
                                    style={
                                        'backgroundColor': '#1a1a1a',
                                        'borderRadius': '15px',
                                        'padding': '25px',
                                        'border': '1px solid rgba(0, 212, 255, 0.1)',
                                        'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)',
                                        'textAlign': 'center'
                                    },
                                    children=[
                                        html.H3(
                                            id="proteinas-total",
                                            children="95g",
                                            style={
                                                'fontSize': '2.5rem',
                                                'fontWeight': '700',
                                                'color': '#ffd166',
                                                'marginBottom': '10px'
                                            }
                                        ),
                                        html.Div(
                                            "ProteÃ­nas",
                                            style={
                                                'color': '#ccc',
                                                'fontSize': '1.1rem'
                                            }
                                        )
                                    ]
                                ),
                                
                                # Grasas
                                html.Div(
                                    style={
                                        'backgroundColor': '#1a1a1a',
                                        'borderRadius': '15px',
                                        'padding': '25px',
                                        'border': '1px solid rgba(0, 212, 255, 0.1)',
                                        'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)',
                                        'textAlign': 'center'
                                    },
                                    children=[
                                        html.H3(
                                            id="grasas-total",
                                            children="65g",
                                            style={
                                                'fontSize': '2.5rem',
                                                'fontWeight': '700',
                                                'color': '#ff6b6b',
                                                'marginBottom': '10px'
                                            }
                                        ),
                                        html.Div(
                                            "Grasas",
                                            style={
                                                'color': '#ccc',
                                                'fontSize': '1.1rem'
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # SecciÃ³n principal: Registro de comidas + HidrataciÃ³n
                        html.Div(
                            style={
                                'display': 'grid',
                                'gridTemplateColumns': '3fr 2fr',
                                'gap': '30px'
                            },
                            children=[
                                # COLUMNA IZQUIERDA: Registro de Comidas
                                html.Div(
                                    style={
                                        'backgroundColor': '#1a1a1a',
                                        'borderRadius': '15px',
                                        'padding': '30px',
                                        'border': '1px solid rgba(0, 212, 255, 0.1)',
                                        'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                                    },
                                    children=[
                                        html.H3(
                                            "ðŸ“ Registro de Comidas",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'fontSize': '1.8rem',
                                                'marginBottom': '30px',
                                                'borderBottom': '2px solid rgba(0, 212, 255, 0.3)',
                                                'paddingBottom': '15px'
                                            }
                                        ),
                                        
                                        # Desayuno
                                        html.Div(
                                            style={
                                                'marginBottom': '25px',
                                                'paddingBottom': '25px',
                                                'borderBottom': '1px solid #2b2b2b'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.H4(
                                                            "ðŸ³ Desayuno",
                                                            style={
                                                                'color': '#fff',
                                                                'fontSize': '1.4rem',
                                                                'margin': '0'
                                                            }
                                                        ),
                                                        html.Div(
                                                            "08:00",
                                                            style={
                                                                'color': HIGHLIGHT_COLOR,
                                                                'fontSize': '1.1rem',
                                                                'fontWeight': '500'
                                                            }
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    id="meal-list-desayuno",
                                                    children=[
                                                        html.Div(
                                                            "â€¢ Avena con frutas y nueces",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        ),
                                                        html.Div(
                                                            "â€¢ CafÃ© negro sin azÃºcar",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # Almuerzo
                                        html.Div(
                                            style={
                                                'marginBottom': '25px',
                                                'paddingBottom': '25px',
                                                'borderBottom': '1px solid #2b2b2b'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.H4(
                                                            "ðŸ¥— Almuerzo",
                                                            style={
                                                                'color': '#fff',
                                                                'fontSize': '1.4rem',
                                                                'margin': '0'
                                                            }
                                                        ),
                                                        html.Div(
                                                            "12:30",
                                                            style={
                                                                'color': HIGHLIGHT_COLOR,
                                                                'fontSize': '1.1rem',
                                                                'fontWeight': '500'
                                                            }
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    id="meal-list-almuerzo",
                                                    children=[
                                                        html.Div(
                                                            "â€¢ Ensalada de pollo a la parrilla",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        ),
                                                        html.Div(
                                                            "â€¢ Quinoa y vegetales al vapor",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        ),
                                                        html.Div(
                                                            "â€¢ Agua con limÃ³n",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # Cena
                                        html.Div(
                                            style={
                                                'marginBottom': '30px',
                                                'paddingBottom': '25px',
                                                'borderBottom': '1px solid #2b2b2b'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.H4(
                                                            "ðŸ² Cena",
                                                            style={
                                                                'color': '#fff',
                                                                'fontSize': '1.4rem',
                                                                'margin': '0'
                                                            }
                                                        ),
                                                        html.Div(
                                                            "18:00",
                                                            style={
                                                                'color': HIGHLIGHT_COLOR,
                                                                'fontSize': '1.1rem',
                                                                'fontWeight': '500'
                                                            }
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    id="meal-list-cena",
                                                    children=[
                                                        html.Div(
                                                            "â€¢ SalmÃ³n a la plancha",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        ),
                                                        html.Div(
                                                            "â€¢ EspÃ¡rragos y brÃ³coli",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        ),
                                                        html.Div(
                                                            "â€¢ Batido de proteÃ­nas",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # Snacks
                                        html.Div(
                                            style={
                                                'marginBottom': '30px'
                                            },
                                            children=[
                                                html.H4(
                                                    "ðŸŽ Snacks",
                                                    style={
                                                        'color': '#fff',
                                                        'fontSize': '1.4rem',
                                                        'margin': '0 0 15px 0'
                                                    }
                                                ),
                                                html.Div(
                                                    id="meal-list-snacks",
                                                    children=[
                                                        html.Div(
                                                            "â€¢ Manzana verde (10:30)",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        ),
                                                        html.Div(
                                                            "â€¢ Yogur griego con almendras (16:00)",
                                                            style={'color': '#ccc', 'marginBottom': '5px'}
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # BotÃ³n para agregar comida
                                        html.Div(
                                            style={
                                                'textAlign': 'center',
                                                'marginTop': '20px'
                                            },
                                            children=dbc.Button(
                                                [
                                                    html.I(className="bi bi-plus-circle me-2"),
                                                    "Agregar Comida"
                                                ],
                                                id="btn-agregar-comida",
                                                className="auth-btn",
                                                style={
                                                    'backgroundColor': HIGHLIGHT_COLOR,
                                                    'border': 'none',
                                                    'fontWeight': '600',
                                                    'padding': '15px 30px',
                                                    'borderRadius': '12px',
                                                    'fontSize': '1.1rem',
                                                    'color': '#0a0a0a',
                                                    'transition': 'all 0.3s ease',
                                                    'width': '100%'
                                                }
                                            )
                                        )
                                    ]
                                ),
                                
                                # COLUMNA DERECHA: HidrataciÃ³n
                                html.Div(
                                    style={
                                        'backgroundColor': '#1a1a1a',
                                        'borderRadius': '15px',
                                        'padding': '30px',
                                        'border': '1px solid rgba(0, 212, 255, 0.1)',
                                        'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                                    },
                                    children=[
                                        html.H3(
                                            "ðŸ’§ HidrataciÃ³n",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'fontSize': '1.8rem',
                                                'marginBottom': '30px',
                                                'borderBottom': '2px solid rgba(0, 212, 255, 0.3)',
                                                'paddingBottom': '15px'
                                            }
                                        ),
                                        
                                        # Progreso de hidrataciÃ³n
                                        html.Div(
                                            style={
                                                'textAlign': 'center',
                                                'marginBottom': '30px'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'position': 'relative',
                                                        'width': '200px',
                                                        'height': '200px',
                                                        'margin': '0 auto 20px'
                                                    },
                                                    children=[
                                                        # CÃ­rculo de fondo
                                                        html.Div(
                                                            style={
                                                                'position': 'absolute',
                                                                'top': '0',
                                                                'left': '0',
                                                                'width': '100%',
                                                                'height': '100%',
                                                                'borderRadius': '50%',
                                                                'border': '10px solid #2b2b2b',
                                                                'boxSizing': 'border-box'
                                                            }
                                                        ),
                                                        # CÃ­rculo de progreso (70% = 2.1L/3L)
                                                        html.Div(
                                                            id="hidratacion-circle-progress",
                                                            style={
                                                                'position': 'absolute',
                                                                'top': '0',
                                                                'left': '0',
                                                                'width': '100%',
                                                                'height': '100%',
                                                                'borderRadius': '50%',
                                                                'border': '10px solid transparent',
                                                                'borderTop': f'10px solid {HIGHLIGHT_COLOR}',
                                                                'borderRight': f'10px solid {HIGHLIGHT_COLOR}',
                                                                'transform': 'rotate(252deg)',  # 70% de 360Â° = 252Â°
                                                                'boxSizing': 'border-box'
                                                            }
                                                        ),
                                                        # Texto en el centro
                                                        html.Div(
                                                            style={
                                                                'position': 'absolute',
                                                                'top': '50%',
                                                                'left': '50%',
                                                                'transform': 'translate(-50%, -50%)',
                                                                'textAlign': 'center'
                                                            },
                                                            children=[
                                                                html.Div(
                                                                    id="hidratacion-progreso",
                                                                    children="2.1L",
                                                                    style={
                                                                        'fontSize': '2.5rem',
                                                                        'fontWeight': '700',
                                                                        'color': HIGHLIGHT_COLOR,
                                                                        'marginBottom': '5px'
                                                                    }
                                                                ),
                                                                html.Div(
                                                                    id="hidratacion-texto",
                                                                    children="de 3L objetivo",
                                                                    style={
                                                                        'color': '#ccc',
                                                                        'fontSize': '1rem'
                                                                    }
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                ),
                                                
                                                html.Div(
                                                    "70% del objetivo diario completado",
                                                    style={
                                                        'color': HIGHLIGHT_COLOR,
                                                        'fontSize': '1.1rem',
                                                        'fontWeight': '500',
                                                        'marginBottom': '15px'
                                                    }
                                                )
                                            ]
                                        ),
                                        
                                        # Recomendaciones de hidrataciÃ³n
                                        html.Div(
                                            style={
                                                'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                                'borderRadius': '12px',
                                                'padding': '20px',
                                                'marginBottom': '30px'
                                            },
                                            children=[
                                                html.H4(
                                                    "ðŸ’¡ Recomendaciones",
                                                    style={
                                                        'color': HIGHLIGHT_COLOR,
                                                        'fontSize': '1.3rem',
                                                        'marginBottom': '15px'
                                                    }
                                                ),
                                                html.Ul(
                                                    style={'paddingLeft': '20px', 'margin': '0'},
                                                    children=[
                                                        html.Li(
                                                            "Bebe 500ml adicionales por cada hora de ejercicio",
                                                            style={'color': '#ccc', 'marginBottom': '8px'}
                                                        ),
                                                        html.Li(
                                                            "Toma agua al despertar para activar el metabolismo",
                                                            style={'color': '#ccc', 'marginBottom': '8px'}
                                                        ),
                                                        html.Li(
                                                            "Controla el color de tu orina como indicador de hidrataciÃ³n",
                                                            style={'color': '#ccc'}
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # BotÃ³n para registrar agua
                                        html.Div(
                                            style={
                                                'textAlign': 'center'
                                            },
                                            children=dbc.Button(
                                                [
                                                    html.I(className="bi bi-droplet me-2"),
                                                    "Registrar Agua (+250ml)"
                                                ],
                                                id="btn-registrar-agua",
                                                className="auth-btn",
                                                style={
                                                    'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                    'border': f'2px solid {HIGHLIGHT_COLOR}',
                                                    'fontWeight': '600',
                                                    'padding': '15px 30px',
                                                    'borderRadius': '12px',
                                                    'fontSize': '1.1rem',
                                                    'color': HIGHLIGHT_COLOR,
                                                    'transition': 'all 0.3s ease',
                                                    'width': '100%'
                                                }
                                            )
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # GrÃ¡fico de distribuciÃ³n de macronutrientes
                        html.Div(
                            style={
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'padding': '30px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                            },
                            children=[
                                html.H3(
                                    "ðŸ“Š DistribuciÃ³n de Macronutrientes",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'fontSize': '1.8rem',
                                        'marginBottom': '30px'
                                    }
                                ),
                                
                                # GrÃ¡fico de pastel
                                dcc.Graph(
                                    id='macronutrientes-chart',
                                    config={'displayModeBar': False},
                                    style={'height': '300px'}
                                ),
                                
                                # Leyenda de macronutrientes
                                html.Div(
                                    style={
                                        'display': 'flex',
                                        'justifyContent': 'center',
                                        'gap': '30px',
                                        'marginTop': '20px',
                                        'flexWrap': 'wrap'
                                    },
                                    children=[
                                        html.Div(
                                            style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'},
                                            children=[
                                                html.Div(
                                                    style={
                                                        'width': '20px',
                                                        'height': '20px',
                                                        'backgroundColor': '#4ecdc4',
                                                        'borderRadius': '4px'
                                                    }
                                                ),
                                                html.Span(
                                                    "Carbohidratos: 180g (53%)",
                                                    style={'color': '#ccc', 'fontWeight': '500'}
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'},
                                            children=[
                                                html.Div(
                                                    style={
                                                        'width': '20px',
                                                        'height': '20px',
                                                        'backgroundColor': '#ffd166',
                                                        'borderRadius': '4px'
                                                    }
                                                ),
                                                html.Span(
                                                    "ProteÃ­nas: 95g (28%)",
                                                    style={'color': '#ccc', 'fontWeight': '500'}
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'},
                                            children=[
                                                html.Div(
                                                    style={
                                                        'width': '20px',
                                                        'height': '20px',
                                                        'backgroundColor': '#ff6b6b',
                                                        'borderRadius': '4px'
                                                    }
                                                ),
                                                html.Span(
                                                    "Grasas: 65g (19%)",
                                                    style={'color': '#ccc', 'fontWeight': '500'}
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # MODAL PARA AGREGAR COMIDA (AGREGAR ESTO) - PUNTO 1
                        dbc.Modal(
                            [
                                dbc.ModalHeader(
                                    html.H4("ðŸ½ï¸ Agregar Nueva Comida", style={'color': HIGHLIGHT_COLOR}),
                                    close_button=True,
                                    style={'backgroundColor': '#1a1a1a', 'borderBottom': '1px solid #2b2b2b'}
                                ),
                                dbc.ModalBody(
                                    style={'backgroundColor': '#1a1a1a', 'color': 'white'},
                                    children=[
                                        # Tipo de comida
                                        html.Div(
                                            style={'marginBottom': '20px'},
                                            children=[
                                                html.Label("Tipo de comida", 
                                                          style={'color': '#ccc', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                                dcc.Dropdown(
                                                    id="meal-type-dropdown",
                                                    options=[
                                                        {'label': 'ðŸ³ Desayuno', 'value': 'desayuno'},
                                                        {'label': 'ðŸ¥— Almuerzo', 'value': 'almuerzo'},
                                                        {'label': 'ðŸ² Cena', 'value': 'cena'},
                                                        {'label': 'ðŸŽ Snacks', 'value': 'snacks'}
                                                    ],
                                                    placeholder="Selecciona el tipo de comida",
                                                    style={
                                                        'backgroundColor': '#2b2b2b',
                                                        'color': 'white',
                                                        'border': '1px solid #444'
                                                    },
                                                    className="dbc dbc-row-selectable"
                                                )
                                            ]
                                        ),
                                        
                                        # Hora de la comida
                                        html.Div(
                                            style={'marginBottom': '20px'},
                                            children=[
                                                html.Label("Hora de la comida", 
                                                          style={'color': '#ccc', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                                dcc.Input(
                                                    id="meal-time-input",
                                                    type="text",
                                                    placeholder="Ej: 08:00, 12:30, 18:00",
                                                    style={
                                                        'width': '100%',
                                                        'padding': '12px 15px',
                                                        'backgroundColor': '#2b2b2b',
                                                        'border': '1px solid #444',
                                                        'borderRadius': '8px',
                                                        'color': 'white',
                                                        'fontSize': '1rem'
                                                    }
                                                )
                                            ]
                                        ),
                                        
                                        # DescripciÃ³n de la comida
                                        html.Div(
                                            style={'marginBottom': '20px'},
                                            children=[
                                                html.Label("Â¿QuÃ© has comido?", 
                                                          style={'color': '#ccc', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                                dcc.Textarea(
                                                    id="meal-description-input",
                                                    placeholder="Ej: Avena con frutas y nueces, CafÃ© negro sin azÃºcar...",
                                                    style={
                                                        'width': '100%',
                                                        'height': '100px',
                                                        'padding': '12px 15px',
                                                        'backgroundColor': '#2b2b2b',
                                                        'border': '1px solid #444',
                                                        'borderRadius': '8px',
                                                        'color': 'white',
                                                        'fontSize': '1rem',
                                                        'resize': 'vertical'
                                                    }
                                                )
                                            ]
                                        ),
                                        
                                        # Macronutrientes (estimados - opcional)
                                        html.Div(
                                            style={
                                                'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                                'padding': '15px',
                                                'borderRadius': '10px',
                                                'marginBottom': '20px'
                                            },
                                            children=[
                                                html.H5("ðŸ“Š Macronutrientes Estimados (Opcional)", 
                                                       style={'color': HIGHLIGHT_COLOR, 'marginBottom': '10px'}),
                                                html.P("Si conoces los valores, puedes ingresarlos manualmente. Si no, el sistema estimarÃ¡ automÃ¡ticamente.", 
                                                       style={'color': '#ccc', 'fontSize': '0.9rem', 'marginBottom': '15px'}),
                                                
                                                html.Div(
                                                    style={
                                                        'display': 'grid',
                                                        'gridTemplateColumns': 'repeat(3, 1fr)',
                                                        'gap': '10px'
                                                    },
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.Label("Carbohidratos (g)", 
                                                                          style={'color': '#ccc', 'fontSize': '0.9rem', 'marginBottom': '5px', 'display': 'block'}),
                                                                dcc.Input(
                                                                    id="carbs-input",
                                                                    type="number",
                                                                    placeholder="Ej: 45",
                                                                    min=0,
                                                                    step=1,
                                                                    style={
                                                                        'width': '100%',
                                                                        'padding': '8px 10px',
                                                                        'backgroundColor': '#2b2b2b',
                                                                        'border': '1px solid #444',
                                                                        'borderRadius': '6px',
                                                                        'color': 'white',
                                                                        'fontSize': '0.9rem'
                                                                    }
                                                                )
                                                            ]
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Label("ProteÃ­nas (g)", 
                                                                          style={'color': '#ccc', 'fontSize': '0.9rem', 'marginBottom': '5px', 'display': 'block'}),
                                                                dcc.Input(
                                                                    id="protein-input",
                                                                    type="number",
                                                                    placeholder="Ej: 25",
                                                                    min=0,
                                                                    step=1,
                                                                    style={
                                                                        'width': '100%',
                                                                        'padding': '8px 10px',
                                                                        'backgroundColor': '#2b2b2b',
                                                                        'border': '1px solid #444',
                                                                        'borderRadius': '6px',
                                                                        'color': 'white',
                                                                        'fontSize': '0.9rem'
                                                                    }
                                                                )
                                                            ]
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Label("Grasas (g)", 
                                                                          style={'color': '#ccc', 'fontSize': '0.9rem', 'marginBottom': '5px', 'display': 'block'}),
                                                                dcc.Input(
                                                                    id="fat-input",
                                                                    type="number",
                                                                    placeholder="Ej: 15",
                                                                    min=0,
                                                                    step=1,
                                                                    style={
                                                                        'width': '100%',
                                                                        'padding': '8px 10px',
                                                                        'backgroundColor': '#2b2b2b',
                                                                        'border': '1px solid #444',
                                                                        'borderRadius': '6px',
                                                                        'color': 'white',
                                                                        'fontSize': '0.9rem'
                                                                    }
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # CalorÃ­as estimadas
                                        html.Div(
                                            style={'marginBottom': '20px'},
                                            children=[
                                                html.Label("CalorÃ­as estimadas", 
                                                          style={'color': '#ccc', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                                                dcc.Input(
                                                    id="calories-input",
                                                    type="number",
                                                    placeholder="Ej: 350",
                                                    min=0,
                                                    step=1,
                                                    style={
                                                        'width': '100%',
                                                        'padding': '12px 15px',
                                                        'backgroundColor': '#2b2b2b',
                                                        'border': '1px solid #444',
                                                        'borderRadius': '8px',
                                                        'color': 'white',
                                                        'fontSize': '1rem'
                                                    }
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                dbc.ModalFooter(
                                    style={'backgroundColor': '#1a1a1a', 'borderTop': '1px solid #2b2b2b'},
                                    children=[
                                        dbc.Button(
                                            "Cancelar",
                                            id="btn-cancel-meal",
                                            color="secondary",
                                            className="me-2",
                                            style={'borderRadius': '8px'}
                                        ),
                                        dbc.Button(
                                            "Agregar Comida",
                                            id="btn-submit-meal",
                                            color="primary",
                                            style={'backgroundColor': HIGHLIGHT_COLOR, 'borderColor': HIGHLIGHT_COLOR, 'borderRadius': '8px'}
                                        )
                                    ]
                                )
                            ],
                            id="modal-add-meal",
                            size="lg",
                            is_open=False,
                            centered=True,
                            backdrop=True,
                            style={'backgroundColor': 'rgba(0,0,0,0.7)'}
                        )
                    ]
                )
            ]
        )
    ]
)

# ===============================
# ENTRENAMIENTOS LAYOUT
# ===============================

# ===============================
# ENTRENAMIENTOS LAYOUT (MODIFICADO)
# ===============================

entrenamientos_layout = html.Div(
    id="entrenamientos-container",
    className="entrenamientos-container",
    style={
        'backgroundColor': DARK_BACKGROUND,
        'minHeight': '100vh',
        'color': 'white',
        'fontFamily': 'Inter, sans-serif'
    },
    children=[
        # Header (igual que en otras pÃ¡ginas)
        html.Div(
            id="entrenamientos-header",
            className="entrenamientos-header",
            style={
                'backgroundColor': '#1a1a1a',
                'padding': '15px 40px',
                'borderBottom': '1px solid rgba(0, 212, 255, 0.1)',
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center'
            },
            children=[
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center'},
                    children=[
                        html.Div(
                            style={
                                'width': '40px',
                                'height': '40px',
                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                'borderRadius': '10px',
                                'border': f'2px solid {HIGHLIGHT_COLOR}',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginRight': '15px'
                            },
                            children=html.Span("A", style={'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.2rem'})
                        ),
                        html.H1(
                            "ATHLETICA",
                            style={
                                'color': HIGHLIGHT_COLOR,
                                'fontSize': '1.8rem',
                                'fontWeight': '900',
                                'letterSpacing': '2px',
                                'textShadow': f'0 0 15px rgba(0, 224, 255, 0.5)',
                                'margin': '0'
                            }
                        )
                    ]
                ),
                
                html.Div(
                    style={
                        'flex': '1',
                        'height': '1px',
                        'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                        'margin': '0 30px'
                    }
                ),
                
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'gap': '20px'},
                    children=[
                        html.Div(
                            style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'gap': '10px',
                                'cursor': 'pointer'
                            },
                            children=[
                                html.Div(
                                    id="entrenamientos-user-profile-avatar",
                                    style={
                                        'width': '45px',
                                        'height': '45px',
                                        'backgroundColor': HIGHLIGHT_COLOR,
                                        'borderRadius': '50%',
                                        'border': f'2px solid {HIGHLIGHT_COLOR}',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.2rem'
                                    }
                                ),
                                html.Div(
                                    style={'textAlign': 'right'},
                                    children=[
                                        html.Div(
                                            id="entrenamientos-user-profile-name",
                                            style={
                                                'fontWeight': '600',
                                                'fontSize': '1rem',
                                                'color': '#fff'
                                            }
                                        ),
                                        html.Div(
                                            "Atleta",
                                            style={
                                                'fontSize': '0.8rem',
                                                'color': HIGHLIGHT_COLOR,
                                                'fontWeight': '500'
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),
                    ]
                )
            ]
        ),

        # Cuerpo principal con sidebar y contenido
        html.Div(
            style={
                'display': 'flex',
                'minHeight': 'calc(100vh - 100px)'
            },
            children=[
                # Sidebar (igual que en otras pÃ¡ginas)
                html.Div(
                    id="entrenamientos-sidebar",
                    className="entrenamientos-sidebar",
                    style={
                        'width': '280px',
                        'backgroundColor': '#141414',
                        'padding': '25px 20px',
                        'borderRight': '1px solid rgba(0, 212, 255, 0.1)',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '30px'
                    },
                    children=[
                        html.Div(
                            style={
                                'padding': '20px',
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'textAlign': 'center'
                            },
                            children=[
                                html.Div(
                                    id="entrenamientos-sidebar-user-avatar",
                                    style={
                                        'width': '70px',
                                        'height': '70px',
                                        'backgroundColor': HIGHLIGHT_COLOR,
                                        'borderRadius': '50%',
                                        'border': f'3px solid {HIGHLIGHT_COLOR}',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#0a0a0a',
                                        'fontWeight': 'bold',
                                        'fontSize': '1.8rem',
                                        'margin': '0 auto 15px'
                                    }
                                ),
                                
                                html.Div(
                                    id="entrenamientos-sidebar-user-fullname",
                                    style={
                                        'fontSize': '1.3rem',
                                        'fontWeight': '700',
                                        'color': '#ffffff',
                                        'marginBottom': '5px'
                                    }
                                ),
                                
                                html.Div(
                                    id="entrenamientos-sidebar-user-level",
                                    style={
                                        'fontSize': '0.9rem',
                                        'color': HIGHLIGHT_COLOR,
                                        'fontWeight': '500',
                                        'marginBottom': '20px'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'height': '1px',
                                        'backgroundColor': 'rgba(255, 255, 255, 0.1)',
                                        'margin': '15px 0'
                                    }
                                ),
                                
                                html.Div(
                                    "Estado de Salud",
                                    style={
                                        'fontSize': '1rem',
                                        'fontWeight': '600',
                                        'color': '#ffffff',
                                        'marginBottom': '15px',
                                        'textAlign': 'center'
                                    }
                                ),
                                
                                html.Div(
                                    id="entrenamientos-health-status-dots",
                                    style={
                                        'display': 'flex',
                                        'justifyContent': 'center',
                                        'gap': '8px',
                                        'marginBottom': '12px'
                                    }
                                ),
                                
                                html.Div(
                                    id="entrenamientos-health-status-description",
                                    style={
                                        'fontSize': '0.8rem',
                                        'color': '#cccccc',
                                        'textAlign': 'center',
                                        'lineHeight': '1.4'
                                    }
                                )
                            ]
                        ),
                        
                        # NavegaciÃ³n
                        html.Div(
                            children=[
                                html.H4(
                                    "NavegaciÃ³n",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'marginBottom': '20px',
                                        'marginTop': '25px',
                                        'fontSize': '1.1rem',
                                        'fontWeight': '600',
                                        'paddingLeft': '10px'
                                    }
                                ),
                                html.Div(
                                    style={'display': 'flex', 'flexDirection': 'column', 'gap': '8px'},
                                    children=[
                                        html.Button(
                                            [
                                                html.I(className="bi bi-house-door", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Inicio", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-inicio-entrenamientos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-graph-up", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("MÃ©tricas", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-metricas-entrenamientos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-bullseye", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Objetivos", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-objetivos-entrenamientos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-egg-fried", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("NutriciÃ³n", style={'fontSize': '0.95rem', 'fontWeight': '400'})
                                            ],
                                            id="nav-nutricion-entrenamientos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'transparent',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': '1px solid transparent',
                                                'color': '#ccc',
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                        
                                        html.Button(
                                            [
                                                html.I(className="bi bi-activity", style={'marginRight': '12px', 'fontSize': '1.1rem'}),
                                                html.Span("Entrenamientos", style={'fontSize': '0.95rem', 'fontWeight': '500'})
                                            ],
                                            id="nav-entrenamientos-entrenamientos",
                                            n_clicks=0,
                                            style={
                                                'display': 'flex',
                                                'alignItems': 'center',
                                                'padding': '12px 15px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                'borderRadius': '10px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.3s ease',
                                                'border': f'1px solid {HIGHLIGHT_COLOR}',
                                                'color': HIGHLIGHT_COLOR,
                                                'textAlign': 'left',
                                                'fontFamily': "'Inter', sans-serif",
                                                'border': 'none'
                                            }
                                        ),
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                
                # CONTENIDO PRINCIPAL DE ENTRENAMIENTOS (NUEVO)
                html.Div(
                    className="entrenamientos-main",
                    style={
                        'flex': '1',
                        'padding': '40px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '30px',
                        'overflowY': 'auto'
                    },
                    children=[
                        # TÃ­tulo principal
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'marginBottom': '10px'
                            },
                            children=[
                                html.H2(
                                    "ðŸ’ª Entrenamientos",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'fontSize': '2.5rem',
                                        'fontWeight': '700',
                                        'margin': '0'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'color': '#ccc',
                                        'fontSize': '1rem'
                                    },
                                    children=f"Hoy, {datetime.now().strftime('%d/%m/%Y')}"
                                )
                            ]
                        ),
                        
                        # Mensaje informativo
                        html.Div(
                            style={
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'padding': '30px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)',
                                'marginBottom': '30px'
                            },
                            children=[
                                html.H3(
                                    "ðŸ“¡ Registro de Entrenamientos",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'fontSize': '1.8rem',
                                        'marginBottom': '20px'
                                    }
                                ),
                                
                                html.P(
                                    "Los entrenamientos que realices se registrarÃ¡n automÃ¡ticamente utilizando un dispositivo externo propio del usuario (reloj inteligente, banda de actividad, etc.).",
                                    style={
                                        'color': '#ccc',
                                        'fontSize': '1.1rem',
                                        'lineHeight': '1.6',
                                        'marginBottom': '25px'
                                    }
                                ),
                                
                                html.P(
                                    "Para comenzar a registrar tus entrenamientos, conecta tu dispositivo compatible vÃ­a Bluetooth:",
                                    style={
                                        'color': '#ccc',
                                        'fontSize': '1.1rem',
                                        'lineHeight': '1.6',
                                        'marginBottom': '30px'
                                    }
                                ),
                                
                                # BotÃ³n de conexiÃ³n Bluetooth
                                html.Div(
                                    style={
                                        'textAlign': 'center',
                                        'marginTop': '20px'
                                    },
                                    children=[
                                        html.Button(
                                            [
                                                html.I(className="bi bi-bluetooth me-2", style={'fontSize': '1.2rem'}),
                                                html.Span("Conectar Dispositivo", id="btn-conectar-text", style={'fontSize': '1.1rem'})
                                            ],
                                            id="btn-conectar-bluetooth",
                                            n_clicks=0,
                                            style={
                                                'backgroundColor': HIGHLIGHT_COLOR,
                                                'border': 'none',
                                                'fontWeight': '600',
                                                'padding': '15px 40px',
                                                'borderRadius': '12px',
                                                'fontSize': '1.1rem',
                                                'color': '#0a0a0a',
                                                'transition': 'all 0.3s ease',
                                                'cursor': 'pointer',
                                                'boxShadow': f'0 4px 15px rgba(0, 212, 255, 0.4)'
                                            }
                                        ),
                                        
                                        # Estado de conexiÃ³n
                                        html.Div(
                                            id="estado-conexion",
                                            style={
                                                'marginTop': '20px',
                                                'padding': '10px 20px',
                                                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                                'borderRadius': '8px',
                                                'border': f'1px solid {HIGHLIGHT_COLOR}',
                                                'display': 'inline-block'
                                            },
                                            children=[
                                                html.I(className="bi bi-circle-fill me-2", id="icono-estado", style={'color': '#ff6b6b', 'fontSize': '0.8rem'}),
                                                html.Span("Dispositivo desconectado", id="texto-estado", style={'color': '#ccc', 'fontWeight': '500'})
                                            ]
                                        )
                                    ]
                                ),
                                
                                # Dispositivos compatibles
                                html.Div(
                                    style={
                                        'marginTop': '40px',
                                        'paddingTop': '30px',
                                        'borderTop': '1px solid #2b2b2b'
                                    },
                                    children=[
                                        html.H4(
                                            "ðŸ“± Dispositivos Compatibles",
                                            style={
                                                'color': HIGHLIGHT_COLOR,
                                                'fontSize': '1.4rem',
                                                'marginBottom': '20px'
                                            }
                                        ),
                                        
                                        html.Div(
                                            style={
                                                'display': 'grid',
                                                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                                                'gap': '20px'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                                        'padding': '20px',
                                                        'borderRadius': '10px',
                                                        'textAlign': 'center',
                                                        'border': '1px solid rgba(0, 212, 255, 0.1)'
                                                    },
                                                    children=[
                                                        html.I(className="bi bi-apple", style={'color': HIGHLIGHT_COLOR, 'fontSize': '2rem', 'marginBottom': '10px'}),
                                                        html.Div("Apple Watch", style={'color': '#fff', 'fontWeight': '600', 'marginBottom': '5px'}),
                                                        html.Div("Series 4 o superior", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                                    ]
                                                ),
                                                
                                                html.Div(
                                                    style={
                                                        'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                                        'padding': '20px',
                                                        'borderRadius': '10px',
                                                        'textAlign': 'center',
                                                        'border': '1px solid rgba(0, 212, 255, 0.1)'
                                                    },
                                                    children=[
                                                        html.I(className="bi bi-watch", style={'color': HIGHLIGHT_COLOR, 'fontSize': '2rem', 'marginBottom': '10px'}),
                                                        html.Div("Garmin", style={'color': '#fff', 'fontWeight': '600', 'marginBottom': '5px'}),
                                                        html.Div("Forerunner, Fenix", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                                    ]
                                                ),
                                                
                                                html.Div(
                                                    style={
                                                        'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                                        'padding': '20px',
                                                        'borderRadius': '10px',
                                                        'textAlign': 'center',
                                                        'border': '1px solid rgba(0, 212, 255, 0.1)'
                                                    },
                                                    children=[
                                                        html.I(className="bi bi-phone", style={'color': HIGHLIGHT_COLOR, 'fontSize': '2rem', 'marginBottom': '10px'}),
                                                        html.Div("Fitbit", style={'color': '#fff', 'fontWeight': '600', 'marginBottom': '5px'}),
                                                        html.Div("Versa, Charge", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                                    ]
                                                ),
                                                
                                                html.Div(
                                                    style={
                                                        'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                                        'padding': '20px',
                                                        'borderRadius': '10px',
                                                        'textAlign': 'center',
                                                        'border': '1px solid rgba(0, 212, 255, 0.1)'
                                                    },
                                                    children=[
                                                        html.I(className="bi bi-watch", style={'color': HIGHLIGHT_COLOR, 'fontSize': '2rem', 'marginBottom': '10px'}),
                                                        html.Div("Samsung Galaxy", style={'color': '#fff', 'fontWeight': '600', 'marginBottom': '5px'}),
                                                        html.Div("Watch Series", style={'color': '#ccc', 'fontSize': '0.9rem'})
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # PrÃ³ximos entrenamientos (ejemplo)
                        html.Div(
                            style={
                                'backgroundColor': '#1a1a1a',
                                'borderRadius': '15px',
                                'padding': '30px',
                                'border': '1px solid rgba(0, 212, 255, 0.1)',
                                'boxShadow': '0 5px 20px rgba(0, 0, 0, 0.3)'
                            },
                            children=[
                                html.H3(
                                    "ðŸ“… PrÃ³ximos Entrenamientos",
                                    style={
                                        'color': HIGHLIGHT_COLOR,
                                        'fontSize': '1.8rem',
                                        'marginBottom': '25px'
                                    }
                                ),
                                
                                html.Div(
                                    style={
                                        'display': 'grid',
                                        'gridTemplateColumns': 'repeat(auto-fit, minmax(300px, 1fr))',
                                        'gap': '20px'
                                    },
                                    children=[
                                        html.Div(
                                            style={
                                                'backgroundColor': 'rgba(0, 212, 255, 0.08)',
                                                'padding': '20px',
                                                'borderRadius': '10px',
                                                'borderLeft': f'4px solid {HIGHLIGHT_COLOR}'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.H4(
                                                            "ðŸƒ Carrera Continua",
                                                            style={'color': '#fff', 'margin': '0', 'fontSize': '1.2rem'}
                                                        ),
                                                        html.Div(
                                                            "MaÃ±ana 8:00",
                                                            style={'color': HIGHLIGHT_COLOR, 'fontWeight': '500'}
                                                        )
                                                    ]
                                                ),
                                                html.P(
                                                    "30 minutos a ritmo moderado. Zona cardÃ­aca 2-3.",
                                                    style={'color': '#ccc', 'marginBottom': '10px', 'fontSize': '0.95rem'}
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span("Distancia: ", style={'color': '#ccc'}),
                                                        html.Span("5 km", style={'color': HIGHLIGHT_COLOR, 'fontWeight': '500'})
                                                    ],
                                                    style={'fontSize': '0.9rem'}
                                                )
                                            ]
                                        ),
                                        
                                        html.Div(
                                            style={
                                                'backgroundColor': 'rgba(78, 205, 196, 0.08)',
                                                'padding': '20px',
                                                'borderRadius': '10px',
                                                'borderLeft': '4px solid #4ecdc4'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.H4(
                                                            "ðŸ’ª Entrenamiento de Fuerza",
                                                            style={'color': '#fff', 'margin': '0', 'fontSize': '1.2rem'}
                                                        ),
                                                        html.Div(
                                                            "Jueves 19:00",
                                                            style={'color': '#4ecdc4', 'fontWeight': '500'}
                                                        )
                                                    ]
                                                ),
                                                html.P(
                                                    "Circuito de fuerza: piernas, pecho y espalda.",
                                                    style={'color': '#ccc', 'marginBottom': '10px', 'fontSize': '0.95rem'}
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span("DuraciÃ³n: ", style={'color': '#ccc'}),
                                                        html.Span("45 min", style={'color': '#4ecdc4', 'fontWeight': '500'})
                                                    ],
                                                    style={'fontSize': '0.9rem'}
                                                )
                                            ]
                                        ),
                                        
                                        html.Div(
                                            style={
                                                'backgroundColor': 'rgba(255, 209, 102, 0.08)',
                                                'padding': '20px',
                                                'borderRadius': '10px',
                                                'borderLeft': '4px solid #ffd166'
                                            },
                                            children=[
                                                html.Div(
                                                    style={
                                                        'display': 'flex',
                                                        'justifyContent': 'space-between',
                                                        'alignItems': 'center',
                                                        'marginBottom': '15px'
                                                    },
                                                    children=[
                                                        html.H4(
                                                            "ðŸ§˜ RecuperaciÃ³n Activa",
                                                            style={'color': '#fff', 'margin': '0', 'fontSize': '1.2rem'}
                                                        ),
                                                        html.Div(
                                                            "Viernes 9:00",
                                                            style={'color': '#ffd166', 'fontWeight': '500'}
                                                        )
                                                    ]
                                                ),
                                                html.P(
                                                    "Yoga y estiramientos para mejorar flexibilidad.",
                                                    style={'color': '#ccc', 'marginBottom': '10px', 'fontSize': '0.95rem'}
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span("Intensidad: ", style={'color': '#ccc'}),
                                                        html.Span("Baja", style={'color': '#ffd166', 'fontWeight': '500'})
                                                    ],
                                                    style={'fontSize': '0.9rem'}
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# ===============================
# LAYOUT PRINCIPAL
# ===============================
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
        
        # STORES
        dcc.Store(id='onboarding-step', data=1), 
        dcc.Store(id='onboarding-user-name', data="Usuario/a"), 
        dcc.Store(id='selected-sports-store', data=[]),
        dcc.Store(id='onboarding-completed', data=False),
        dcc.Store(id='current-user', data=None),
        dcc.Store(id='user-activity-level', data=5),
        dcc.Store(id='user-goals-store', data={"fitness": [], "health": []}),  # Inicializado correctamente
        
        # NUEVOS STORES PARA NUTRICIÃ“N (MODIFICADOS)
        dcc.Store(id='user-meals-store', data=[]),  # Inicializado
        dcc.Store(id='nutrition-totals-store', data={  # Inicializado
            'calories': 0,
            'carbs': 0,
            'protein': 0,
            'fat': 0
        }),
        dcc.Store(id='water-tracker-store', data={'current': 2.1, 'target': 3.0}),  # NUEVO: Store para agua
        dcc.Store(id='bluetooth-status-store', data={'connected': False}),
        
        # DIV DE DIAGNÃ“STICO
        html.Div(id="stores-debug", style={"display": "none"}),

        dcc.Store(id='user-type-store', data=None),  # 'doctor' o 'athlete'
        
        
        # Trigger para refrescar dashboard mÃ©dico
        dcc.Store(id='doctor-dashboard-refresh-trigger', data=None),  
    ]
)
# ==========================================================
# ÃšNICO CALLBACK PARA INICIALIZAR NIVEL DE ACTIVIDAD
# ==========================================================

@app.callback(
    Output("user-activity-level", "data"),
    [Input("current-user", "data")],
    prevent_initial_call=False
)
def initialize_user_activity_level(current_user):
    """Inicializa el nivel de actividad cuando cambia el usuario"""
    print(f"ðŸ” INIT USER ACTIVITY LEVEL - user: {current_user}")
    
    if current_user:
        activity_level = get_user_activity_level(current_user)
        print(f"âœ… Nivel de actividad inicializado: {activity_level}")
        return activity_level
    
    return 5  # Valor por defecto

# ==========================================================
# CALLBACK PARA NAVEGACIÃ“N INICIAL (ACTUALIZADO)
# ==========================================================

@app.callback(
    Output("url", "pathname"),
    [Input("current-user", "data"),
     Input("onboarding-completed", "data"),
     Input("user-type-store", "data")],  # NUEVO INPUT
    [State("url", "pathname")],
    prevent_initial_call=False
)
def handle_initial_navigation(current_user, onboarding_completed, user_type, current_path):
    """Maneja la navegaciÃ³n basada en estado del usuario y tipo"""
    print(f"ðŸ” NAVIGATION - user: {current_user}, type: {user_type}, onboarding: {onboarding_completed}, path: {current_path}")
    
    # Si no hay usuario, ir a login
    if not current_user:
        return '/login'
    
    # Si es mÃ©dico, ir directamente al dashboard mÃ©dico
    if user_type == "doctor":
        print(f"ðŸ‘¨â€âš•ï¸ MÃ©dico {current_user} detectado, redirigiendo a dashboard mÃ©dico")
        return '/doctor-dashboard'
    
    # Si es atleta pero no completÃ³ onboarding
    if user_type == "athlete" and not onboarding_completed:
        print(f"ðŸŽ¯ Atleta {current_user} necesita onboarding")
        return '/onboarding'
    
    # Si es atleta y completÃ³ onboarding
    if user_type == "athlete" and onboarding_completed:
        print(f"âœ… Atleta {current_user} redirigiendo a inicio")
        return '/inicio'
    
    return dash.no_update

# ==========================================================
# CALLBACK PRINCIPAL DE PÃGINA (ULTRA SIMPLIFICADO)
# ==========================================================

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    [State('current-user', 'data'),
     State('user-type-store', 'data')],
    prevent_initial_call=False
)
def display_page_corrected(pathname, current_user, user_type):
    """Callback principal de navegaciÃ³n - VERSIÃ“N CORREGIDA"""
    print(f"ðŸ”„ display_page: {pathname}, user: {current_user}, type: {user_type}")
    
    # Extraer parÃ¡metros si los hay
    base_path = pathname.split('?')[0]
    
    # Si es mÃ©dico y quiere ver dashboard mÃ©dico
    if base_path == '/doctor-dashboard':
        if user_type == "doctor":
            return doctor_dashboard_layout
        else:
            # Si no es mÃ©dico, redirigir a inicio
            return html.Div("Acceso no autorizado", style={'textAlign': 'center', 'padding': '50px'})
    
    # Si hay parÃ¡metro de paciente
    if base_path == '/inicio' and '?patient=' in pathname:
        patient_username = pathname.split('?patient=')[1]
        print(f"ðŸ‘¨â€âš•ï¸ Mostrando datos del paciente: {patient_username}")
        
        # Verificar permisos si es mÃ©dico
        if user_type == "doctor" and current_user in DOCTORS_DB:
            patients = DOCTORS_DB[current_user].get("patients", [])
            if patient_username in patients:
                # Crear layout especial para vista de paciente
                return create_patient_view_layout(patient_username)
        
        # Si no tiene permisos, mostrar inicio normal
        return inicio_layout
    
    # Mapeo simple de rutas a layouts
    route_map = {
        '/': welcome_layout,
        '/login': login_layout,
        '/register': register_layout,
        '/onboarding': onboarding_layout,
        '/inicio': inicio_layout,
        '/metricas': metricas_layout,
        '/objetivos': objetivos_layout,
        '/nutricion': nutricion_layout,
        '/entrenamientos': entrenamientos_layout,
    }
    
    return route_map.get(base_path, welcome_layout)

# ==========================================================
# CALLBACKS PARA EL DASHBOARD MÃ‰DICO
# ==========================================================

@app.callback(
    [Output("doctor-profile-avatar", "children"),
     Output("doctor-profile-name", "children"),
     Output("doctor-patients-grid", "children"),
     Output("doctor-debug-info", "children")],  # Solo estos 4 Outputs existen
    [Input("current-user", "data"),
     Input("user-type-store", "data"),
     Input("url", "pathname"),
     Input("doctor-dashboard-refresh-trigger", "data")],  
    prevent_initial_call=False
)
def update_doctor_dashboard_corrected(current_user, user_type, pathname, refresh_trigger):
    """Actualiza el dashboard mÃ©dico con datos del doctor y sus pacientes - VERSIÃ“N CORREGIDA"""
    
    # Solo ejecutar si estamos en el dashboard mÃ©dico
    if pathname != '/doctor-dashboard':
        raise dash.exceptions.PreventUpdate
    
    # Verificar que el usuario sea mÃ©dico
    if user_type != "doctor" or current_user not in DOCTORS_DB:
        # Devolver valores por defecto
        debug_info = "No es mÃ©dico o usuario no encontrado"
        return ["M", "Sin datos", html.Div("No hay datos disponibles"), debug_info]
    
    # Obtener datos del mÃ©dico
    doctor_data = DOCTORS_DB[current_user]
    doctor_name = doctor_data.get("full_name", current_user)
    
    # Obtener inicial del avatar
    avatar_initial = doctor_name[0].upper() if doctor_name else current_user[0].upper()
    
    # Obtener lista de pacientes
    patient_usernames = doctor_data.get("patients", [])
    patient_count = len(patient_usernames)
    
    print(f"ðŸ‘¨â€âš•ï¸ MÃ©dico {current_user} tiene {patient_count} pacientes: {patient_usernames}")
    
    # Crear tarjetas de pacientes
    patient_cards = []
    total_activity = 0
    total_bpm = 0
    risk_patients = 0
    
    for patient_username in patient_usernames:
        if patient_username in USERS_DB:
            patient_data = USERS_DB[patient_username]
            patient_name = patient_data.get("full_name", patient_username)
            activity_level = patient_data.get("activity_level", 5)
            health_score = get_health_score_from_activity_level(activity_level)
            
            # Calcular BPM simulado basado en actividad
            base_bpm = 60 + (activity_level * 2)
            
            # Acumular para promedios
            total_activity += activity_level
            total_bpm += base_bpm
            
            # Contar pacientes en riesgo (baja actividad)
            if activity_level <= 3:
                risk_patients += 1
            
            # Determinar color basado en estado de salud
            if health_score >= 4:
                card_color = HIGHLIGHT_COLOR
            elif health_score >= 3:
                card_color = '#ffd166'
            else:
                card_color = '#ff6b6b'
            
            patient_card = html.Div(
                style={
                    'backgroundColor': '#141414',
                    'borderRadius': '12px',
                    'padding': '20px',
                    'border': f'2px solid {card_color}',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease',
                    'position': 'relative',
                    'overflow': 'hidden',
                    'marginBottom': '15px'
                },
                id={
                    'type': 'patient-card',
                    'patient-username': patient_username
                },
                children=[
                    html.Div(
                        style={
                            'position': 'absolute',
                            'top': '10px',
                            'right': '10px',
                            'backgroundColor': card_color,
                            'color': '#0a0a0a',
                            'padding': '5px 10px',
                            'borderRadius': '15px',
                            'fontSize': '0.8rem',
                            'fontWeight': '600'
                        },
                        children=f"Nivel {activity_level}/10"
                    ),
                    
                    html.Div(
                        style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'marginBottom': '15px'
                        },
                        children=[
                            html.Div(
                                style={
                                    'width': '50px',
                                    'height': '50px',
                                    'backgroundColor': card_color,
                                    'borderRadius': '50%',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'color': '#0a0a0a',
                                    'fontWeight': 'bold',
                                    'fontSize': '1.2rem',
                                    'marginRight': '15px'
                                },
                                children=patient_name[0].upper()
                            ),
                            html.Div(
                                style={'flex': '1'},
                                children=[
                                    html.Div(
                                        patient_name,
                                        style={
                                            'fontWeight': '600',
                                            'fontSize': '1.1rem',
                                            'color': '#fff',
                                            'marginBottom': '5px'
                                        }
                                    ),
                                    html.Div(
                                        f"@{patient_username}",
                                        style={
                                            'color': '#ccc',
                                            'fontSize': '0.9rem'
                                        }
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Estado de salud
                    html.Div(
                        style={
                            'marginBottom': '15px',
                            'padding': '10px',
                            'backgroundColor': 'rgba(0, 0, 0, 0.2)',
                            'borderRadius': '8px'
                        },
                        children=[
                            html.Div(
                                "Estado de Salud",
                                style={
                                    'color': '#ccc',
                                    'fontSize': '0.9rem',
                                    'marginBottom': '8px'
                                }
                            ),
                            html.Div(
                                style={
                                    'display': 'flex',
                                    'gap': '5px',
                                    'marginBottom': '8px'
                                },
                                children=[
                                    html.Div(
                                        style={
                                            'width': f'{health_score * 20}%',
                                            'height': '8px',
                                            'backgroundColor': card_color,
                                            'borderRadius': '4px'
                                        }
                                    ),
                                    html.Div(
                                        style={
                                            'flex': '1',
                                            'height': '8px',
                                            'backgroundColor': '#2b2b2b',
                                            'borderRadius': '4px'
                                        }
                                    )
                                ]
                            ),
                            html.Div(
                                get_health_description(health_score),
                                style={
                                    'color': card_color,
                                    'fontSize': '0.8rem',
                                    'fontWeight': '500'
                                }
                            )
                        ]
                    ),
                    
                    # MÃ©tricas rÃ¡pidas
                    html.Div(
                        style={
                            'display': 'flex',
                            'justifyContent': 'space-between'
                        },
                        children=[
                            html.Div(
                                style={'textAlign': 'center'},
                                children=[
                                    html.Div(
                                        f"{base_bpm}",
                                        style={
                                            'fontSize': '1.2rem',
                                            'fontWeight': '700',
                                            'color': card_color,
                                            'marginBottom': '5px'
                                        }
                                    ),
                                    html.Div(
                                        "BPM",
                                        style={'color': '#ccc', 'fontSize': '0.8rem'}
                                    )
                                ]
                            ),
                            html.Div(
                                style={'textAlign': 'center'},
                                children=[
                                    html.Div(
                                        f"{health_score}/5",
                                        style={
                                            'fontSize': '1.2rem',
                                            'fontWeight': '700',
                                            'color': card_color,
                                            'marginBottom': '5px'
                                        }
                                    ),
                                    html.Div(
                                        "Salud",
                                        style={'color': '#ccc', 'fontSize': '0.8rem'}
                                    )
                                ]
                            ),
                            html.Div(
                                style={'textAlign': 'center'},
                                children=[
                                    html.Div(
                                        "Ver",
                                        style={
                                            'fontSize': '1.2rem',
                                            'fontWeight': '700',
                                            'color': card_color,
                                            'marginBottom': '5px'
                                        }
                                    ),
                                    html.Div(
                                        "Detalles",
                                        style={'color': '#ccc', 'fontSize': '0.8rem'}
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Indicador de doble clic
                    html.Div(
                        "Doble clic para ver detalles",
                        style={
                            'position': 'absolute',
                            'bottom': '10px',
                            'left': '0',
                            'right': '0',
                            'textAlign': 'center',
                            'color': '#666',
                            'fontSize': '0.7rem',
                            'fontStyle': 'italic'
                        }
                    )
                ]
            )
            patient_cards.append(patient_card)
        else:
            print(f"âš ï¸ Paciente {patient_username} no encontrado en USERS_DB")
    
    # Calcular promedios
    avg_activity = round(total_activity / max(patient_count, 1), 1) if patient_count > 0 else 0.0
    avg_bpm = round(total_bpm / max(patient_count, 1)) if patient_count > 0 else 0
    
    # Crear estadÃ­sticas para debug
    stats_text = f"""
    ðŸ“Š EstadÃ­sticas del MÃ©dico:
    â€¢ Total pacientes: {patient_count}
    â€¢ Actividad promedio: {avg_activity}/10
    â€¢ BPM promedio: {avg_bpm}
    â€¢ Pacientes en riesgo: {risk_patients}
    â€¢ Ãšltima actualizaciÃ³n: {datetime.now().strftime('%H:%M:%S')}
    """
    
    print(f"ðŸ“Š EstadÃ­sticas: {patient_count} pacientes, actividad promedio: {avg_activity}, BPM promedio: {avg_bpm}")
    
    # Si no hay pacientes, mostrar mensaje
    if patient_count == 0:
        patient_cards = html.Div(
            "No hay pacientes aÃºn. Usa la bÃºsqueda para aÃ±adir pacientes.",
            style={
                'textAlign': 'center',
                'padding': '40px',
                'color': '#666',
                'fontStyle': 'italic',
                'backgroundColor': '#1a1a1a',
                'borderRadius': '10px',
                'border': '1px solid #2b2b2b'
            }
        )
    
    return (
        avatar_initial,
        doctor_name,
        patient_cards,
        stats_text
    )

@app.callback(
    Output("doctor-search-results", "children"),
    [Input("doctor-search-btn", "n_clicks"),
     Input("doctor-search-input", "n_submit")],
    [State("doctor-search-input", "value"),
     State("current-user", "data"),
     State("url", "pathname")],
    prevent_initial_call=True
)
def search_patients(n_clicks, n_submit, search_term, current_user, pathname):
    """Busca pacientes y muestra resultados - VERSIÃ“N SIMPLIFICADA"""
    
    if pathname != '/doctor-dashboard':
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    if not search_term or len(search_term.strip()) < 2:
        return html.Div(
            "Ingresa al menos 2 caracteres para buscar",
            style={'color': '#666', 'fontStyle': 'italic', 'padding': '10px', 'textAlign': 'center'}
        )
    
    print(f"ðŸ” BÃºsqueda iniciada: '{search_term}' por mÃ©dico {current_user}")
    
    # Usar la funciÃ³n auxiliar para crear los resultados
    search_results = search_users_by_name(search_term) if search_term else []
    display_results = create_search_results_display(search_results, current_user)
    
    return display_results

    # Obtener pacientes actuales del mÃ©dico
    current_patients = []
    if current_user in DOCTORS_DB:
        current_patients = DOCTORS_DB[current_user].get("patients", [])
    
    # Buscar usuarios
    search_results = search_users_by_name(search_term)
    
    if not search_results:
        return html.Div(
            "No se encontraron pacientes con ese criterio",
            style={'color': '#666', 'fontStyle': 'italic', 'padding': '10px', 'textAlign': 'center'}
        )
    
    # Crear lista de resultados
    result_items = []
    for result in search_results:
        username = result["username"]
        full_name = result["full_name"]
        email = result["email"]
        activity_level = result["activity_level"]
        
        # Verificar si ya es paciente de este mÃ©dico
        is_current_patient = username in current_patients
        
        # Crear ID Ãºnico para el botÃ³n
        button_id = f"add-patient-btn-{username.replace('.', '-').replace('@', '-')}"
        
        # Crear el botÃ³n con ID simple
        result_item = html.Div(
            style={
                'backgroundColor': '#2b2b2b',
                'borderRadius': '8px',
                'padding': '15px',
                'marginBottom': '10px',
                'border': f'1px solid {HIGHLIGHT_COLOR if not is_current_patient else "#4ecdc4"}'
            },
            children=[
                html.Div(
                    style={
                        'display': 'flex',
                        'justifyContent': 'space-between',
                        'alignItems': 'center',
                        'marginBottom': '10px'
                    },
                    children=[
                        html.Div(
                            style={'flex': '1'},
                            children=[
                                html.Div(
                                    full_name,
                                    style={
                                        'fontWeight': '600',
                                        'color': '#fff',
                                        'fontSize': '1rem'
                                    }
                                ),
                                html.Div(
                                    f"@{username} â€¢ {email}",
                                    style={
                                        'color': '#ccc',
                                        'fontSize': '0.8rem',
                                        'marginTop': '5px'
                                    }
                                )
                            ]
                        ),
                        html.Div(
                            style={
                                'backgroundColor': f'rgba({", ".join(str(int(c * 255)) for c in mpl.colors.to_rgb(HIGHLIGHT_COLOR if not is_current_patient else "#4ecdc4"))}, 0.1)',
                                'padding': '5px 10px',
                                'borderRadius': '12px',
                                'fontSize': '0.8rem',
                                'fontWeight': '500',
                                'color': HIGHLIGHT_COLOR if not is_current_patient else "#4ecdc4"
                            },
                            children=f"Nivel {activity_level}/10"
                        )
                    ]
                ),
                
                # BotÃ³n con ID simple
                html.Button(
                    "âœ“ Ya es paciente" if is_current_patient else "+ AÃ±adir como paciente",
                    id=button_id,  # ID simple
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': HIGHLIGHT_COLOR if not is_current_patient else 'transparent',
                        'border': f'1px solid {HIGHLIGHT_COLOR if not is_current_patient else "#4ecdc4"}',
                        'borderRadius': '6px',
                        'color': '#0a0a0a' if not is_current_patient else '#4ecdc4',
                        'fontWeight': '600',
                        'cursor': 'pointer' if not is_current_patient else 'default',
                        'opacity': '1' if not is_current_patient else '0.7',
                        'transition': 'all 0.3s ease'
                    },
                    disabled=is_current_patient
                ),
                
                # Input oculto con el username para el callback
                dcc.Input(
                    id=f"patient-username-{username.replace('.', '-').replace('@', '-')}",
                    type="hidden",
                    value=username
                )
            ]
        )
        result_items.append(result_item)
    
    return html.Div(result_items)

# ==========================================================
# CALLBACK CORREGIDO PARA AÃ‘ADIR PACIENTES (SIEMPRE MOSTRAR BOTÃ“N)
# ==========================================================

@app.callback(
    [Output("doctor-search-results", "children", allow_duplicate=True),
     Output("doctor-dashboard-refresh-trigger", "data", allow_duplicate=True)],
    [Input({"type": "add-patient-btn", "patient-username": dash.ALL}, "n_clicks")],
    [State("current-user", "data"),
     State({"type": "add-patient-btn", "patient-username": dash.ALL}, "id"),
     State("doctor-search-input", "value"),
     State("url", "pathname")],
    prevent_initial_call=True
)
def add_patient_to_doctor_simplified(n_clicks_list, current_user, button_ids, search_term, pathname):
    """AÃ±ade un paciente al mÃ©dico - VERSIÃ“N SIMPLIFICADA Y CORRECTA"""
    
    # Solo ejecutar en dashboard mÃ©dico
    if pathname != '/doctor-dashboard':
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    # Encontrar quÃ© botÃ³n se presionÃ³
    triggered_id = ctx.triggered[0]['prop_id']
    if triggered_id == '.' or not triggered_id:
        raise dash.exceptions.PreventUpdate
    
    try:
        # Extraer el username del paciente
        import json
        import ast
        
        # El formato es: {"type":"add-patient-btn","patient-username":"username"}.n_clicks
        json_str = triggered_id.split('.')[0]
        
        try:
            trigger_id_dict = json.loads(json_str)
        except:
            try:
                trigger_id_dict = ast.literal_eval(json_str.replace('"', "'"))
            except:
                print(f"âŒ Error parseando JSON: {json_str}")
                raise dash.exceptions.PreventUpdate
        
        patient_username = trigger_id_dict.get("patient-username")
        
        if not patient_username or not current_user:
            print("âŒ No se pudo obtener paciente o usuario")
            raise dash.exceptions.PreventUpdate
        
        print(f"ðŸ‘¨â€âš•ï¸ AÃ±adiendo paciente {patient_username} al mÃ©dico {current_user}")
        
        # AÃ±adir paciente (la funciÃ³n ya verifica si ya existe)
        success = add_patient_to_doctor(current_user, patient_username)
        
        if success:
            print(f"âœ… Paciente {patient_username} aÃ±adido/actualizado")
            
            # Actualizar resultados de bÃºsqueda
            search_results = search_users_by_name(search_term) if search_term else []
            updated_results = create_search_results_display(search_results, current_user)
            
            # Trigger para refrescar dashboard
            import time
            refresh_trigger = time.time()
            
            return updated_results, refresh_trigger
            
    except Exception as e:
        print(f"âŒ Error aÃ±adiendo paciente: {e}")
        import traceback
        traceback.print_exc()
    
    raise dash.exceptions.PreventUpdate

def create_search_results_display(search_results, current_user):
    """Crea la visualizaciÃ³n de resultados de bÃºsqueda - SIEMPRE muestra botÃ³n AÃ±adir"""
    
    if not search_results:
        return html.Div(
            "No se encontraron pacientes con ese criterio",
            style={'color': '#666', 'fontStyle': 'italic', 'padding': '10px', 'textAlign': 'center'}
        )
    
    # Obtener pacientes actuales del mÃ©dico
    current_patients = []
    if current_user in DOCTORS_DB:
        current_patients = DOCTORS_DB[current_user].get("patients", [])
    
    # Crear lista de resultados
    result_items = []
    for result in search_results:
        username = result["username"]
        full_name = result["full_name"]
        email = result["email"]
        activity_level = result["activity_level"]
        
        # Verificar si ya es paciente de este mÃ©dico
        is_current_patient = username in current_patients
        
        # Determinar el color del borde y del indicador
        border_color = "#4ecdc4" if is_current_patient else HIGHLIGHT_COLOR
        indicator_color = "#4ecdc4" if is_current_patient else HIGHLIGHT_COLOR
        
        # Crear el resultado
        result_item = html.Div(
            style={
                'backgroundColor': '#2b2b2b',
                'borderRadius': '8px',
                'padding': '15px',
                'marginBottom': '10px',
                'border': f'1px solid {border_color}'
            },
            children=[
                html.Div(
                    style={
                        'display': 'flex',
                        'justifyContent': 'space-between',
                        'alignItems': 'center',
                        'marginBottom': '10px'
                    },
                    children=[
                        html.Div(
                            style={'flex': '1'},
                            children=[
                                # Nombre con indicador visual si ya es paciente
                                html.Div(
                                    style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '5px'},
                                    children=[
                                        html.Div(
                                            full_name,
                                            style={
                                                'fontWeight': '600',
                                                'color': '#fff',
                                                'fontSize': '1rem'
                                            }
                                        ),
                                        # Indicador visual si ya es paciente
                                        html.Div(
                                            " âœ“ Ya es paciente" if is_current_patient else "",
                                            style={
                                                'color': '#4ecdc4',
                                                'fontSize': '0.8rem',
                                                'marginLeft': '8px',
                                                'fontWeight': '500',
                                                'display': 'inline' if is_current_patient else 'none'
                                            }
                                        )
                                    ]
                                ),
                                html.Div(
                                    f"@{username} â€¢ {email}",
                                    style={
                                        'color': '#ccc',
                                        'fontSize': '0.8rem',
                                        'marginTop': '5px'
                                    }
                                )
                            ]
                        ),
                        html.Div(
                            style={
                                'backgroundColor': f'rgba({", ".join(str(int(c * 255)) for c in mpl.colors.to_rgb(indicator_color))}, 0.1)',
                                'padding': '5px 10px',
                                'borderRadius': '12px',
                                'fontSize': '0.8rem',
                                'fontWeight': '500',
                                'color': indicator_color
                            },
                            children=f"Nivel {activity_level}/10"
                        )
                    ]
                ),
                
                # BotÃ³n - SIEMPRE se muestra como "AÃ±adir como paciente"
                html.Button(
                    "+ AÃ±adir como paciente",  # SIEMPRE este texto
                    id={
                        "type": "add-patient-btn",
                        "patient-username": username
                    },
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': HIGHLIGHT_COLOR,
                        'border': f'1px solid {HIGHLIGHT_COLOR}',
                        'borderRadius': '6px',
                        'color': '#0a0a0a',
                        'fontWeight': '600',
                        'cursor': 'pointer',
                        'transition': 'all 0.3s ease',
                        'marginTop': '10px'
                    },
                    # NUNCA deshabilitar el botÃ³n - siempre estÃ¡ activo
                    disabled=False
                ),
                
                # Mensaje informativo (opcional - puede ser mÃ¡s visible)
                html.Div(
                    "Nota: Si ya es paciente, al hacer clic se mostrarÃ¡ un mensaje pero no se aÃ±adirÃ¡ de nuevo",
                    style={
                        'color': '#666',
                        'fontSize': '0.7rem',
                        'fontStyle': 'italic',
                        'marginTop': '8px',
                        'textAlign': 'center',
                        'display': 'block' if is_current_patient else 'none'
                    }
                )
            ]
        )
        result_items.append(result_item)
    
    return html.Div(result_items)


@app.callback(
    Output("doctor-dashboard-refresh-trigger", "data"),
    [Input({"type": "add-patient-btn", "patient-username": dash.ALL}, "n_clicks")],
    prevent_initial_call=True
)
def refresh_doctor_dashboard(n_clicks_list):
    """Solo un trigger para refrescar el dashboard cuando se aÃ±ade un paciente"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    # Retornar un timestamp para forzar actualizaciÃ³n
    import time
    return time.time()

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input({"type": "patient-card", "patient-username": dash.ALL}, "n_dblclick")],
    [State({"type": "patient-card", "patient-username": dash.ALL}, "id"),
     State("current-user", "data"),
     State("user-type-store", "data"),
     State("url", "pathname")],
    prevent_initial_call=True
)
def handle_patient_double_click_corrected(n_dblclicks_list, card_ids, current_user, user_type, current_path):
    """Maneja el doble clic en una tarjeta de paciente para ver sus datos"""
    
    # Solo ejecutar si estamos en dashboard mÃ©dico
    if current_path != '/doctor-dashboard':
        raise dash.exceptions.PreventUpdate
    
    # Verificar que sea mÃ©dico
    if user_type != "doctor":
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    try:
        # Encontrar quÃ© tarjeta recibiÃ³ el doble clic
        trigger_id_str = ctx.triggered[0]['prop_id']
        print(f"ðŸ” Doble clic detectado: {trigger_id_str}")
        
        if trigger_id_str == '.' or not trigger_id_str:
            raise dash.exceptions.PreventUpdate
        
        # Extraer el username del paciente
        import json
        import re
        
        # El formato es: {"type":"patient-card","patient-username":"Haisea"}.n_dblclick
        json_str = trigger_id_str.split('.n_dblclick')[0]
        
        try:
            trigger_data = json.loads(json_str)
            patient_username = trigger_data.get("patient-username")
        except json.JSONDecodeError:
            match = re.search(r'"patient-username":"([^"]+)"', json_str)
            if match:
                patient_username = match.group(1)
            else:
                raise ValueError("No se pudo extraer el nombre de usuario")
        
        if not patient_username:
            raise dash.exceptions.PreventUpdate
        
        # Verificar que el paciente pertenezca al mÃ©dico
        if current_user in DOCTORS_DB:
            if patient_username in DOCTORS_DB[current_user].get("patients", []):
                print(f"ðŸ‘¨â€âš•ï¸ Redirigiendo mÃ©dico {current_user} a datos de paciente {patient_username}")
                return f'/inicio?patient={patient_username}'
        else:
            print(f"âš ï¸ MÃ©dico {current_user} no encontrado en DOCTORS_DB")
        
    except Exception as e:
        print(f"âŒ Error en doble clic: {e}")
        import traceback
        traceback.print_exc()
    
    raise dash.exceptions.PreventUpdate
    
# ==========================================================
# CALLBACK PARA INICIALIZAR STORES DE USUARIO (MEJORADO)
# ==========================================================

@app.callback(
    [Output("user-meals-store", "data"),
     Output("nutrition-totals-store", "data"),
     Output("user-goals-store", "data")],
    [Input("current-user", "data")],
    [State("url", "pathname")],
    prevent_initial_call=False
)
def initialize_user_data(current_user, current_path):
    """Inicializa los stores con datos del usuario - VERSIÃ“N SIMPLIFICADA"""
    print(f"ðŸ” INITIALIZE USER DATA - user: {current_user}, path: {current_path}")
    
    # SI NO HAY USUARIO, RETORNAR DATOS VACÃOS
    if not current_user:
        print("âš ï¸ No hay usuario activo, retornando datos vacÃ­os")
        return [], {
            'calories': 0,
            'carbs': 0,
            'protein': 0,
            'fat': 0
        }, {
            "fitness": [],
            "health": []
        }
    
    # SI ESTAMOS EN ONBOARDING, NO CARGAR DATOS AÃšN
    if current_path == '/onboarding':
        print("ðŸŽ¯ En onboarding, no cargar datos de usuario aÃºn")
        return [], {
            'calories': 0,
            'carbs': 0,
            'protein': 0,
            'fat': 0
        }, {
            "fitness": [],
            "health": []
        }
    
    # Cargar comidas
    meals = load_user_meals(current_user)
    print(f"ðŸ“Š Comidas cargadas: {len(meals) if meals else 0}")
    
    # Calcular totales
    if meals:
        totals = calculate_daily_totals(meals)
    else:
        # Valores por defecto si no hay comidas
        totals = {
            'calories': 0,
            'carbs': 0,
            'protein': 0,
            'fat': 0
        }
    
    # Cargar objetivos
    goals = get_user_goals_for_display(current_user)
    
    print(f"âœ… Datos inicializados para {current_user}: {len(meals)} comidas")
    
    return meals, totals, goals

# ==========================================================
# CALLBACK PARA ACTUALIZAR STORES DESPUÃ‰S DE ACCIONES DE NUTRICIÃ“N
# ==========================================================

@app.callback(
    [Output("user-meals-store", "data", allow_duplicate=True),
     Output("nutrition-totals-store", "data", allow_duplicate=True),
     Output("user-goals-store", "data", allow_duplicate=True)],
    [Input("btn-submit-meal", "n_clicks"),
     Input("btn-registrar-agua", "n_clicks")],
    [State("current-user", "data")],
    prevent_initial_call=True
)
def update_stores_after_nutrition_actions(meal_clicks, water_clicks, current_user):
    """Actualiza los stores despuÃ©s de acciones de nutriciÃ³n"""
    ctx = dash.callback_context
    
    # Si no hay trigger o usuario, no hacer nada
    if not ctx.triggered or not current_user:
        raise dash.exceptions.PreventUpdate
    
    print(f"ðŸ” NUTRITION ACTIONS - Triggered, recargando datos para {current_user}")
    
    # Recargar todos los datos del usuario
    meals = load_user_meals(current_user)
    totals = calculate_daily_totals(meals) if meals else {
        'calories': 2847,
        'carbs': 180,
        'protein': 95,
        'fat': 65
    }
    goals = get_user_goals_for_display(current_user)
    
    print(f"âœ… Stores de nutriciÃ³n actualizados para {current_user}")
    return meals, totals, goals

# ==========================================================
# CALLBACK PARA ACTUALIZAR STORES DESPUÃ‰S DE ACCIONES DE OBJETIVOS
# ==========================================================

@app.callback(
    [Output("user-meals-store", "data", allow_duplicate=True),
     Output("nutrition-totals-store", "data", allow_duplicate=True),
     Output("user-goals-store", "data", allow_duplicate=True)],
    [Input("btn-submit-goal", "n_clicks"),
     Input({"type": "complete-goal", "goal-id": dash.ALL}, "n_clicks"),
     Input({"type": "delete-goal", "goal-id": dash.ALL}, "n_clicks")],
    [State("current-user", "data")],
    prevent_initial_call=True
)
def update_stores_after_goal_actions(goal_clicks, complete_clicks, delete_clicks, current_user):
    """Actualiza los stores despuÃ©s de acciones de objetivos"""
    ctx = dash.callback_context
    
    # Si no hay trigger o usuario, no hacer nada
    if not ctx.triggered or not current_user:
        raise dash.exceptions.PreventUpdate
    
    print(f"ðŸ” GOAL ACTIONS - Triggered, recargando datos para {current_user}")
    
    # Recargar todos los datos del usuario
    meals = load_user_meals(current_user)
    totals = calculate_daily_totals(meals) if meals else {
        'calories': 2847,
        'carbs': 180,
        'protein': 95,
        'fat': 65
    }
    goals = get_user_goals_for_display(current_user)
    
    print(f"âœ… Stores de objetivos actualizados para {current_user}")
    return meals, totals, goals

# ==========================================================
# CALLBACK PARA EL MODAL DE AGREGAR COMIDA (CORREGIDO)
# ==========================================================

@app.callback(
    Output("modal-add-meal", "is_open"),
    [Input("btn-agregar-comida", "n_clicks"),
     Input("btn-cancel-meal", "n_clicks"),
     Input("btn-submit-meal", "n_clicks")],
    [State("modal-add-meal", "is_open"),
     State("url", "pathname")],  # AÃ‘ADIR pathname para verificaciÃ³n
    prevent_initial_call=True
)
def toggle_meal_modal(open_clicks, cancel_clicks, submit_clicks, is_open, pathname):
    """Abre/cierra el modal de agregar comida - VERSIÃ“N CORREGIDA"""
    
    # Verificar que estamos en la pÃ¡gina correcta
    if pathname != '/nutricion':
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id in ["btn-agregar-comida", "btn-cancel-meal"]:
        return not is_open
    elif trigger_id == "btn-submit-meal":
        return False
    
    return is_open

@app.callback(
    [Output("btn-agregar-comida", "children"),
     Output("modal-add-meal", "is_open", allow_duplicate=True),
     Output("meal-description-input", "value"),
     Output("meal-time-input", "value"),
     Output("meal-type-dropdown", "value"),
     Output("carbs-input", "value"),
     Output("protein-input", "value"),
     Output("fat-input", "value"),
     Output("calories-input", "value")],
    [Input("btn-submit-meal", "n_clicks")],
    [State("meal-type-dropdown", "value"),
     State("meal-time-input", "value"),
     State("meal-description-input", "value"),
     State("carbs-input", "value"),
     State("protein-input", "value"),
     State("fat-input", "value"),
     State("calories-input", "value"),
     State("current-user", "data"),
     State("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def submit_new_meal(submit_clicks, meal_type, meal_time, description, 
                   carbs, protein, fat, calories, current_user, pathname):
    """Procesa la nueva comida agregada - VERSIÃ“N CORREGIDA"""
    
    # Verificar que estamos en la pÃ¡gina correcta
    if pathname != '/nutricion':
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered or submit_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    if not description or not current_user:
        print("âš ï¸ No hay descripciÃ³n o usuario para agregar comida")
        raise dash.exceptions.PreventUpdate
    
    print(f"ðŸ“ Agregando nueva comida para {current_user}: {description}")
    
    # Crear objeto de la comida
    meal_data = {
        "type": meal_type or "snacks",
        "time": meal_time or datetime.now().strftime("%H:%M"),
        "description": description,
        "carbs": int(carbs) if carbs else 0,
        "protein": int(protein) if protein else 0,
        "fat": int(fat) if fat else 0,
        "calories": int(calories) if calories else 0
    }
    
    # Si no se ingresaron valores de macronutrientes, estimarlos
    if not (carbs or protein or fat or calories):
        print("ðŸ“Š Estimando nutrientes desde descripciÃ³n")
        estimated_nutrients = estimate_nutrients_from_description(description)
        meal_data.update(estimated_nutrients)
    
    print(f"ðŸ½ï¸ Datos de comida: {meal_data}")
    
    # Guardar la comida
    success = save_user_meal(current_user, meal_data)
    
    if success:
        # Mensaje de Ã©xito en el botÃ³n
        success_message = [
            html.I(className="bi bi-check-circle me-2"),
            "Â¡Comida agregada!"
        ]
        
        # Resetear formulario
        return success_message, False, "", "", None, None, None, None, None
    else:
        print("âŒ Error al guardar la comida")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
@app.callback(
    [Output("meal-description-input", "value", allow_duplicate=True),
     Output("meal-time-input", "value", allow_duplicate=True),
     Output("meal-type-dropdown", "value", allow_duplicate=True),
     Output("carbs-input", "value", allow_duplicate=True),
     Output("protein-input", "value", allow_duplicate=True),
     Output("fat-input", "value", allow_duplicate=True),
     Output("calories-input", "value", allow_duplicate=True)],
    [Input("modal-add-meal", "is_open"),
     Input("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def reset_meal_form_when_opening(is_open, current_path):
    """Restablece el formulario cuando se abre el modal de comida"""
    
    # SOLO EJECUTAR SI ESTAMOS EN NUTRICIÃ“N
    if current_path != '/nutricion' and current_path is not None:
        raise dash.exceptions.PreventUpdate
    
    if is_open:
        print("ðŸ”“ Abriendo modal, reset formulario")
        # Limpiar campos del formulario
        return "", "", None, None, None, None, None
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# ==========================================================
# CALLBACK PARA ACTUALIZAR LA INTERFAZ DE NUTRICIÃ“N (MODIFICADO)
# ==========================================================

@app.callback(
    [Output("calorias-total", "children"),
     Output("carbohidratos-total", "children"),
     Output("proteinas-total", "children"),
     Output("grasas-total", "children"),
     Output("hidratacion-progreso", "children"),
     Output("hidratacion-texto", "children"),
     Output("hidratacion-circle-progress", "style"),
     Output("meal-list-desayuno", "children"),
     Output("meal-list-almuerzo", "children"),
     Output("meal-list-cena", "children"),
     Output("meal-list-snacks", "children")],
    [Input("nutrition-totals-store", "data"),
     Input("user-meals-store", "data"),
     Input("water-tracker-store", "data")],  # NUEVO: Agregar store de agua
    [State("current-user", "data"),
     State("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=False
)
def update_nutrition_display(totals, meals_data, water_data, current_user, pathname):
    """Actualiza la interfaz de nutriciÃ³n con datos reales - VERSIÃ“N CORREGIDA"""
    
    # Solo actualizar si estamos en la pÃ¡gina de nutriciÃ³n
    if pathname != '/nutricion' and pathname is not None:
        raise dash.exceptions.PreventUpdate
    
    print(f"ðŸ” UPDATE NUTRITION DISPLAY - user: {current_user}, tiene comidas: {len(meals_data) if meals_data else 0}")
    
    # Si no hay datos, usar valores por defecto o cargar desde archivo
    if not totals:
        if current_user:
            print("ðŸ“‹ Cargando totales desde archivo")
            if not meals_data:
                meals_data = load_user_meals(current_user)
            totals = calculate_daily_totals(meals_data)
        else:
            print("ðŸ‘¤ Sin usuario, usando valores por defecto")
            totals = {
                'calories': 2847,
                'carbs': 180,
                'protein': 95,
                'fat': 65
            }
    
    if not meals_data and current_user:
        print("ðŸ½ï¸ Cargando comidas desde archivo")
        meals_data = load_user_meals(current_user)
    
    print(f"ðŸ“Š Totales a mostrar: {totals}")
    
    # Formatear comidas por tipo
    breakfast_items = []
    lunch_items = []
    dinner_items = []
    snacks_items = []
    
    if meals_data:
        print(f"ðŸ“ Procesando {len(meals_data)} comidas")
        for meal in meals_data:
            item = html.Div(
                f"â€¢ {meal.get('description', '')} ({meal.get('time', '')})",
                style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'}
            )
            
            meal_type = meal.get('type')
            if meal_type == 'desayuno':
                breakfast_items.append(item)
            elif meal_type == 'almuerzo':
                lunch_items.append(item)
            elif meal_type == 'cena':
                dinner_items.append(item)
            elif meal_type == 'snacks':
                snacks_items.append(item)
    
    # Si no hay comidas, mostrar ejemplos
    if not breakfast_items:
        breakfast_items = [
            html.Div("â€¢ Avena con frutas y nueces", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'}),
            html.Div("â€¢ CafÃ© negro sin azÃºcar", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'})
        ]
    
    if not lunch_items:
        lunch_items = [
            html.Div("â€¢ Ensalada de pollo a la parrilla", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'}),
            html.Div("â€¢ Quinoa y vegetales al vapor", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'}),
            html.Div("â€¢ Agua con limÃ³n", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'})
        ]
    
    if not dinner_items:
        dinner_items = [
            html.Div("â€¢ SalmÃ³n a la plancha", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'}),
            html.Div("â€¢ EspÃ¡rragos y brÃ³coli", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'}),
            html.Div("â€¢ Batido de proteÃ­nas", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'})
        ]
    
    if not snacks_items:
        snacks_items = [
            html.Div("â€¢ Manzana verde (10:30)", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'}),
            html.Div("â€¢ Yogur griego con almendras (16:00)", style={'color': '#ccc', 'marginBottom': '5px', 'fontSize': '0.9rem'})
        ]
    
    # Obtener datos de agua
    if water_data:
        water_current = water_data.get('current', 2.1)
        water_target = water_data.get('target', 3.0)
    else:
        water_current = 2.1
        water_target = 3.0
    
    # Calcular progreso de hidrataciÃ³n
    water_progress = int((water_current / water_target) * 100) if water_target > 0 else 0
    
    # Crear estilo para el cÃ­rculo de progreso
    water_circle_style = {
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'width': '100%',
        'height': '100%',
        'borderRadius': '50%',
        'border': '10px solid transparent',
        'borderTop': f'10px solid {HIGHLIGHT_COLOR}',
        'borderRight': f'10px solid {HIGHLIGHT_COLOR}',
        'transform': f'rotate({int(water_progress * 3.6)}deg)',  # Convertir porcentaje a grados
        'boxSizing': 'border-box'
    }
    
    print(f"âœ… NutriciÃ³n actualizada: {totals.get('calories', 0)} cal, Agua: {water_current}L")
    
    return (
        f"{totals.get('calories', 2847)}",  # CalorÃ­as totales
        f"{totals.get('carbs', 180)}g",     # Carbohidratos
        f"{totals.get('protein', 95)}g",    # ProteÃ­nas
        f"{totals.get('fat', 65)}g",        # Grasas
        f"{water_current:.1f}L",            # Progreso de hidrataciÃ³n
        f"de {water_target:.1f}L objetivo", # Texto de hidrataciÃ³n
        water_circle_style,                  # Estilo del cÃ­rculo de progreso
        breakfast_items,                     # Lista de desayunos
        lunch_items,                         # Lista de almuerzos
        dinner_items,                        # Lista de cenas
        snacks_items                         # Lista de snacks
    )

# ==========================================================
# CALLBACK PARA REGISTRAR AGUA (MODIFICADO)
# ==========================================================

@app.callback(
    [Output("btn-registrar-agua", "children"),
     Output("water-tracker-store", "data", allow_duplicate=True)],
    Input("btn-registrar-agua", "n_clicks"),
    [State("water-tracker-store", "data"),
     State("current-user", "data"),
     State("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def register_water(water_clicks, water_data, current_user, pathname):
    """Registra el consumo de agua - VERSIÃ“N CORREGIDA"""
    
    # Verificar que estamos en la pÃ¡gina correcta
    if pathname != '/nutricion':
        raise dash.exceptions.PreventUpdate
    
    if not water_clicks:
        return dash.no_update, dash.no_update
    
    print(f"ðŸ’§ Registrando agua para {current_user}")
    
    # Obtener datos actuales
    if water_data:
        current = water_data.get('current', 2.1)
        target = water_data.get('target', 3.0)
    else:
        current = 2.1
        target = 3.0
    
    # AÃ±adir 250ml (0.25L)
    new_current = current + 0.25
    
    # No exceder el objetivo
    if new_current > target:
        new_current = target
    
    # Actualizar store
    updated_water_data = {
        'current': round(new_current, 2),
        'target': target
    }
    
    # Mensaje de Ã©xito
    success_message = [
        html.I(className="bi bi-check-circle me-2"),
        f"Â¡Agua registrada! ({new_current:.2f}L)"
    ]
    
    return success_message, updated_water_data

# ==========================================================
# CALLBACKS PARA OBJETIVOS - VERIFICACIÃ“N, ELIMINACIÃ“N Y MODAL
# ==========================================================

# ==========================================================
# 1. CALLBACK PARA SUBMIT DE NUEVO OBJETIVO
# ==========================================================

@app.callback(
    [Output("btn-agregar-objetivo", "children"),
     Output("modal-add-goal", "is_open", allow_duplicate=True),
     Output("goal-name-input", "value", allow_duplicate=True),
     Output("goal-description-input", "value", allow_duplicate=True),
     Output("goal-target-input", "value", allow_duplicate=True),
     Output("goal-deadline-dropdown", "value", allow_duplicate=True)],
    [Input("btn-submit-goal", "n_clicks")],
    [State("goal-name-input", "value"),
     State("goal-description-input", "value"),
     State("goal-target-input", "value"),
     State("goal-deadline-dropdown", "value"),
     State("goal-type-text", "children"),
     State("current-user", "data"),
     State("url", "pathname")],
    prevent_initial_call=True
)
def submit_new_goal_corrected(submit_clicks, name, description, target, deadline, goal_type, current_user, pathname):
    """Procesa el nuevo objetivo agregado - VERSIÃ“N CORREGIDA Y SIMPLIFICADA"""
    
    if pathname != '/objetivos':
        raise dash.exceptions.PreventUpdate
    
    if not submit_clicks or not name or not current_user:
        raise dash.exceptions.PreventUpdate
    
    # Determinar el tipo de objetivo
    goal_type_key = "health" if goal_type == "Salud" else "fitness"
    
    # Crear objeto del objetivo
    goal_data = {
        "name": name,
        "description": description or "",
        "target": target or "",
        "deadline": deadline or "1_month",
        "type": goal_type_key
    }
    
    print(f"ðŸ“ Agregando nuevo objetivo para {current_user}: {name} ({goal_type_key})")
    
    # Guardar el objetivo
    success = add_user_goal(current_user, goal_type_key, goal_data)
    
    if success:
        # Mensaje de Ã©xito en el botÃ³n
        success_message = [
            html.I(className="bi bi-check-circle me-2"),
            "Â¡Objetivo agregado!"
        ]
        
        # Resetear formulario
        return success_message, False, "", "", "", None
    else:
        print("âŒ Error al agregar objetivo")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# ==========================================================
# CALLBACK PARA RESETAR MENSAJE DE Ã‰XITO
# ==========================================================

@app.callback(
    Output("btn-agregar-objetivo", "children", allow_duplicate=True),
    [Input("btn-agregar-objetivo", "children")],
    [State("url", "pathname")],
    prevent_initial_call=True
)
def reset_success_message(children, pathname):
    """Resetea el mensaje de Ã©xito despuÃ©s de agregar objetivo"""
    
    if pathname != '/objetivos':
        raise dash.exceptions.PreventUpdate
    
    # Verificar si el botÃ³n muestra mensaje de Ã©xito
    if isinstance(children, list) and len(children) > 0:
        # Si el botÃ³n tiene icono de check, significa que acaba de agregar
        # Esperar 2 segundos y luego restaurar el texto original
        import time
        time.sleep(2)
        
        return [
            html.I(className="bi bi-plus-circle me-2"),
            "Agregar Nuevo Objetivo"
        ]
    
    return dash.no_update
    
# ==========================================================
# 2. CALLBACK PARA MANEJAR VERIFICACIÃ“N DE OBJETIVOS
# ==========================================================

@app.callback(
    Output("user-goals-store", "data", allow_duplicate=True),
    [Input({"type": "complete-goal", "goal-id": dash.ALL}, "n_clicks")],
    [State("current-user", "data"),
     State("user-goals-store", "data"),
     State("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def handle_complete_goal(n_clicks_list, current_user, current_goals, pathname):
    """Maneja el clic en el botÃ³n de verificaciÃ³n - VERSIÃ“N CORREGIDA"""
    
    # Solo ejecutar en pÃ¡gina de objetivos
    if pathname != '/objetivos':
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    
    if not ctx.triggered or not current_user:
        print("âš ï¸ No hay trigger o usuario en complete_goal")
        raise dash.exceptions.PreventUpdate
    
    # Obtener el botÃ³n que se hizo clic
    trigger_id = ctx.triggered[0]['prop_id']
    
    try:
        # Parsear el ID del objetivo desde el trigger
        if trigger_id == "." or not trigger_id:
            print("âš ï¸ Trigger vacÃ­o en complete_goal")
            raise dash.exceptions.PreventUpdate
        
        print(f"ðŸ” Trigger recibido: {trigger_id}")
        
        # Extraer el goal-id del trigger
        try:
            # El trigger_id viene como un string JSON como: {'type': 'complete-goal', 'goal-id': 'goal_1234'}
            # Necesitamos parsearlo correctamente
            import json
            import re
            
            # Limpiar el string
            clean_trigger = trigger_id.replace("'", '"')
            # Extraer el JSON
            match = re.search(r'\{.*\}', clean_trigger)
            if match:
                trigger_json = match.group()
                trigger_data = json.loads(trigger_json)
                goal_id = trigger_data.get('goal-id')
            else:
                # Si no podemos parsear como JSON, intentar otra forma
                if '"goal-id"' in clean_trigger:
                    goal_id = clean_trigger.split('"goal-id":')[1].split('"')[1]
                else:
                    raise ValueError("No se pudo encontrar goal-id")
        except Exception as parse_error:
            print(f"âš ï¸ Error parseando trigger: {parse_error}")
            # Intentar mÃ©todo alternativo
            try:
                if 'goal-id' in trigger_id:
                    parts = trigger_id.split('goal-id')
                    if len(parts) > 1:
                        goal_id_part = parts[1].strip('":,}')
                        goal_id = goal_id_part.strip('"\'')
            except:
                goal_id = None
        
        if not goal_id:
            print("âŒ No se pudo extraer goal-id del trigger")
            raise dash.exceptions.PreventUpdate
        
        print(f"âœ… Marcando objetivo como completado: {goal_id}")
        
        # Marcar como completado
        success = mark_goal_completed(current_user, goal_id)
        
        if success:
            # Recargar objetivos actualizados
            updated_goals = get_user_goals_for_display(current_user)
            print(f"âœ… Objetivo {goal_id} marcado como completado exitosamente")
            return updated_goals
        else:
            print(f"âŒ No se pudo marcar objetivo {goal_id} como completado")
    
    except Exception as e:
        print(f"âŒ Error al completar objetivo: {e}")
        import traceback
        traceback.print_exc()
    
    raise dash.exceptions.PreventUpdate

# ==========================================================
# 3. CALLBACK PARA MANEJAR ELIMINACIÃ“N DE OBJETIVOS
# ==========================================================

@app.callback(
    Output("user-goals-store", "data", allow_duplicate=True),
    [Input({"type": "delete-goal", "goal-id": dash.ALL}, "n_clicks")],
    [State("current-user", "data"),
     State("user-goals-store", "data"),
     State("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def handle_delete_goal(n_clicks_list, current_user, current_goals, pathname):
    """Maneja el clic en el botÃ³n de eliminaciÃ³n - VERSIÃ“N CORREGIDA"""
    
    # Solo ejecutar en pÃ¡gina de objetivos
    if pathname != '/objetivos':
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    
    if not ctx.triggered or not current_user:
        print("âš ï¸ No hay trigger o usuario en delete_goal")
        raise dash.exceptions.PreventUpdate
    
    # Obtener el botÃ³n que se hizo clic
    trigger_id = ctx.triggered[0]['prop_id']
    
    try:
        # Parsear el ID del objetivo desde el trigger
        if trigger_id == "." or not trigger_id:
            print("âš ï¸ Trigger vacÃ­o en delete_goal")
            raise dash.exceptions.PreventUpdate
        
        print(f"ðŸ” Trigger recibido: {trigger_id}")
        
        # Extraer el goal-id del trigger
        try:
            # El trigger_id viene como un string JSON
            import json
            import re
            
            # Limpiar el string
            clean_trigger = trigger_id.replace("'", '"')
            # Extraer el JSON
            match = re.search(r'\{.*\}', clean_trigger)
            if match:
                trigger_json = match.group()
                trigger_data = json.loads(trigger_json)
                goal_id = trigger_data.get('goal-id')
            else:
                # Si no podemos parsear como JSON, intentar otra forma
                if '"goal-id"' in clean_trigger:
                    goal_id = clean_trigger.split('"goal-id":')[1].split('"')[1]
                else:
                    raise ValueError("No se pudo encontrar goal-id")
        except Exception as parse_error:
            print(f"âš ï¸ Error parseando trigger: {parse_error}")
            # Intentar mÃ©todo alternativo
            try:
                if 'goal-id' in trigger_id:
                    parts = trigger_id.split('goal-id')
                    if len(parts) > 1:
                        goal_id_part = parts[1].strip('":,}')
                        goal_id = goal_id_part.strip('"\'')
            except:
                goal_id = None
        
        if not goal_id:
            print("âŒ No se pudo extraer goal-id del trigger")
            raise dash.exceptions.PreventUpdate
        
        print(f"ðŸ—‘ï¸ Eliminando objetivo: {goal_id}")
        
        # Eliminar el objetivo
        success = delete_user_goal(current_user, goal_id)
        
        if success:
            # Recargar objetivos actualizados
            updated_goals = get_user_goals_for_display(current_user)
            print(f"âœ… Objetivo {goal_id} eliminado exitosamente")
            return updated_goals
        else:
            print(f"âŒ No se pudo eliminar objetivo {goal_id}")
    
    except Exception as e:
        print(f"âŒ Error al eliminar objetivo: {e}")
        import traceback
        traceback.print_exc()
    
    raise dash.exceptions.PreventUpdate

# ==========================================================
# 4. CALLBACK PARA RESET DE FORMULARIO AL ABRIR MODAL
# ==========================================================

@app.callback(
    [Output("choose-goal-type", "style", allow_duplicate=True),
     Output("goal-form-container", "style", allow_duplicate=True),
     Output("goal-name-input", "value", allow_duplicate=True),
     Output("goal-description-input", "value", allow_duplicate=True),
     Output("goal-target-input", "value", allow_duplicate=True),
     Output("goal-deadline-dropdown", "value", allow_duplicate=True)],
    [Input("url", "pathname"),  # AÃ‘ADIR pathname como Input
     Input("modal-add-goal", "is_open")],
    prevent_initial_call=True
)
def reset_goal_form_when_opening(current_path, is_open):
    """Restablece el formulario cuando se abre el modal de objetivos"""
    
    # SOLO EJECUTAR SI ESTAMOS EN OBJETIVOS
    if current_path != '/objetivos' and current_path is not None:
        raise dash.exceptions.PreventUpdate
    
    if is_open:
        print("ðŸ”“ Abriendo modal de objetivos, reset formulario")
        # Mostrar selecciÃ³n de tipo y ocultar formulario, limpiar campos
        return (
            {'display': 'block'},      # Mostrar selecciÃ³n de tipo
            {'display': 'none'},       # Ocultar formulario
            "",                        # Limpiar nombre
            "",                        # Limpiar descripciÃ³n
            "",                        # Limpiar objetivo
            None                       # Limpiar deadline
        )
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# ==========================================================
# 5. CALLBACK PARA ACTUALIZAR LA INTERFAZ DE OBJETIVOS (PRINCIPAL)
# ==========================================================

@app.callback(
    [Output("fitness-goals-list", "children"),
     Output("health-goals-list", "children"),
     Output("progreso-total-percent", "children"),
     Output("objetivos-activos-count", "children")],
    [Input("user-goals-store", "data"),
     Input("url", "pathname")],
    [State("current-user", "data")],
    prevent_initial_call=False
)
def update_goals_display_simple(goals_data, pathname, current_user):
    """Actualiza la interfaz de objetivos - VERSIÃ“N SIMPLIFICADA"""
    
    print(f"ðŸ” UPDATE GOALS DISPLAY SIMPLE - pathname: {pathname}, user: {current_user}")
    
    # Solo actualizar si estamos en la pÃ¡gina de objetivos
    if pathname != '/objetivos':
        raise dash.exceptions.PreventUpdate
    
    # Si no hay datos pero hay usuario, cargar desde archivo
    if not goals_data and current_user:
        print("ðŸ“‹ Cargando objetivos desde archivo")
        goals_data = get_user_goals_for_display(current_user)
    
    if not goals_data:
        print("ðŸŽ¯ Sin objetivos, usando estructura vacÃ­a")
        goals_data = {"fitness": [], "health": []}
    
    print(f"ðŸ“Š Objetivos a mostrar: {len(goals_data.get('fitness', []))} fitness, {len(goals_data.get('health', []))} health")
    
    # Crear elementos de lista para objetivos de fitness
    fitness_items = []
    for goal in goals_data.get("fitness", []):
        goal_id = goal.get("id", "")
        goal_status = goal.get("status", "active")
        progress = goal.get("progress", 0)
        
        # Determinar si estÃ¡ completado
        is_completed = goal_status == "completed"
        
        # Estilo diferente para objetivos completados
        card_style = {
            'backgroundColor': '#141414' if not is_completed else '#0a2a38',
            'padding': '15px',
            'marginBottom': '10px',
            'borderRadius': '10px',
            'border': '1px solid #2b2b2b' if not is_completed else f'1px solid {HIGHLIGHT_COLOR}',
            'listStyleType': 'none',
            'position': 'relative'
        }
        
        # Texto tachado si estÃ¡ completado
        name_style = {
            'color': '#fff' if not is_completed else '#888',
            'fontWeight': '500',
            'textDecoration': 'line-through' if is_completed else 'none',
            'flex': '1',
            'marginRight': '10px'
        }
        
        # Barra de progreso con color diferente si estÃ¡ completado
        progress_color = HIGHLIGHT_COLOR if not is_completed else '#4ecdc4'
        
        item = html.Li(
            [
                # Contenedor principal
                html.Div([
                    # Primera fila: Emoji, nombre y botones
                    html.Div([
                        # Emoji
                        html.Span(f"{goal.get('emoji', 'ðŸŽ¯')} ", 
                                 style={'marginRight': '10px', 'fontSize': '1.2rem'}),
                        
                        # Nombre y objetivo
                        html.Div([
                            html.Span(goal.get("name", "Sin nombre"), style=name_style),
                            html.Span(f" - {goal.get('target', '')}", 
                                     style={'color': '#ccc' if not is_completed else '#666', 
                                            'fontSize': '0.9rem'})
                        ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}),
                        
                        # Botones de acciÃ³n
                        html.Div([
                            # BotÃ³n de verificaciÃ³n (solo si no estÃ¡ completado)
                            html.Button(
                                html.I(className="bi bi-check-circle"),
                                id={"type": "complete-goal", "goal-id": goal_id},
                                n_clicks=0,
                                style={
                                    'backgroundColor': 'transparent',
                                    'border': f'1px solid {HIGHLIGHT_COLOR}',
                                    'color': HIGHLIGHT_COLOR,
                                    'padding': '6px 12px',
                                    'borderRadius': '6px',
                                    'cursor': 'pointer' if not is_completed else 'not-allowed',
                                    'marginRight': '8px',
                                    'opacity': '1' if not is_completed else '0.5',
                                    'transition': 'all 0.3s ease',
                                    'display': 'inline-block'
                                },
                                disabled=is_completed,
                                title="Marcar como completado" if not is_completed else "Ya completado"
                            ),
                            
                            # BotÃ³n de eliminaciÃ³n
                            html.Button(
                                html.I(className="bi bi-trash"),
                                id={"type": "delete-goal", "goal-id": goal_id},
                                n_clicks=0,
                                style={
                                    'backgroundColor': 'transparent',
                                    'border': '1px solid #ff6b6b',
                                    'color': '#ff6b6b',
                                    'padding': '6px 12px',
                                    'borderRadius': '6px',
                                    'cursor': 'pointer',
                                    'transition': 'all 0.3s ease',
                                    'display': 'inline-block'
                                },
                                title="Eliminar objetivo"
                            )
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'marginBottom': '15px'}),
                    
                    # DescripciÃ³n (si existe)
                    html.Div(
                        goal.get("description", ""),
                        style={
                            'color': '#aaa',
                            'fontSize': '0.9rem',
                            'marginBottom': '10px',
                            'display': 'block' if goal.get("description") else 'none'
                        }
                    ),
                    
                    # Segunda fila: Barra de progreso
                    html.Div([
                        html.Div(
                            style={
                                'width': '100%',
                                'height': '8px',
                                'backgroundColor': '#2b2b2b',
                                'borderRadius': '4px',
                                'overflow': 'hidden'
                            },
                            children=html.Div(
                                style={
                                    'width': f"{progress}%",
                                    'height': '100%',
                                    'backgroundColor': progress_color,
                                    'borderRadius': '4px',
                                    'transition': 'width 0.5s ease'
                                }
                            )
                        ),
                    ]),
                    
                    # Tercera fila: InformaciÃ³n de progreso y fecha
                    html.Div([
                        html.Div([
                            html.Span(
                                f"Progreso: {progress}%",
                                style={'color': progress_color, 'fontSize': '0.9rem'}
                            ),
                            html.Span(
                                " âœ… Completado" if is_completed else "",
                                style={'color': '#4ecdc4', 'fontSize': '0.8rem', 'marginLeft': '10px', 'fontWeight': '600'}
                            )
                        ], style={'flex': '1'}),
                        
                        html.Div([
                            html.Span(
                                f"Creado: {goal.get('created_at', '').split()[0] if goal.get('created_at') else ''}",
                                style={'color': '#666', 'fontSize': '0.8rem'}
                            ),
                            html.Span(
                                f" | Completado: {goal.get('completed_at', '').split()[0] if goal.get('completed_at') else ''}",
                                style={'color': '#4ecdc4', 'fontSize': '0.8rem', 
                                       'display': 'inline' if is_completed else 'none'}
                            )
                        ], style={'textAlign': 'right'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginTop': '8px'})
                ])
            ],
            style=card_style,
            id=f"goal-item-{goal_id}"
        )
        fitness_items.append(item)
    
    if not fitness_items:
        fitness_items = [html.Li(
            "No hay objetivos de fitness activos. Â¡Agrega uno!",
            style={'color': '#ccc', 'fontStyle': 'italic', 'padding': '15px'}
        )]
    
    # Crear elementos de lista para objetivos de salud
    health_items = []
    for goal in goals_data.get("health", []):
        goal_id = goal.get("id", "")
        goal_status = goal.get("status", "active")
        progress = goal.get("progress", 0)
        
        # Determinar si estÃ¡ completado
        is_completed = goal_status == "completed"
        
        # Estilo diferente para objetivos completados
        card_style = {
            'backgroundColor': '#141414' if not is_completed else '#0a2a38',
            'padding': '15px',
            'marginBottom': '10px',
            'borderRadius': '10px',
            'border': '1px solid #2b2b2b' if not is_completed else f'1px solid #4ecdc4',
            'listStyleType': 'none',
            'position': 'relative'
        }
        
        # Texto tachado si estÃ¡ completado
        name_style = {
            'color': '#fff' if not is_completed else '#888',
            'fontWeight': '500',
            'textDecoration': 'line-through' if is_completed else 'none',
            'flex': '1',
            'marginRight': '10px'
        }
        
        # Barra de progreso con color diferente si estÃ¡ completado
        progress_color = '#4ecdc4' if not is_completed else '#4ecdc4'
        
        item = html.Li(
            [
                # Contenedor principal
                html.Div([
                    # Primera fila: Emoji, nombre y botones
                    html.Div([
                        # Emoji
                        html.Span(f"{goal.get('emoji', 'â¤ï¸')} ", 
                                 style={'marginRight': '10px', 'fontSize': '1.2rem'}),
                        
                        # Nombre y objetivo
                        html.Div([
                            html.Span(goal.get("name", "Sin nombre"), style=name_style),
                            html.Span(f" - {goal.get('target', '')}", 
                                     style={'color': '#ccc' if not is_completed else '#666', 
                                            'fontSize': '0.9rem'})
                        ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}),
                        
                        # Botones de acciÃ³n
                        html.Div([
                            # BotÃ³n de verificaciÃ³n (solo si no estÃ¡ completado)
                            html.Button(
                                html.I(className="bi bi-check-circle"),
                                id={"type": "complete-goal", "goal-id": goal_id},
                                n_clicks=0,
                                style={
                                    'backgroundColor': 'transparent',
                                    'border': f'1px solid #4ecdc4',
                                    'color': '#4ecdc4',
                                    'padding': '6px 12px',
                                    'borderRadius': '6px',
                                    'cursor': 'pointer' if not is_completed else 'not-allowed',
                                    'marginRight': '8px',
                                    'opacity': '1' if not is_completed else '0.5',
                                    'transition': 'all 0.3s ease',
                                    'display': 'inline-block'
                                },
                                disabled=is_completed,
                                title="Marcar como completado" if not is_completed else "Ya completado"
                            ),
                            
                            # BotÃ³n de eliminaciÃ³n
                            html.Button(
                                html.I(className="bi bi-trash"),
                                id={"type": "delete-goal", "goal-id": goal_id},
                                n_clicks=0,
                                style={
                                    'backgroundColor': 'transparent',
                                    'border': '1px solid #ff6b6b',
                                    'color': '#ff6b6b',
                                    'padding': '6px 12px',
                                    'borderRadius': '6px',
                                    'cursor': 'pointer',
                                    'transition': 'all 0.3s ease',
                                    'display': 'inline-block'
                                },
                                title="Eliminar objetivo"
                            )
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'marginBottom': '15px'}),
                    
                    # DescripciÃ³n (si existe)
                    html.Div(
                        goal.get("description", ""),
                        style={
                            'color': '#aaa',
                            'fontSize': '0.9rem',
                            'marginBottom': '10px',
                            'display': 'block' if goal.get("description") else 'none'
                        }
                    ),
                    
                    # Segunda fila: Barra de progreso
                    html.Div([
                        html.Div(
                            style={
                                'width': '100%',
                                'height': '8px',
                                'backgroundColor': '#2b2b2b',
                                'borderRadius': '4px',
                                'overflow': 'hidden'
                            },
                            children=html.Div(
                                style={
                                    'width': f"{progress}%",
                                    'height': '100%',
                                    'backgroundColor': progress_color,
                                    'borderRadius': '4px',
                                    'transition': 'width 0.5s ease'
                                }
                            )
                        ),
                    ]),
                    
                    # Tercera fila: InformaciÃ³n de progreso y fecha
                    html.Div([
                        html.Div([
                            html.Span(
                                f"Progreso: {progress}%",
                                style={'color': progress_color, 'fontSize': '0.9rem'}
                            ),
                            html.Span(
                                " âœ… Completado" if is_completed else "",
                                style={'color': '#4ecdc4', 'fontSize': '0.8rem', 'marginLeft': '10px', 'fontWeight': '600'}
                            )
                        ], style={'flex': '1'}),
                        
                        html.Div([
                            html.Span(
                                f"Creado: {goal.get('created_at', '').split()[0] if goal.get('created_at') else ''}",
                                style={'color': '#666', 'fontSize': '0.8rem'}
                            ),
                            html.Span(
                                f" | Completado: {goal.get('completed_at', '').split()[0] if goal.get('completed_at') else ''}",
                                style={'color': '#4ecdc4', 'fontSize': '0.8rem', 
                                       'display': 'inline' if is_completed else 'none'}
                            )
                        ], style={'textAlign': 'right'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginTop': '8px'})
                ])
            ],
            style=card_style,
            id=f"goal-item-{goal_id}"
        )
        health_items.append(item)
    
    if not health_items:
        health_items = [html.Li(
            "No hay objetivos de salud activos. Â¡Agrega uno!",
            style={'color': '#ccc', 'fontStyle': 'italic', 'padding': '15px'}
        )]
    
    # Calcular progreso total y contar objetivos activos
    fitness_goals = goals_data.get("fitness", [])
    health_goals = goals_data.get("health", [])
    all_goals = fitness_goals + health_goals
    
    # Contar objetivos activos (no completados)
    active_goals = 0
    total_progress_sum = 0
    total_goals_count = 0
    
    for goal in all_goals:
        if goal.get("status") != "completed":
            active_goals += 1
        total_progress_sum += goal.get("progress", 0)
        total_goals_count += 1
    
    if total_goals_count > 0:
        total_progress = total_progress_sum / total_goals_count
    else:
        total_progress = 0
    
    print(f"âœ… Objetivos actualizados: {active_goals} activos, {total_progress:.1f}%")
    
    return (
        fitness_items,                # Lista de objetivos de fitness
        health_items,                 # Lista de objetivos de salud
        f"{int(total_progress)}%",    # Progreso total
        str(active_goals)             # Conteo de objetivos activos
    )

# ==========================================================
# CALLBACK PARA EL GRÃFICO DE MACRONUTRIENTES (MODIFICADO)
# ==========================================================

@app.callback(
    Output("macronutrientes-chart", "figure"),
    [Input("nutrition-totals-store", "data"),
     Input("url", "pathname"),
     Input("current-user", "data")],  # NUEVO: Agregar usuario
    prevent_initial_call=False
)
def update_macronutrients_chart(totals, pathname, current_user):
    """Actualiza el grÃ¡fico de pastel de macronutrientes - VERSIÃ“N CORREGIDA"""
    
    print(f"ðŸ” MACRO CHART - pathname: {pathname}, user: {current_user}")
    
    if pathname != '/nutricion' and pathname is not None:
        # Devolver figura vacÃ­a si no estamos en nutriciÃ³n
        empty_fig = {
            'data': [],
            'layout': {
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': '#ccc'},
                'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'margin': {'t': 10, 'b': 10, 'l': 10, 'r': 10},
                'annotations': [{
                    'text': 'Cargando...',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle',
                    'showarrow': False, 'font': {'size': 14, 'color': '#ccc'}
                }]
            }
        }
        return empty_fig
    
    # Si no hay totales pero hay usuario, cargar comidas
    if not totals and current_user:
        print("ðŸ“Š Cargando comidas para calcular macronutrientes")
        meals = load_user_meals(current_user)
        if meals:
            totals = calculate_daily_totals(meals)
    
    # Si aÃºn no hay totales, usar valores por defecto
    if not totals:
        print("âš ï¸ Sin datos, usando valores por defecto para grÃ¡fico")
        totals = {
            'carbs': 180,
            'protein': 95,
            'fat': 65
        }
    
    print(f"ðŸ“ˆ Datos para grÃ¡fico: {totals}")
    
    # Calcular porcentajes
    total = totals.get('carbs', 0) + totals.get('protein', 0) + totals.get('fat', 0)
    if total > 0:
        carbs_pct = (totals.get('carbs', 0) / total) * 100
        protein_pct = (totals.get('protein', 0) / total) * 100
        fat_pct = (totals.get('fat', 0) / total) * 100
    else:
        carbs_pct = 53
        protein_pct = 28
        fat_pct = 19
    
    fig = {
        'data': [{
            'values': [carbs_pct, protein_pct, fat_pct],
            'labels': ['Carbohidratos', 'ProteÃ­nas', 'Grasas'],
            'type': 'pie',
            'hole': 0.4,
            'marker': {
                'colors': ['#4ecdc4', '#ffd166', '#ff6b6b']
            },
            'hoverinfo': 'label+percent+value',
            'textinfo': 'none',
            'hovertemplate': '<b>%{label}</b><br>%{value:.1f}g<br>%{percent}<extra></extra>',
            'textposition': 'inside'
        }],
        'layout': {
            'paper_bgcolor': '#1a1a1a',
            'plot_bgcolor': '#1a1a1a',
            'font': {'color': '#ccc', 'family': "'Inter', sans-serif"},
            'showlegend': True,
            'legend': {
                'x': 1.05,
                'y': 0.5,
                'bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': '#ccc', 'size': 12}
            },
            'margin': {'t': 30, 'b': 30, 'l': 30, 'r': 100},
            'height': 300,
            'annotations': [{
                'text': 'DistribuciÃ³n<br>Macronutrientes',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'xanchor': 'center',
                'yanchor': 'middle',
                'showarrow': False,
                'font': {'size': 14, 'color': '#ccc'}
            }]
        }
    }
    
    print(f"âœ… GrÃ¡fico generado: C{carbs_pct:.1f}% P{protein_pct:.1f}% G{fat_pct:.1f}%")
    
    return fig

@app.callback(
    [Output("user-profile-name", "children"),
     Output("user-profile-avatar", "children"),
     Output("sidebar-user-fullname", "children"),
     Output("sidebar-user-avatar", "children"),
     Output("sidebar-user-level", "children"),
     Output("health-status-dots", "children"),
     Output("health-status-description", "children"),
     Output("health-summary-text", "children")],
    [Input("url", "pathname"),],
    [State("current-user", "data"),
     State("user-type-store", "data")],
    prevent_initial_call=False
)
def update_patient_view(pathname, current_user, user_type):
    """Actualiza la vista para mostrar datos del paciente cuando es accedido por un mÃ©dico"""
    
    # Verificar si estamos en /inicio con parÃ¡metro de paciente
    if '/inicio?patient=' in pathname:
        patient_username = pathname.split('?patient=')[1].split('&')[0]  # Manejar parÃ¡metros adicionales
        
        # Verificar que el usuario sea mÃ©dico y tenga acceso al paciente
        if user_type == "doctor" and current_user in DOCTORS_DB:
            if patient_username in DOCTORS_DB[current_user].get("patients", []):
                
                # Obtener datos del paciente
                if patient_username in USERS_DB:
                    patient_data = USERS_DB[patient_username]
                    full_name = patient_data.get("full_name", patient_username)
                    activity_level = patient_data.get("activity_level", 5)
                    
                    # Calcular estado de salud del paciente
                    health_score = get_health_score_from_activity_level(activity_level)
                    health_description = get_health_description(health_score)
                    
                    # Avatar
                    avatar_initial = full_name[0].upper() if full_name else patient_username[0].upper()
                    
                    # Nivel
                    level_text = f"Paciente â€¢ Nivel {activity_level}/10"
                    
                    # Generar cÃ­rculos de estado de salud
                    health_dots = []
                    for i in range(5):
                        if i < health_score:
                            dot_style = {
                                'width': '12px',
                                'height': '12px',
                                'backgroundColor': HIGHLIGHT_COLOR,
                                'borderRadius': '50%',
                                'boxShadow': f'0 0 8px {HIGHLIGHT_COLOR}'
                            }
                        else:
                            dot_style = {
                                'width': '12px',
                                'height': '12px',
                                'backgroundColor': '#444',
                                'borderRadius': '50%',
                                'border': '1px solid #666'
                            }
                        health_dots.append(html.Div(style=dot_style))
                    
                    # Texto de estado de salud
                    health_status_text = html.Div([
                        html.Div(f"Estado de Salud: {health_score}/5", 
                                style={'color': HIGHLIGHT_COLOR, 'fontWeight': '600', 'fontSize': '0.9rem', 'marginBottom': '5px'}),
                        html.Div(health_description, 
                                style={'color': '#cccccc', 'fontSize': '0.8rem', 'lineHeight': '1.4'})
                    ], style={'textAlign': 'center'})
                    
                    # Texto de resumen mÃ©dico
                    doctor_data = DOCTORS_DB[current_user]
                    doctor_name = doctor_data.get("full_name", current_user)
                    summary_text = f"ðŸ‘¨â€âš•ï¸ {doctor_name} viendo datos de {full_name} â€¢ Paciente desde: {datetime.now().strftime('%d/%m/%Y')}"
                    
                    print(f"ðŸ‘¤ Mostrando datos del paciente {full_name} para mÃ©dico {doctor_name}")
                    
                    return (
                        f"ðŸ‘¨â€âš•ï¸ {full_name}",
                        avatar_initial,
                        full_name,
                        avatar_initial,
                        level_text,
                        health_dots,
                        health_status_text,
                        summary_text
                    )
    
    # Si no es un paciente, mostrar datos normales del usuario
    if current_user:
        if user_type == "doctor" and current_user in DOCTORS_DB:
            doctor_data = DOCTORS_DB[current_user]
            full_name = doctor_data.get("full_name", current_user)
            avatar_initial = "D"
            level_text = "MÃ©dico"
            health_score = 5  # MÃ¡ximo para mÃ©dicos
            
            # Puntos de salud para mÃ©dico
            health_dots = []
            for i in range(5):
                dot_style = {
                    'width': '12px',
                    'height': '12px',
                    'backgroundColor': '#4ecdc4',
                    'borderRadius': '50%',
                    'boxShadow': '0 0 8px #4ecdc4'
                }
                health_dots.append(html.Div(style=dot_style))
            
            health_status_text = html.Div([
                html.Div("ðŸ‘¨â€âš•ï¸ MÃ©dico Especialista", 
                        style={'color': '#4ecdc4', 'fontWeight': '600', 'fontSize': '0.9rem', 'marginBottom': '5px'}),
                html.Div("Acceso completo a datos de pacientes", 
                        style={'color': '#cccccc', 'fontSize': '0.8rem', 'lineHeight': '1.4'})
            ], style={'textAlign': 'center'})
            
            summary_text = f"Panel de Control MÃ©dico â€¢ {len(doctor_data.get('patients', []))} pacientes activos"
            
        elif current_user in USERS_DB:
            user_data = USERS_DB[current_user]
            full_name = user_data.get("full_name", current_user)
            activity_level = user_data.get("activity_level", 5)
            health_score = get_health_score_from_activity_level(activity_level)
            health_description = get_health_description(health_score)
            
            avatar_initial = full_name[0].upper() if full_name else current_user[0].upper()
            level_text = f"Atleta â€¢ Nivel {activity_level}/10"
            
            # Puntos de salud
            health_dots = []
            for i in range(5):
                if i < health_score:
                    dot_style = {
                        'width': '12px',
                        'height': '12px',
                        'backgroundColor': HIGHLIGHT_COLOR,
                        'borderRadius': '50%',
                        'boxShadow': f'0 0 8px {HIGHLIGHT_COLOR}'
                    }
                else:
                    dot_style = {
                        'width': '12px',
                        'height': '12px',
                        'backgroundColor': '#444',
                        'borderRadius': '50%',
                        'border': '1px solid #666'
                    }
                health_dots.append(html.Div(style=dot_style))
            
            health_status_text = html.Div([
                html.Div(f"Estado de Salud: {health_score}/5", 
                        style={'color': HIGHLIGHT_COLOR, 'fontWeight': '600', 'fontSize': '0.9rem', 'marginBottom': '5px'}),
                html.Div(health_description, 
                        style={'color': '#cccccc', 'fontSize': '0.8rem', 'lineHeight': '1.4'})
            ], style={'textAlign': 'center'})
            
            summary_text = f"Bienvenido/a, {full_name} â€¢ Tu salud estÃ¡ en buenas manos"
        
        else:
            full_name = current_user
            avatar_initial = current_user[0].upper()
            level_text = "Usuario"
            health_dots = []
            health_status_text = html.Div()
            summary_text = "Usuario no identificado"
        
        return (
            full_name,
            avatar_initial,
            full_name,
            avatar_initial,
            level_text,
            health_dots,
            health_status_text,
            summary_text
        )
    
    # Por defecto
    return "Usuario", "U", "Usuario", "U", "Visitante", [], html.Div(), "Bienvenido/a a Athletica"

# ==========================================================
# CALLBACKS DE NAVEGACIÃ“N (TODOS LOS COMPLETOS)
# ==========================================================

# Callback para navegaciÃ³n desde INICIO
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input("nav-inicio-inicio", "n_clicks"),
     Input("nav-metricas-inicio", "n_clicks"),
     Input("nav-objetivos-inicio", "n_clicks"),
     Input("nav-nutricion-inicio", "n_clicks"),
     Input("nav-entrenamientos-inicio", "n_clicks"),
     ],
    prevent_initial_call=True
)
def handle_navigation_inicio(inicio_clicks, metricas_clicks, objetivos_clicks, 
                            nutricion_clicks, entrenamientos_clicks, 
                            ):
    """Maneja navegaciÃ³n desde la pÃ¡gina de inicio"""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Mapeo de IDs a rutas
    route_map = {
        'nav-inicio-inicio': '/inicio',
        'nav-metricas-inicio': '/metricas',
        'nav-objetivos-inicio': '/objetivos',
        'nav-nutricion-inicio': '/nutricion',
        'nav-entrenamientos-inicio': '/entrenamientos',
    }
    
    new_route = route_map.get(button_id, '/inicio')
    print(f"ðŸ” NavegaciÃ³n desde INICIO - botÃ³n: {button_id} -> Ruta: {new_route}")
    return new_route

# Callback para navegaciÃ³n desde MÃ‰TRICAS
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input("nav-inicio-metricas", "n_clicks"),
     Input("nav-metricas-metricas", "n_clicks"),
     Input("nav-objetivos-metricas", "n_clicks"),
     Input("nav-nutricion-metricas", "n_clicks"),
     Input("nav-entrenamientos-metricas", "n_clicks"),
     ],
    prevent_initial_call=True
)
def handle_navigation_metricas(inicio_clicks, metricas_clicks, objetivos_clicks, 
                              nutricion_clicks, entrenamientos_clicks, 
                              ):
    
    """Maneja navegaciÃ³n desde la pÃ¡gina de mÃ©tricas"""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Mapeo de IDs a rutas
    route_map = {
        'nav-inicio-metricas': '/inicio',
        'nav-metricas-metricas': '/metricas',
        'nav-objetivos-metricas': '/objetivos',
        'nav-nutricion-metricas': '/nutricion',
        'nav-entrenamientos-metricas': '/entrenamientos',
    }
    
    new_route = route_map.get(button_id, '/inicio')
    print(f"ðŸ” NavegaciÃ³n desde MÃ‰TRICAS - botÃ³n: {button_id} -> Ruta: {new_route}")
    return new_route

# Callback para navegaciÃ³n desde OBJETIVOS
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input("nav-inicio-objetivos", "n_clicks"),
     Input("nav-metricas-objetivos", "n_clicks"),
     Input("nav-objetivos-objetivos", "n_clicks"),
     Input("nav-nutricion-objetivos", "n_clicks"),
     Input("nav-entrenamientos-objetivos", "n_clicks"),
    ],
    prevent_initial_call=True
)
def handle_navigation_objetivos(inicio_clicks, metricas_clicks, objetivos_clicks, 
                               nutricion_clicks,entrenamientos_clicks, 
                               ):
    
    """Maneja navegaciÃ³n desde la pÃ¡gina de objetivos"""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Mapeo de IDs a rutas
    route_map = {
        'nav-inicio-objetivos': '/inicio',
        'nav-metricas-objetivos': '/metricas',
        'nav-objetivos-objetivos': '/objetivos',
        'nav-nutricion-objetivos': '/nutricion',
        'nav-entrenamientos-objetivos': '/entrenamientos',
    }
    
    new_route = route_map.get(button_id, '/inicio')
    print(f"ðŸ” NavegaciÃ³n desde OBJETIVOS - botÃ³n: {button_id} -> Ruta: {new_route}")
    return new_route

# Callback para navegaciÃ³n desde NUTRICIÃ“N
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input("nav-inicio-nutricion", "n_clicks"),
     Input("nav-metricas-nutricion", "n_clicks"),
     Input("nav-objetivos-nutricion", "n_clicks"),
     Input("nav-nutricion-nutricion", "n_clicks"),
     Input("nav-entrenamientos-nutricion", "n_clicks"),
     ],
    prevent_initial_call=True
)
def handle_navigation_nutricion(inicio_clicks, metricas_clicks, objetivos_clicks, 
                               nutricion_clicks, entrenamientos_clicks, 
                               ):
    
    """Maneja navegaciÃ³n desde la pÃ¡gina de nutriciÃ³n"""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Mapeo de IDs a rutas
    route_map = {
        'nav-inicio-nutricion': '/inicio',
        'nav-metricas-nutricion': '/metricas',
        'nav-objetivos-nutricion': '/objetivos',
        'nav-nutricion-nutricion': '/nutricion',
        'nav-entrenamientos-nutricion': '/entrenamientos',
    }
    
    new_route = route_map.get(button_id, '/inicio')
    print(f"ðŸ” NavegaciÃ³n desde NUTRICIÃ“N - botÃ³n: {button_id} -> Ruta: {new_route}")
    return new_route

# ==========================================================
# CALLBACKS DE NAVEGACIÃ“N PARA ENTRENAMIENTOS (NUEVO)
# ==========================================================

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input("nav-inicio-entrenamientos", "n_clicks"),
     Input("nav-metricas-entrenamientos", "n_clicks"),
     Input("nav-objetivos-entrenamientos", "n_clicks"),
     Input("nav-nutricion-entrenamientos", "n_clicks"),
     Input("nav-entrenamientos-entrenamientos", "n_clicks"),
     ],
    prevent_initial_call=True
)
def handle_navigation_entrenamientos(inicio_clicks, metricas_clicks, objetivos_clicks, 
                                    nutricion_clicks, entrenamientos_clicks, 
                                    ):
    
    """Maneja navegaciÃ³n desde la pÃ¡gina de entrenamientos"""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Mapeo de IDs a rutas
    route_map = {
        'nav-inicio-entrenamientos': '/inicio',
        'nav-metricas-entrenamientos': '/metricas',
        'nav-objetivos-entrenamientos': '/objetivos',
        'nav-nutricion-entrenamientos': '/nutricion',
        'nav-entrenamientos-entrenamientos': '/entrenamientos',
    }
    
    new_route = route_map.get(button_id, '/inicio')
    print(f"ðŸ” NavegaciÃ³n desde ENTRENAMIENTOS - botÃ³n: {button_id} -> Ruta: {new_route}")
    return new_route

# ==========================================================
# CALLBACK PARA NAVEGACIÃ“N DESDE DASHBOARD MÃ‰DICO (NUEVO)
# ==========================================================

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input("nav-dashboard-doctor", "n_clicks"),
     Input("nav-pacientes-doctor", "n_clicks"),
     Input("nav-metricas-doctor", "n_clicks"),
     Input("nav-config-doctor", "n_clicks")],
    prevent_initial_call=True
)
def handle_navigation_doctor(dashboard_clicks, pacientes_clicks, metricas_clicks, config_clicks):
    """Maneja navegaciÃ³n desde el dashboard mÃ©dico"""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Mapeo de IDs a rutas para mÃ©dicos
    route_map = {
        'nav-dashboard-doctor': '/doctor-dashboard',  # Dashboard principal
        'nav-pacientes-doctor': '/doctor-dashboard',  # Mismo dashboard, pero podrÃ­a ser diferente
        'nav-metricas-doctor': '/metricas',           # PodrÃ­as crear una versiÃ³n mÃ©dica de mÃ©tricas
        'nav-config-doctor': '/configuracion',        # NecesitarÃ­as crear esta pÃ¡gina
    }
    
    new_route = route_map.get(button_id, '/doctor-dashboard')
    print(f"ðŸ” NavegaciÃ³n desde DOCTOR - botÃ³n: {button_id} -> Ruta: {new_route}")
    return new_route

# ==========================================================
# CALLBACKS PARA ESTILOS DE NAVEGACIÃ“N (TODOS LOS COMPLETOS)
# ==========================================================

@app.callback(
    [Output("nav-inicio-entrenamientos", "style"),
     Output("nav-metricas-entrenamientos", "style"),
     Output("nav-objetivos-entrenamientos", "style"),
     Output("nav-nutricion-entrenamientos", "style"),
     Output("nav-entrenamientos-entrenamientos", "style"),
     ],
    [Input("url", "pathname")],
    prevent_initial_call=True
)
def update_entrenamientos_nav_styles(pathname):
    """Actualiza estilos de navegaciÃ³n en la pÃ¡gina de entrenamientos"""
    if pathname not in ['/inicio', '/metricas', '/objetivos', '/nutricion', '/entrenamientos']:
        raise dash.exceptions.PreventUpdate
    
    # Estilo base para botones inactivos
    base_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'transparent',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': '1px solid transparent',
        'color': '#ccc',
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Estilo para botÃ³n activo
    active_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': f'1px solid {HIGHLIGHT_COLOR}',
        'color': HIGHLIGHT_COLOR,
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Inicializar todos con estilo base 
    styles = [base_style] * 5
    
    # Actualizar segÃºn la ruta activa
    if pathname == '/inicio':
        styles[0] = active_style  # Inicio
    elif pathname == '/metricas':
        styles[1] = active_style  # MÃ©tricas
    elif pathname == '/objetivos':
        styles[2] = active_style  # Objetivos
    elif pathname == '/nutricion':
        styles[3] = active_style  # NutriciÃ³n
    elif pathname == '/entrenamientos':
        styles[4] = active_style  # Entrenamientos
    
    return styles

# ==========================================================
# CALLBACK PARA ESTILOS DE NAVEGACIÃ“N MÃ‰DICA (NUEVO)
# ==========================================================

@app.callback(
    [Output("nav-dashboard-doctor", "style"),
     Output("nav-pacientes-doctor", "style"),
     Output("nav-metricas-doctor", "style"),
     Output("nav-config-doctor", "style")],
    [Input("url", "pathname")],
    prevent_initial_call=True
)
def update_doctor_nav_styles(pathname):
    """Actualiza estilos de navegaciÃ³n en el dashboard mÃ©dico"""
    
    # Estilo base para botones inactivos
    base_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'transparent',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': '1px solid transparent',
        'color': '#ccc',
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Estilo para botÃ³n activo (color mÃ©dico)
    active_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'rgba(78, 205, 196, 0.1)',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': f'1px solid #4ecdc4',
        'color': '#4ecdc4',
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Inicializar todos con estilo base
    styles = [base_style] * 4
    
    # Actualizar segÃºn la ruta activa
    if pathname == '/doctor-dashboard':
        styles[0] = active_style  # Dashboard activo
    # AquÃ­ puedes agregar lÃ³gica para otras rutas mÃ©dicas cuando las crees
    
    return styles

# ==========================================================
# FUNCIONES AUXILIARES PARA PUNTOS DE SALUD
# ==========================================================

def get_health_score_from_activity_level(activity_level):
    """Convierte nivel de actividad (1-10) a puntuaciÃ³n de salud (1-5)"""
    if activity_level <= 2:
        return 1
    elif activity_level <= 4:
        return 2
    elif activity_level <= 6:
        return 3
    elif activity_level <= 8:
        return 4
    else:
        return 5

def get_health_description(health_score):
    """Devuelve descripciÃ³n segÃºn puntuaciÃ³n de salud"""
    descriptions = {
        1: "Actividad baja â€¢ Se recomienda aumentar ejercicio gradualmente",
        2: "Actividad media-baja â€¢ Buen comienzo, sigue progresando",
        3: "Actividad intermedia â€¢ Manteniendo buen ritmo de ejercicio",
        4: "Actividad alta â€¢ Excelente condiciÃ³n fÃ­sica",
        5: "Actividad muy alta â€¢ Nivel atlÃ©tico excepcional"
    }
    return descriptions.get(health_score, "Estado normal â€¢ Manteniendo ritmo")

# ==========================================================
# CALLBACK PARA ACTUALIZAR NIVEL DE ACTIVIDAD DURANTE ONBOARDING
# ==========================================================

@app.callback(
    Output("user-activity-level", "data", allow_duplicate=True),
    [Input("input-activity-level", "value")],
    [State("current-user", "data"),
     State("url", "pathname")],

    prevent_initial_call=True  # Solo cuando se cambia el slider
)
def update_activity_level_during_onboarding(activity_level, current_user, current_path):
    """Actualiza store de nivel de actividad - SOLO en onboarding"""
    
    # Verificar EXPLÃCITAMENTE que estamos en onboarding
    if current_path != '/onboarding':
        print(f"âš ï¸ Intento de update fuera de onboarding: {current_path}")
        raise dash.exceptions.PreventUpdate
    
    # Si activity_level es None (input no renderizado aÃºn)
    if activity_level is None:
        raise dash.exceptions.PreventUpdate
    
    print(f"âœ… Actualizando actividad en onboarding: {activity_level}")
    
    if current_user:
        # Guardar en la base de datos
        update_user_activity_level(current_user, activity_level)
    
    return activity_level

# ==========================================================
# CALLBACK UNIFICADO PARA PERFILES DE USUARIO (CORREGIDO)
# ==========================================================

# Modificar la funciÃ³n create_profile_callback para manejar mÃ©dicos:

def create_profile_callback(output_ids, page_name):
    """Crea un callback dinÃ¡mico para actualizar perfiles de usuario"""
    
    @app.callback(
        [Output(f"{page_name}-sidebar-user-avatar", "children"),
         Output(f"{page_name}-sidebar-user-fullname", "children"),
         Output(f"{page_name}-sidebar-user-level", "children"),
         Output(f"{page_name}-health-status-dots", "children"),
         Output(f"{page_name}-health-status-description", "children"),
         Output(f"{page_name}-user-profile-avatar", "children"),
         Output(f"{page_name}-user-profile-name", "children")],
        [Input("current-user", "data"),
         Input("user-activity-level", "data"),
         Input("user-type-store", "data")],  # NUEVO INPUT
        prevent_initial_call=False
    )
    def update_page_profile(current_user, activity_level, user_type):
        """Actualiza perfil en la pÃ¡gina especÃ­fica"""
        print(f"ðŸ” UPDATE {page_name.upper()} PROFILE - user: {current_user}, type: {user_type}, activity: {activity_level}")
        
        if current_user is None:
            # Usuario no logueado
            return "U", "Usuario", "Visitante", [], "Sin datos", "U", "Usuario"
        
        # Si es mÃ©dico, mostrar informaciÃ³n diferente
        if user_type == "doctor" and current_user in DOCTORS_DB:
            doctor_data = DOCTORS_DB[current_user]
            
            # Avatar del mÃ©dico (usar D en lugar de inicial para diferenciar)
            avatar_initial = "D"
            
            full_name = doctor_data.get("full_name", current_user)
            patient_count = len(doctor_data.get("patients", []))
            level_text = f"MÃ©dico â€¢ {patient_count} paciente{'s' if patient_count != 1 else ''}"
            
            # Para mÃ©dicos, mostrar puntos de actividad diferente
            health_dots = []
            for i in range(5):
                # Todos los puntos activos para mÃ©dicos
                dot_style = {
                    'width': '12px',
                    'height': '12px',
                    'backgroundColor': '#4ecdc4',  # Color diferente para mÃ©dicos
                    'borderRadius': '50%',
                    'boxShadow': '0 0 8px #4ecdc4'
                }
                health_dots.append(html.Div(style=dot_style))
            
            health_status_text = html.Div([
                html.Div("ðŸ‘¨â€âš•ï¸ MÃ©dico Especialista", 
                        style={'color': '#4ecdc4', 'fontWeight': '600', 'fontSize': '0.9rem', 'marginBottom': '5px'}),
                html.Div("Acceso completo a datos de pacientes", 
                        style={'color': '#cccccc', 'fontSize': '0.8rem', 'lineHeight': '1.4'})
            ], style={'textAlign': 'center'})
            
            print(f"âœ… Perfil mÃ©dico actualizado: {full_name}")
            
            return (
                avatar_initial,
                full_name,
                level_text,
                health_dots,
                health_status_text,
                avatar_initial,
                full_name
            )
        
        # Si es atleta, usar la lÃ³gica original
        # Si activity_level es None, obtener del usuario o usar valor por defecto
        if activity_level is None:
            print(f"âš ï¸ activity_level es None para {current_user}, obteniendo de la base de datos")
            if current_user in USERS_DB:
                activity_level = USERS_DB[current_user].get("activity_level", 5)
            else:
                activity_level = 5
        
        # Obtener informaciÃ³n del usuario
        user_info = {}
        if current_user in USERS_DB:
            user_info = {
                "full_name": USERS_DB[current_user].get("full_name", current_user),
                "level": "Atleta Intermedio" if activity_level >= 7 else "Atleta Principiante" if activity_level <= 4 else "Atleta"
            }
        else:
            user_info = {
                "full_name": current_user,
                "level": "Atleta"
            }
        
        # Obtener inicial del avatar
        avatar_initial = user_info["full_name"][0].upper() if user_info["full_name"] else current_user[0].upper()
        
        # Calcular estado de salud basado en nivel de actividad
        health_score = get_health_score_from_activity_level(activity_level)
        health_description = get_health_description(health_score)
        
        # Generar cÃ­rculos de estado de salud (5 cÃ­rculos totales)
        health_dots = []
        for i in range(5):
            if i < health_score:
                # CÃ­rculo lleno (activo)
                dot_style = {
                    'width': '12px',
                    'height': '12px',
                    'backgroundColor': HIGHLIGHT_COLOR,
                    'borderRadius': '50%',
                    'boxShadow': f'0 0 8px {HIGHLIGHT_COLOR}'
                }
            else:
                # CÃ­rculo vacÃ­o (inactivo)
                dot_style = {
                    'width': '12px',
                    'height': '12px',
                    'backgroundColor': '#444',
                    'borderRadius': '50%',
                    'border': '1px solid #666'
                }
            health_dots.append(html.Div(style=dot_style))
        
        # Crear texto del estado de salud
        health_status_text = html.Div([
            html.Div(f"Estado de Salud: {health_score}/5", 
                    style={'color': HIGHLIGHT_COLOR, 'fontWeight': '600', 'fontSize': '0.9rem', 'marginBottom': '5px'}),
            html.Div(health_description, 
                    style={'color': '#cccccc', 'fontSize': '0.8rem', 'lineHeight': '1.4'})
        ], style={'textAlign': 'center'})
        
        print(f"âœ… Perfil atleta actualizado: {user_info['full_name']}, actividad: {activity_level}, salud: {health_score}/5")
        
        return (
            avatar_initial,
            user_info["full_name"],
            user_info["level"],
            health_dots,
            health_status_text,
            avatar_initial,
            user_info["full_name"]
        )
    
    return update_page_profile

# REGISTRAR TODOS LOS CALLBACKS DE PERFIL

update_entrenamientos_profiles = create_profile_callback([
    "entrenamientos-sidebar-user-avatar",
    "entrenamientos-sidebar-user-fullname",
    "entrenamientos-sidebar-user-level",
    "entrenamientos-health-status-dots",
    "entrenamientos-health-status-description",
    "entrenamientos-user-profile-avatar",
    "entrenamientos-user-profile-name"
], "entrenamientos")

update_inicio_profiles = create_profile_callback([
    "sidebar-user-avatar",
    "sidebar-user-fullname",
    "sidebar-user-level",
    "health-status-dots",
    "health-status-description",
    "user-profile-avatar",
    "user-profile-name"
], "")

update_metricas_profiles = create_profile_callback([
    "metricas-sidebar-user-avatar",
    "metricas-sidebar-user-fullname",
    "metricas-sidebar-user-level",
    "metricas-health-status-dots",
    "metricas-health-status-description",
    "metricas-user-profile-avatar",
    "metricas-user-profile-name"
], "metricas")

update_objetivos_profiles = create_profile_callback([
    "objetivos-sidebar-user-avatar",
    "objetivos-sidebar-user-fullname",
    "objetivos-sidebar-user-level",
    "objetivos-health-status-dots",
    "objetivos-health-status-description",
    "objetivos-user-profile-avatar",
    "objetivos-user-profile-name"
], "objetivos")

update_nutricion_profiles = create_profile_callback([
    "nutricion-sidebar-user-avatar",
    "nutricion-sidebar-user-fullname",
    "nutricion-sidebar-user-level",
    "nutricion-health-status-dots",
    "nutricion-health-status-description",
    "nutricion-user-profile-avatar",
    "nutricion-user-profile-name"
], "nutricion")

# ==========================================================
# CALLBACKS PARA ESTILOS DE NAVEGACIÃ“N (CONTINUACIÃ“N)
# ==========================================================

@app.callback(
    [Output("nav-inicio-inicio", "style"),
     Output("nav-metricas-inicio", "style"),
     Output("nav-objetivos-inicio", "style"),
     Output("nav-nutricion-inicio", "style"),
     Output("nav-entrenamientos-inicio", "style"),],
    [Input("url", "pathname")],
    prevent_initial_call=True
)
def update_inicio_nav_styles(pathname):
    if pathname not in ['/inicio', '/metricas', '/objetivos', '/nutricion', '/entrenamientos']:
        raise dash.exceptions.PreventUpdate
    
    # Estilo base para botones inactivos
    base_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'transparent',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': '1px solid transparent',
        'color': '#ccc',
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Estilo para botÃ³n activo
    active_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': f'1px solid {HIGHLIGHT_COLOR}',
        'color': HIGHLIGHT_COLOR,
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Inicializar todos con estilo base (SOLO 6 ELEMENTOS)
    styles = [base_style] * 5  
    
    # Actualizar segÃºn la ruta activa
    if pathname == '/inicio':
        styles[0] = active_style  # Inicio
    elif pathname == '/metricas':
        styles[1] = active_style  # MÃ©tricas
    elif pathname == '/objetivos':
        styles[2] = active_style  # Objetivos
    elif pathname == '/nutricion':
        styles[3] = active_style  # NutriciÃ³n
    elif pathname == '/entrenamientos':
        styles[4] = active_style  # Entrenamientos
    
    return styles

@app.callback(
    [Output("nav-inicio-metricas", "style"),
     Output("nav-metricas-metricas", "style"),
     Output("nav-objetivos-metricas", "style"),
     Output("nav-nutricion-metricas", "style"),
     Output("nav-entrenamientos-metricas", "style"),],
    [Input("url", "pathname")],
    prevent_initial_call=True
)
def update_metricas_nav_styles(pathname):
    """Actualiza estilos de navegaciÃ³n en la pÃ¡gina de mÃ©tricas"""
    if pathname not in ['/inicio', '/metricas', '/objetivos', '/nutricion', '/entrenamientos']:
        raise dash.exceptions.PreventUpdate
    
    # Estilo base para botones inactivos
    base_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'transparent',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': '1px solid transparent',
        'color': '#ccc',
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Estilo para botÃ³n activo
    active_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': f'1px solid {HIGHLIGHT_COLOR}',
        'color': HIGHLIGHT_COLOR,
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Inicializar todos con estilo base
    styles = [base_style] * 5
    
    # Actualizar segÃºn la ruta activa
    if pathname == '/inicio':
        styles[0] = active_style  # Inicio
    elif pathname == '/metricas':
        styles[1] = active_style  # MÃ©tricas
    elif pathname == '/objetivos':
        styles[2] = active_style  # Objetivos
    elif pathname == '/nutricion':
        styles[3] = active_style  # NutriciÃ³n
    elif pathname == '/entrenamientos':
        styles[4] = active_style  # Entrenamientos
    
    return styles

@app.callback(
    [Output("nav-inicio-objetivos", "style"),
     Output("nav-metricas-objetivos", "style"),
     Output("nav-objetivos-objetivos", "style"),
     Output("nav-nutricion-objetivos", "style"),
     Output("nav-entrenamientos-objetivos", "style"),],
    [Input("url", "pathname")],
    prevent_initial_call=True
)
def update_objetivos_nav_styles(pathname):
    """Actualiza estilos de navegaciÃ³n en la pÃ¡gina de objetivos"""
    if pathname not in ['/inicio', '/metricas', '/objetivos', '/nutricion', '/entrenamientos']:
        raise dash.exceptions.PreventUpdate
    
    # Estilo base para botones inactivos
    base_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'transparent',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': '1px solid transparent',
        'color': '#ccc',
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Estilo para botÃ³n activo
    active_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': f'1px solid {HIGHLIGHT_COLOR}',
        'color': HIGHLIGHT_COLOR,
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Inicializar todos con estilo base
    styles = [base_style] * 5
    
    # Actualizar segÃºn la ruta activa
    if pathname == '/inicio':
        styles[0] = active_style  # Inicio
    elif pathname == '/metricas':
        styles[1] = active_style  # MÃ©tricas
    elif pathname == '/objetivos':
        styles[2] = active_style  # Objetivos
    elif pathname == '/nutricion':
        styles[3] = active_style  # NutriciÃ³n
    elif pathname == '/entrenamientos':
        styles[4] = active_style  # Entrenamientos
    
    return styles

@app.callback(
    [Output("nav-inicio-nutricion", "style"),
     Output("nav-metricas-nutricion", "style"),
     Output("nav-objetivos-nutricion", "style"),
     Output("nav-nutricion-nutricion", "style"),
     Output("nav-entrenamientos-nutricion", "style"),],
    [Input("url", "pathname")],
    prevent_initial_call=True
)
def update_nutricion_nav_styles(pathname):
    """Actualiza estilos de navegaciÃ³n en la pÃ¡gina de nutriciÃ³n"""
    if pathname not in ['/inicio', '/metricas', '/objetivos', '/nutricion', '/entrenamientos']:
        raise dash.exceptions.PreventUpdate
    
    # Estilo base para botones inactivos
    base_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'transparent',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': '1px solid transparent',
        'color': '#ccc',
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Estilo para botÃ³n activo
    active_style = {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 15px',
        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'border': f'1px solid {HIGHLIGHT_COLOR}',
        'color': HIGHLIGHT_COLOR,
        'textAlign': 'left',
        'fontFamily': "'Inter', sans-serif",
        'border': 'none'
    }
    
    # Inicializar todos con estilo base
    styles = [base_style] * 5
    
    # Actualizar segÃºn la ruta activa
    if pathname == '/inicio':
        styles[0] = active_style  # Inicio
    elif pathname == '/metricas':
        styles[1] = active_style  # MÃ©tricas
    elif pathname == '/objetivos':
        styles[2] = active_style  # Objetivos
    elif pathname == '/nutricion':
        styles[3] = active_style  # NutriciÃ³n
    elif pathname == '/entrenamientos':
        styles[4] = active_style  # Entrenamientos
    
    return styles

# ==========================================================
# CALLBACKS PARA ECG Y GRÃFICAS
# ==========================================================

@app.callback(
    [Output('ecg-graph', 'figure'),
     Output('current-bpm', 'children'),
     Output('bpm-status', 'children'),
     Output('max-bpm', 'children'),
     Output('min-bpm', 'children'),
     Output('avg-bpm', 'children')],
    [Input('url', 'pathname'),
     Input('current-user', 'data')],
     [State('user-type-store', 'data')],
    prevent_initial_call=False
)
def update_ecg_inicio(pathname, current_user, user_type):
    print(f"ðŸ” ECG Callback - pathname: {pathname}, user: {current_user}")

        
    # Determinar si estamos viendo un paciente
    is_viewing_patient = False
    patient_username = None
    
    if '/inicio?patient=' in pathname:
        patient_username = pathname.split('?patient=')[1].split('&')[0]
        is_viewing_patient = True
    
    # Determinar para quiÃ©n mostrar datos
    if is_viewing_patient and user_type == "doctor" and patient_username:
        # Mostrar datos del paciente
        target_user = patient_username
        print(f"ðŸ‘¨â€âš•ï¸ Mostrando ECG del paciente: {target_user}")
    else:
        # Mostrar datos del usuario actual
        target_user = current_user
        print(f"ðŸ‘¤ Mostrando ECG del usuario: {target_user}")
    
    # Solo ejecutar si estamos en inicio o mÃ©tricas
    if pathname not in ['/inicio', '/metricas']:
        print("âš ï¸ ECG Callback - No estÃ¡ en inicio o mÃ©tricas, usando figura vacÃ­a")
        empty_fig = {
            'data': [],
            'layout': {
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': '#ccc'},
                'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'margin': {'t': 10, 'b': 10, 'l': 10, 'r': 10},
                'annotations': [{
                    'text': 'Cargando datos de ECG...',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle',
                    'showarrow': False, 'font': {'size': 16, 'color': '#ccc'}
                }]
            }
        }
        return empty_fig, "Cargando...", "Cargando", "Cargando", "Cargando", "Cargando"
    
    try:
        print("ðŸ“Š Cargando datos de ECG...")
        t, ecg, bpm, peaks = load_ecg_and_compute_bpm("ecg_example.csv")
        
        if len(t) == 0 or len(ecg) == 0:
            print("âš ï¸ No hay datos de ECG disponibles")
            empty_fig = {
                'data': [],
                'layout': {
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'font': {'color': '#ccc'},
                    'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                    'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                    'margin': {'t': 10, 'b': 10, 'l': 10, 'r': 10},
                    'annotations': [{
                        'text': 'No hay datos de ECG disponibles',
                        'xref': 'paper', 'yref': 'paper',
                        'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle',
                        'showarrow': False, 'font': {'size': 16, 'color': '#ccc'}
                    }]
                }
            }
            return empty_fig, "0 bpm", "Sin datos", "0 bpm", "0 bpm", "0 bpm"
        
        print(f"âœ… Datos ECG cargados: {len(t)} puntos, BPM: {bpm}")
        
        fig = {
            'data': [
                {
                    'x': t,
                    'y': ecg,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {'color': HIGHLIGHT_COLOR, 'width': 2},
                    'name': 'SeÃ±al ECG',
                    'hovertemplate': 'Tiempo: %{x:.2f}s<br>Amplitud: %{y:.2f}<extra></extra>'
                }
            ],
            'layout': {
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': '#ccc'},
                'xaxis': {
                    'title': 'Tiempo (s)',
                    'gridcolor': '#2b2b2b',
                    'zerolinecolor': '#2b2b2b',
                    'titlefont': {'color': '#ccc'},
                    'showgrid': True,
                    'gridwidth': 1,
                    'showline': True,
                    'linecolor': '#444'
                },
                'yaxis': {
                    'title': 'Amplitud ECG',
                    'gridcolor': '#2b2b2b',
                    'zerolinecolor': '#2b2b2b',
                    'titlefont': {'color': '#ccc'},
                    'showgrid': True,
                    'gridwidth': 1,
                    'showline': True,
                    'linecolor': '#444'
                },
                'margin': {'t': 40, 'b': 50, 'l': 60, 'r': 30},
                'showlegend': False,
                'hovermode': 'closest',
                'height': 200,
                'title': {
                    'text': 'SeÃ±al ECG en Tiempo Real',
                    'font': {'color': HIGHLIGHT_COLOR, 'size': 14},
                    'x': 0.5,
                    'xanchor': 'center'
                }
            }
        }
        
        if len(peaks) > 0:
            fig['data'].append({
                'x': t[peaks],
                'y': ecg[peaks],
                'mode': 'markers',
                'marker': {
                    'color': '#ff6b6b', 
                    'size': 6, 
                    'symbol': 'circle',
                    'line': {'width': 1, 'color': 'white'}
                },
                'name': 'Picos R',
                'hovertemplate': 'Pico R<br>Tiempo: %{x:.2f}s<br>Amplitud: %{y:.2f}<extra></extra>',
                'showlegend': False
            })
        
        if bpm < 60:
            status = "Bradicardia"
        elif bpm < 100:
            status = "Normal" 
        else:
            status = "Taquicardia"
        
        if len(ecg) > 0:
            max_bpm = int(bpm * 1.18)
            min_bpm = int(bpm * 0.82)
            avg_bpm = int(bpm)
        else:
            max_bpm = min_bpm = avg_bpm = int(bpm)
        
        print(f"âœ… ECG generado exitosamente: BPM={int(bpm)}, Status={status}")
        
        return (
            fig,
            f"{int(bpm)} bpm",
            status,
            f"{max_bpm} bpm",
            f"{min_bpm} bpm", 
            f"{avg_bpm} bpm"
        )
        
    except Exception as e:
        print(f"âŒ Error en update_ecg_inicio: {e}")
        import traceback
        traceback.print_exc()
        
        # Crear datos de ejemplo de fallback
        t_example = np.linspace(0, 10, 1000)
        ecg_example = (
            0.5 * np.sin(2 * np.pi * 0.2 * t_example) +
            1.5 * np.sin(2 * np.pi * 1.0 * (t_example - 0.1)) * np.exp(-5 * (t_example - 0.1)**2) +
            0.3 * np.sin(2 * np.pi * 0.3 * (t_example - 0.3))
        )
        
        fig_fallback = {
            'data': [{
                'x': t_example,
                'y': ecg_example,
                'type': 'scatter',
                'mode': 'lines',
                'line': {'color': HIGHLIGHT_COLOR, 'width': 2},
                'name': 'SeÃ±al ECG (Ejemplo)',
                'hovertemplate': 'Tiempo: %{x:.2f}s<br>Amplitud: %{y:.2f}<extra></extra>'
            }],
            'layout': {
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': '#ccc'},
                'xaxis': {
                    'title': 'Tiempo (s)',
                    'gridcolor': '#2b2b2b',
                    'zerolinecolor': '#2b2b2b',
                    'titlefont': {'color': '#ccc'},
                    'showgrid': True,
                    'gridwidth': 1
                },
                'yaxis': {
                    'title': 'Amplitud ECG',
                    'gridcolor': '#2b2b2b', 
                    'zerolinecolor': '#2b2b2b',
                    'titlefont': {'color': '#ccc'},
                    'showgrid': True,
                    'gridwidth': 1
                },
                'margin': {'t': 40, 'b': 50, 'l': 60, 'r': 30},
                'showlegend': False,
                'title': {
                    'text': 'SeÃ±al ECG (Datos de Ejemplo)',
                    'font': {'color': HIGHLIGHT_COLOR, 'size': 14},
                    'x': 0.5,
                    'xanchor': 'center'
                }
            }
        }
        
        print("âœ… Usando datos de ejemplo para ECG")
        
        return (
            fig_fallback, 
            "72 bpm", 
            "Normal", 
            "85 bpm", 
            "65 bpm", 
            "72 bpm"
        )

# ==========================================================
# CALLBACKS PARA GRÃFICAS AVANZADAS EN MÃ‰TRICAS
# ==========================================================

@app.callback(
    [Output('intensity-recovery-chart', 'figure'),
     Output('performance-heatmap', 'figure'),
     Output('athletic-radar-chart', 'figure')],
    [Input('url', "pathname"),
     Input('current-user', "data")],
    prevent_initial_call=False
)
def generate_advanced_metrics_charts(pathname, current_user):
    """Genera las grÃ¡ficas avanzadas para la pÃ¡gina de mÃ©tricas"""
    
    print(f"ðŸ” Advanced Charts Callback - pathname: {pathname}, user: {current_user}")
    
    # Solo generar grÃ¡ficas si estamos en la pÃ¡gina de mÃ©tricas
    if pathname != '/metricas':
        # Devolver figuras vacÃ­as si no estamos en mÃ©tricas
        empty_fig = {
            'data': [],
            'layout': {
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': '#ccc'},
                'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'yaxis': {'showgrid': False, 'zeroline:': False, 'visible': False},
                'margin': {'t': 10, 'b': 10, 'l': 10, 'r': 10},
                'annotations': [{
                    'text': 'Cargando grÃ¡fica...',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle',
                    'showarrow': False, 'font': {'size': 14, 'color': '#ccc'}
                }]
            }
        }
        return empty_fig, empty_fig, empty_fig
    
    print("ðŸ“Š Generando grÃ¡ficas avanzadas para mÃ©tricas...")
    
    try:
        # 1. GRÃFICA DE INTENSIDAD VS RECUPERACIÃ“N
        days = list(range(1, 31))
        intensity_days = [1, 2, 3, 1, 4, 2, 1, 3, 4, 2, 
                         1, 2, 3, 1, 4, 2, 1, 3, 4, 2,
                         1, 2, 3, 1, 4, 2, 1, 3, 4, 2]
        recovery_days = [2, 1, 2, 3, 1, 2, 3, 2, 1, 3,
                        2, 1, 2, 3, 1, 2, 3, 2, 1, 3,
                        2, 1, 2, 3, 1, 2, 3, 2, 1, 3]
        
        intensity_fig = {
            'data': [
                {
                    'x': days,
                    'y': intensity_days,
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': 'DÃ­as Alta Intensidad',
                    'line': {'color': HIGHLIGHT_COLOR, 'width': 3, 'shape': 'spline'},
                    'marker': {'size': 8, 'color': HIGHLIGHT_COLOR},
                    'fill': 'tozeroy',
                    'fillcolor': 'rgba(0, 212, 255, 0.1)'
                },
                {
                    'x': days,
                    'y': recovery_days,
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': 'DÃ­as RecuperaciÃ³n',
                    'line': {'color': '#4ecdc4', 'width': 3, 'shape': 'spline'},
                    'marker': {'size': 8, 'color': '#4ecdc4'},
                    'fill': 'tozeroy',
                    'fillcolor': 'rgba(78, 205, 196, 0.1)'
                }
            ],
            'layout': {
                'title': {
                    'text': 'AnÃ¡lisis de Intensidad vs RecuperaciÃ³n (Ãšltimos 30 dÃ­as)',
                    'font': {'color': HIGHLIGHT_COLOR, 'size': 18},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'paper_bgcolor': '#1a1a1a',
                'plot_bgcolor': '#1a1a1a',
                'font': {'color': '#ccc'},
                'xaxis': {
                    'title': 'DÃ­as',
                    'gridcolor': '#2b2b2b',
                    'zerolinecolor': '#2b2b2b',
                    'titlefont': {'color': '#ccc', 'size': 14},
                    'tickfont': {'color': '#ccc', 'size': 12},
                    'showgrid': True,
                    'gridwidth': 1,
                    'showline': True,
                    'linecolor': '#444'
                },
                'yaxis': {
                    'title': 'Nivel (1-4)',
                    'gridcolor': '#2b2b2b',
                    'zerolinecolor': '#2b2b2b',
                    'titlefont': {'color': '#ccc', 'size': 14},
                    'tickfont': {'color': '#ccc', 'size': 12},
                    'showgrid': True,
                    'gridwidth': 1,
                    'showline': True,
                    'linecolor': '#444',
                    'range': [0, 5]
                },
                'margin': {'t': 60, 'b': 60, 'l': 80, 'r': 40},
                'showlegend': True,
                'legend': {
                    'x': 0.02,
                    'y': 1,
                    'bgcolor': 'rgba(0,0,0,0.5)',
                    'bordercolor': '#444',
                    'borderwidth': 1,
                    'font': {'color': '#ccc', 'size': 12}
                },
                'hovermode': 'x unified',
                'height': 400
            }
        }
        
        # 2. HEATMAP DE RENDIMIENTO SEMANAL
        days_of_week = ['Lun', 'Mar', 'MiÃ©', 'Jue', 'Vie', 'SÃ¡b', 'Dom']
        weeks = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']
        
        heatmap_data = [
            [2, 5, 3, 7, 6, 1, 4],
            [4, 6, 5, 8, 7, 3, 2],
            [3, 7, 6, 8, 5, 4, 1],
            [5, 8, 7, 6, 4, 2, 3]
        ]
        
        colorscale = [
            [0, '#0a2a38'],
            [0.4, '#006d8f'],
            [1, HIGHLIGHT_COLOR]
        ]
        
        heatmap_fig = {
            'data': [{
                'z': heatmap_data,
                'x': days_of_week,
                'y': weeks,
                'type': 'heatmap',
                'colorscale': colorscale,
                'showscale': True,
                'colorbar': {
                    'title': 'Intensidad',
                    'titleside': 'right',
                    'titlefont': {'color': '#ccc', 'size': 12},
                    'tickfont': {'color': '#ccc', 'size': 11},
                    'ticks': 'outside',
                    'tickcolor': '#ccc',
                    'ticklen': 5,
                    'thickness': 15,
                    'len': 0.8
                },
                'hovertemplate': 'DÃ­a: %{x}<br>Semana: %{y}<br>Intensidad: %{z}/8<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Heatmap de Rendimiento Semanal',
                    'font': {'color': HIGHLIGHT_COLOR, 'size': 18},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'paper_bgcolor': '#1a1a1a',
                'plot_bgcolor': '#1a1a1a',
                'font': {'color': '#ccc'},
                'xaxis': {
                    'side': 'bottom',
                    'tickfont': {'color': '#ccc', 'size': 12},
                    'gridcolor': '#2b2b2b',
                    'linecolor': '#444'
                },
                'yaxis': {
                    'tickfont': {'color': '#ccc', 'size': 12},
                    'gridcolor': '#2b2b2b',
                    'linecolor': '#444'
                },
                'margin': {'t': 60, 'b': 60, 'l': 80, 'r': 80},
                'height': 350
            }
        }
        
        # 3. RADAR DE COMPETENCIAS ATLÃ‰TICAS
        categories = ['Resistencia', 'Fuerza', 'Velocidad', 'Flexibilidad', 'Agilidad', 'Potencia']
        user_values = [92, 88, 95, 78, 85, 90]
        elite_values = [98, 96, 99, 95, 97, 98]
        
        radar_fig = go.Figure()
        
        radar_fig.add_trace(go.Scatterpolar(
            r=elite_values,
            theta=categories,
            fill='toself',
            name='Atleta Ã‰lite (Referencia)',
            line_color='rgba(255, 255, 255, 0.4)',
            fillcolor='rgba(255, 255, 255, 0.1)',
            line_width=2,
            opacity=0.6
        ))
        
        radar_fig.add_trace(go.Scatterpolar(
            r=user_values,
            theta=categories,
            fill='toself',
            name='Tu Rendimiento',
            line_color=HIGHLIGHT_COLOR,
            fillcolor=f'rgba(0, 212, 255, 0.3)',
            line_width=3,
            opacity=0.8
        ))
        
        radar_fig.update_layout(
            title={
                'text': 'Radar de Competencias AtlÃ©ticas',
                'font': {'color': HIGHLIGHT_COLOR, 'size': 18, 'family': "'Inter', sans-serif"},
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.95
            },
            paper_bgcolor='#1a1a1a',
            plot_bgcolor='#1a1a1a',
            font={'color': '#ccc', 'family': "'Inter', sans-serif", 'size': 12},
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont={'color': '#ccc', 'size': 10, 'family': "'Inter', sans-serif"},
                    gridcolor='#2b2b2b',
                    linecolor='#444',
                    ticksuffix='%',
                    showline=True,
                    linewidth=1,
                    tickmode='array',
                    tickvals=[0, 20, 40, 60, 80, 100],
                    ticktext=['0%', '20%', '40%', '60%', '80%', '100%'],
                    tickangle=0,
                    ticklen=5,
                    tickwidth=1,
                    layer='below traces'
                ),
                angularaxis=dict(
                    tickfont={'color': '#ccc', 'size': 12, 'family': "'Inter', sans-serif"},
                    gridcolor='#2b2b2b',
                    linecolor='#444',
                    rotation=90,
                    direction='clockwise'
                ),
                bgcolor='#141414',
                sector=[0, 360],
                hole=0
            ),
            showlegend=True,
            legend=dict(
                x=1.05,
                y=0.5,
                bgcolor='rgba(20, 20, 20, 0.8)',
                bordercolor='#444',
                borderwidth=1,
                font={'color': '#ccc', 'size': 11, 'family': "'Inter', sans-serif"},
                orientation='v'
            ),
            margin=dict(t=80, b=80, l=80, r=120),
            height=450,
            width=None,
            hovermode='closest',
            autosize=True
        )
        
        radar_fig.update_traces(
            hovertemplate='<b>%{theta}</b><br>PuntuaciÃ³n: %{r}%<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(26, 26, 26, 0.9)',
                font_size=12,
                font_family="'Inter', sans-serif"
            )
        )
        
        radar_fig.update_layout(
            autosize=True,
            dragmode=False
        )
        
        print("âœ… GrÃ¡ficas avanzadas generadas exitosamente")
        
        return intensity_fig, heatmap_fig, radar_fig
        
    except Exception as e:
        print(f"âŒ Error generando grÃ¡ficas avanzadas: {e}")
        import traceback
        traceback.print_exc()
        
        error_fig_intensity = {
            'data': [],
            'layout': {
                'title': {
                    'text': 'Error: Intensidad vs RecuperaciÃ³n',
                    'font': {'color': '#ff6b6b', 'size': 16}
                },
                'paper_bgcolor': '#1a1a1a',
                'plot_bgcolor': '#1a1a1a',
                'font': {'color': '#ccc'},
                'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'margin': {'t': 60, 'b': 60, 'l': 80, 'r': 40},
                'annotations': [{
                    'text': 'Error cargando datos. Intenta recargar.',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle',
                    'showarrow': False,
                    'font': {'size': 14, 'color': '#ff6b6b'}
                }],
                'height': 400
            }
        }
        
        error_fig_heatmap = {
            'data': [],
            'layout': {
                'title': {
                    'text': 'Error: Heatmap de Rendimiento',
                    'font': {'color': '#ff6b6b', 'size': 16}
                },
                'paper_bgcolor': '#1a1a1a',
                'plot_bgcolor': '#1a1a1a',
                'font': {'color': '#ccc'},
                'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
                'margin': {'t': 60, 'b': 60, 'l': 80, 'r': 80},
                'annotations': [{
                    'text': 'Error cargando datos. Intenta recargar.',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle',
                    'showarrow': False,
                    'font': {'size': 14, 'color': '#ff6b6b'}
                }],
                'height': 350
            }
        }
        
        error_fig_radar = go.Figure()
        error_fig_radar.update_layout(
            title={
                'text': 'Error: Radar de Competencias',
                'font': {'color': '#ff6b6b', 'size': 16}
            },
            paper_bgcolor='#1a1a1a',
            plot_bgcolor='#1a1a1a',
            font={'color': '#ccc'},
            margin=dict(t=60, b=60, l=60, r=100),
            height=400,
            annotations=[{
                'text': 'Error cargando datos del radar. Intenta recargar.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle',
                'showarrow': False,
                'font': {'size': 14, 'color': '#ff6b6b'}
            }]
        )
        
        return error_fig_intensity, error_fig_heatmap, error_fig_radar

# ==========================================================
# CALLBACK PARA CONFIGURACIÃ“N SIMPLIFICADA DE GRÃFICAS
# ==========================================================

@app.callback(
    [Output('intensity-recovery-chart', 'config'),
     Output('performance-heatmap', 'config'),
     Output('athletic-radar-chart', 'config')],
    Input('url', "pathname"),
    prevent_initial_call=False
)
def configure_minimal_toolbars(pathname):
    """ConfiguraciÃ³n ultra-simplificada: solo zoom y descargar"""
    
    if pathname != '/metricas':
        # ConfiguraciÃ³n vacÃ­a cuando no estamos en mÃ©tricas
        return {}, {}, {}
    
    # ConfiguraciÃ³n comÃºn para TODAS las grÃ¡ficas
    minimal_config = {
        'displayModeBar': True,      # Muestra la barra
        'displaylogo': False,        # Sin logo de Plotly
        'modeBarButtonsToRemove': [  # Remueve TODOS los botones por defecto
            'pan2d', 'select2d', 'lasso2d', 
            'zoomIn2d', 'zoomOut2d', 'autoScale2d', 
            'resetScale2d', 'hoverClosestCartesian',
            'hoverCompareCartesian', 'toggleSpikelines',
            'zoom2d', 'toImage'  # TambiÃ©n removemos estos para luego agregarlos limpios
        ],
        'modeBarButtons': [          # Solo estos dos botones
            ['zoom2d'],              # BotÃ³n de zoom
            ['toImage']              # BotÃ³n de descargar
        ],
        'toImageButtonOptions': {
            'format': 'png',         # Formato PNG
            'filename': 'athletica_grafica',  # Nombre por defecto
            'height': 600,
            'width': 1000,
            'scale': 1              # Escala normal, sin ampliaciÃ³n
        }
    }
    
    # Configuraciones especÃ­ficas para cada grÃ¡fica
    intensity_config = minimal_config.copy()
    intensity_config['toImageButtonOptions']['filename'] = 'intensidad_recuperacion'
    
    heatmap_config = minimal_config.copy()
    heatmap_config['toImageButtonOptions']['filename'] = 'heatmap_rendimiento'
    heatmap_config['toImageButtonOptions']['height'] = 500
    heatmap_config['toImageButtonOptions']['width'] = 800
    
    radar_config = minimal_config.copy()
    radar_config['toImageButtonOptions']['filename'] = 'radar_competencias'
    radar_config['toImageButtonOptions']['height'] = 500
    radar_config['toImageButtonOptions']['width'] = 800
    
    return intensity_config, heatmap_config, radar_config

# ==========================================================
# CALLBACK PARA EL MODAL DE AGREGAR OBJETIVOS (CORREGIDO)
# ==========================================================

@app.callback(
    Output("modal-add-goal", "is_open"),
    [Input("btn-agregar-objetivo", "n_clicks"),
     Input("btn-cancel-goal", "n_clicks"),
     Input("btn-submit-goal", "n_clicks")],
    [State("modal-add-goal", "is_open"),
     State("url", "pathname")],
    prevent_initial_call=True
)
def toggle_modal(open_clicks, cancel_clicks, submit_clicks, is_open, pathname):
    """Abre/cierra el modal de agregar objetivo - VERSIÃ“N CORREGIDA"""
    
    # Verificar que estamos en la pÃ¡gina correcta
    if pathname != '/objetivos':
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Si se hace clic en "Agregar Nuevo Objetivo" o "Cancelar", alternar estado
    if trigger_id in ["btn-agregar-objetivo", "btn-cancel-goal"]:
        return not is_open
    # Si se hace clic en "Agregar Objetivo", cerrar el modal
    elif trigger_id == "btn-submit-goal":
        return False
    
    return is_open

@app.callback(
    [Output("choose-goal-type", "style"),
     Output("goal-form-container", "style"),
     Output("goal-type-icon", "children"),
     Output("goal-type-text", "children"),
     Output("goal-type-text", "style")],
    [Input("btn-health-goal", "n_clicks"),
     Input("btn-fitness-goal", "n_clicks"),
     Input("btn-back-to-choose", "n_clicks"),
     Input("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def toggle_goal_form(health_clicks, fitness_clicks, back_clicks, pathname):
    """Alterna entre la selecciÃ³n de tipo y el formulario - VERSIÃ“N CORREGIDA"""
    
    # Verificar que estamos en la pÃ¡gina correcta
    if pathname != '/objetivos':
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "btn-back-to-choose":
        # Volver a la selecciÃ³n de tipo
        return (
            {'display': 'block'},
            {'display': 'none'},
            "â¤ï¸",
            "Salud",
            {'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.1rem'}
        )
    
    elif trigger_id == "btn-health-goal":
        # Mostrar formulario para objetivo de salud
        return (
            {'display': 'none'},
            {'display': 'block'},
            "â¤ï¸",
            "Salud",
            {'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.1rem'}
        )
    
    elif trigger_id == "btn-fitness-goal":
        # Mostrar formulario para objetivo de fitness
        return (
            {'display': 'none'},
            {'display': 'block'},
            "ðŸ’ª",
            "Fitness",
            {'color': '#ffd166', 'fontWeight': 'bold', 'fontSize': '1.1rem'}
        )
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    [Output("btn-health-goal", "style"),
     Output("btn-fitness-goal", "style")],
    [Input("btn-health-goal", "n_clicks"),
     Input("btn-fitness-goal", "n_clicks"),
     Input("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def highlight_selected_goal(health_clicks, fitness_clicks, pathname):
    """Resalta visualmente la opciÃ³n seleccionada - VERSIÃ“N CORREGIDA"""
    
    # Verificar que estamos en la pÃ¡gina correcta
    if pathname != '/objetivos':
        # Devolver estilos vacÃ­os
        return dash.no_update, dash.no_update
    
    ctx = dash.callback_context
    if not ctx.triggered:
        # Estado inicial
        return [
            {'backgroundColor': 'rgba(0, 212, 255, 0.1)', 'border': '1px solid rgba(0, 212, 255, 0.3)', 'borderRadius': '12px', 'padding': '20px', 'cursor': 'pointer', 'transition': 'all 0.3s ease', 'color': 'white', 'textAlign': 'center'},
            {'backgroundColor': 'rgba(255, 209, 102, 0.1)', 'border': '1px solid rgba(255, 209, 102, 0.3)', 'borderRadius': '12px', 'padding': '20px', 'cursor': 'pointer', 'transition': 'all 0.3s ease', 'color': 'white', 'textAlign': 'center'}
        ]
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "btn-health-goal":
        # Salud seleccionada
        return [
            {'backgroundColor': 'rgba(0, 212, 255, 0.25)', 'border': f'2px solid {HIGHLIGHT_COLOR}', 'borderRadius': '12px', 'padding': '20px', 'cursor': 'pointer', 'transition': 'all 0.3s ease', 'color': 'white', 'textAlign': 'center', 'boxShadow': f'0 0 15px rgba(0, 212, 255, 0.5)'},
            {'backgroundColor': 'rgba(255, 209, 102, 0.1)', 'border': '1px solid rgba(255, 209, 102, 0.3)', 'borderRadius': '12px', 'padding': '20px', 'cursor': 'pointer', 'transition': 'all 0.3s ease', 'color': 'white', 'textAlign': 'center'}
        ]
    
    elif trigger_id == "btn-fitness-goal":
        # Fitness seleccionado
        return [
            {'backgroundColor': 'rgba(0, 212, 255, 0.1)', 'border': '1px solid rgba(0, 212, 255, 0.3)', 'borderRadius': '12px', 'padding': '20px', 'cursor': 'pointer', 'transition': 'all 0.3s ease', 'color': 'white', 'textAlign': 'center'},
            {'backgroundColor': 'rgba(255, 209, 102, 0.25)', 'border': '2px solid #ffd166', 'borderRadius': '12px', 'padding': '20px', 'cursor': 'pointer', 'transition': 'all 0.3s ease', 'color': 'white', 'textAlign': 'center', 'boxShadow': '0 0 15px rgba(255, 209, 102, 0.5)'}
        ]
    
    return dash.no_update

# ==========================================================
# CALLBACKS PARA ACTIVIDAD (INDICADOR) - SOLO EN ONBOARDING
# ==========================================================

@app.callback(
    Output("activity-level-indicator", "children"),
    [Input("input-activity-level", "value"),
     Input("url", "pathname")],
    prevent_initial_call=True
)
def update_activity_indicator(activity_level, current_path):
    """Actualiza indicador de nivel de actividad - SOLO en onboarding"""
    
    # SOLO EJECUTAR SI ESTAMOS EN ONBOARDING
    if current_path != '/onboarding' and current_path is not None:
        raise dash.exceptions.PreventUpdate
    
    # Usar contexto para determinar quÃ© disparÃ³ el callback
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    # Obtener quÃ© input disparÃ³ el callback
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Si se disparÃ³ por cambio de URL (navegaciÃ³n) y activity_level es None, usar valor por defecto
    if trigger_id == 'url' and activity_level is None:
        activity_level = 5
    # Si se disparÃ³ por el slider pero activity_level es None, prevenir actualizaciÃ³n
    elif activity_level is None:
        raise dash.exceptions.PreventUpdate
    
    # Definir niveles de actividad
    levels = {
        1: ("Muy Baja", "Actividad mÃ­nima o sedentaria"),
        2: ("Baja", "Actividad muy ligera"),
        3: ("Media-Baja", "Actividad ocasional"),
        4: ("Media", "Actividad regular ligera"),
        5: ("Media-Alta", "Actividad moderada regular"),
        6: ("Alta", "Actividad consistente"),
        7: ("Muy Alta", "Actividad frecuente e intensa"),
        8: ("Excelente", "Actividad muy frecuente"),
        9: ("AtlÃ©tico", "Nivel atlÃ©tico"),
        10: ("Ã‰lite", "Nivel atlÃ©tico avanzado")
    }
    
    level_name, description = levels.get(activity_level, ("Media", "Actividad moderada"))
    health_score = get_health_score_from_activity_level(activity_level)
    
    # Crear puntos de vista previa del estado de salud
    preview_dots = []
    for i in range(5):
        if i < health_score:
            dot_style = {
                'width': '8px',
                'height': '8px',
                'backgroundColor': HIGHLIGHT_COLOR,
                'borderRadius': '50%',
                'display': 'inline-block',
                'margin': '0 2px',
                'boxShadow': f'0 0 4px {HIGHLIGHT_COLOR}'
            }
        else:
            dot_style = {
                'width': '8px',
                'height': '8px',
                'backgroundColor': '#444',
                'borderRadius': '50%',
                'display': 'inline-block',
                'margin': '0 2px',
                'border': '1px solid #666'
            }
        preview_dots.append(html.Div(style=dot_style))
    
    # Crear y retornar el contenido del indicador
    return html.Div([
        html.Div(f"Nivel: {level_name} ({activity_level}/10)", 
                style={'color': HIGHLIGHT_COLOR, 'fontWeight': 'bold', 'marginBottom': '5px'}),
        html.Div(description, 
                style={'color': '#ccc', 'fontSize': '0.9rem', 'marginBottom': '8px'}),
        html.Div(preview_dots, 
                style={'display': 'flex', 'justifyContent': 'center', 'gap': '2px'})
    ])

# ==========================================================
# CALLBACKS DE DIAGNÃ“STICO
# ==========================================================

@app.callback(
    Output("current-user-debug", "children"),
    Input("current-user", "data")
)
def debug_current_user(current_user):
    print(f"ðŸ” STORE current-user actualizado: {current_user}")
    return f"Usuario actual: {current_user}"

@app.callback(
    Output("onboarding-completed-debug", "children"), 
    Input("onboarding-completed", "data")
)
def debug_onboarding_completed(onboarding_completed):
    print(f"ðŸ” STORE onboarding-completed actualizado: {onboarding_completed}")
    return f"Onboarding: {onboarding_completed}"

def force_onboarding_completed(current_user):
    """Obtiene el estado de onboarding del usuario"""
    if current_user and current_user in USERS_DB:
        user_data = USERS_DB[current_user]
        # IMPORTANTE: Verificar si existe la clave, si no, asumir que necesita onboarding
        onboarding_status = user_data.get("onboarding_completed", False)
        print(f"ðŸ” Estado onboarding de {current_user}: {onboarding_status}")
        return onboarding_status
    return False

@app.callback(
    Output("stores-debug", "children"),
    [Input("current-user", "data"),
     Input("onboarding-completed", "data"),
     Input("url", "pathname")]
)
def debug_all_stores(current_user, onboarding_completed, pathname):
    print(f"ðŸ” DEBUG COMPLETO - current-user: {current_user}, onboarding: {onboarding_completed}, pathname: {pathname}")
    return f"Stores: user={current_user}, onboarding={onboarding_completed}, path={pathname}"

# ==========================================================
# CALLBACKS PARA ENTRENAMIENTOS
# ==========================================================

@app.callback(
    [Output("btn-conectar-text", "children"),
     Output("icono-estado", "style"),
     Output("texto-estado", "children"),
     Output("bluetooth-status-store", "data")],
    [Input("btn-conectar-bluetooth", "n_clicks")],
    [State("bluetooth-status-store", "data"),
     State("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def toggle_bluetooth_connection(n_clicks, bluetooth_status, pathname):
    """Alterna el estado de conexiÃ³n Bluetooth - VERSIÃ“N CORREGIDA"""
    
    # Verificar que estamos en la pÃ¡gina correcta
    if pathname != '/entrenamientos':
        raise dash.exceptions.PreventUpdate
    
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Obtener estado actual
    is_connected = bluetooth_status.get('connected', False) if bluetooth_status else False
    
    # Alternar estado
    new_status = not is_connected
    
    # Actualizar interfaz segÃºn el nuevo estado
    if new_status:
        # Estado: Conectado
        return (
            "Desconectar Dispositivo",
            {'color': '#4ecdc4', 'fontSize': '0.8rem', 'marginRight': '8px'},
            "Dispositivo conectado - ON",
            {'connected': True}
        )
    else:
        # Estado: Desconectado
        return (
            "Conectar Dispositivo",
            {'color': '#ff6b6b', 'fontSize': '0.8rem', 'marginRight': '8px'},
            "Dispositivo desconectado",
            {'connected': False}
        )
    
# ==========================================================
# CALLBACK PARA CARGAR OBJETIVOS AL ABRIR PÃGINA
# ==========================================================

@app.callback(
    Output("user-goals-store", "data", allow_duplicate=True),
    [Input("url", "pathname")],
    [State("current-user", "data")],
    prevent_initial_call=True
)
def load_goals_when_page_opens(pathname, current_user):
    """Carga objetivos cuando se abre la pÃ¡gina de objetivos"""
    
    if pathname != '/objetivos':
        raise dash.exceptions.PreventUpdate
    
    if not current_user:
        print("âš ï¸ No hay usuario para cargar objetivos")
        raise dash.exceptions.PreventUpdate
    
    print(f"ðŸ“‹ Cargando objetivos para {current_user} al abrir pÃ¡gina")
    goals = get_user_goals_for_display(current_user)
    print(f"âœ… Objetivos cargados: {len(goals.get('fitness', []))} fitness, {len(goals.get('health', []))} health")
    
    return goals

# ==========================================================
# CALLBACK DINÃMICO PARA ONBOARDING (MODIFICADO - CORREGIDO)
# ==========================================================

@app.callback(
    [Output("onboarding-content", "children"),
     Output("onboarding-current-step-title", "children"),
     Output("onboarding-current-step-subtitle", "children"),
     Output("onboarding-progress-bar", "style"),
     Output("onboarding-step", "data"),
     Output("onboarding-prev-btn-visual", "style"),
     Output("onboarding-next-btn-visual", "children")],
    [Input("onboarding-step", "data"),
     Input("onboarding-user-name", "data"),
     Input("onboarding-next-btn-visual", "n_clicks"),
     Input("onboarding-prev-btn-visual", "n_clicks")],
    [State("url", "pathname")],  # Â¡ESTO ES CRÃTICO!
    prevent_initial_call=True
)
def update_onboarding_step_dynamic(step, user_name, next_clicks, prev_clicks, current_path):
    """Callback dinÃ¡mico que solo se ejecuta cuando estamos en onboarding"""
    
    # Â¡VERIFICACIÃ“N MÃS ESTRICTA!
    ctx = dash.callback_context
    if not ctx.triggered:
        current_step = step if step else 1
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # SI NO ESTAMOS EN ONBOARDING, PREVENIR TODO
        if current_path != '/onboarding' and current_path is not None:
            print(f"ðŸš« Callback prevenido: Estamos en {current_path}, no en /onboarding")
            raise dash.exceptions.PreventUpdate
        
        if trigger_id == "onboarding-step":
            current_step = step
        elif trigger_id == "onboarding-user-name":
            current_step = step
        elif trigger_id == "onboarding-next-btn-visual" and next_clicks:
            current_step = min(step + 1, 5) if step else 1
        elif trigger_id == "onboarding-prev-btn-visual" and prev_clicks:
            current_step = max(step - 1, 1) if step else 1
        else:
            current_step = step if step else 1
    
    # El resto de tu lÃ³gica original aquÃ­...
    step_titles = {
        1: "Â¡Bienvenido/a a Athletica!",
        2: "Datos BiomÃ©tricos BÃ¡sicos",
        3: "Actividad y Objetivos",
        4: "Salud y Precauciones",
        5: "SueÃ±o y NutriciÃ³n"
    }
    
    step_subtitles = {
        1: "Vamos a crear tu plan personalizado paso a paso.",
        2: "InformaciÃ³n bÃ¡sica para calibrar tus mÃ©tricas.",
        3: "Define tu nivel de actividad y objetivos principales.",
        4: "InformaciÃ³n relevante para tu seguridad.",
        5: "Preferencias para optimizar tu rendimiento."
    }
    
    if current_step == 1:
        step_content = onboarding_step_1(user_name=user_name if user_name else "Usuario/a")
    elif current_step == 2:
        step_content = onboarding_step_2()
    elif current_step == 3:
        step_content = onboarding_step_3()
    elif current_step == 4:
        step_content = onboarding_step_4()
    elif current_step == 5:
        step_content = onboarding_step_5()
    else:
        step_content = onboarding_step_1(user_name=user_name if user_name else "Usuario/a")
    
    progress_width = f"{((current_step - 1) / 4) * 100}%"
    prev_btn_style = {"display": "block"} if current_step > 1 else {"display": "none"}
    next_btn_text = "Finalizar" if current_step == 5 else "Siguiente"
    
    return (
        step_content,
        step_titles[current_step],
        step_subtitles[current_step],
        {"width": progress_width},
        current_step,
        prev_btn_style,
        next_btn_text
    )

# ==========================================================
# CALLBACK PARA COMPLETAR ONBOARDING (SIMPLIFICADO - SOLO UNO)
# ==========================================================

@app.callback(
    Output("onboarding-completed", "data"),
    Input("onboarding-next-btn-visual", "n_clicks"),
    [State("onboarding-step", "data"),
     State("current-user", "data"),
     State("url", "pathname")],  # Â¡ESTO ES CRÃTICO!
    prevent_initial_call=True
)
def mark_onboarding_complete(n_clicks, current_step, current_user, pathname):
    """Marca el onboarding como completado - VERSIÃ“N DEFINITIVA"""
    
    # Â¡VERIFICACIÃ“N DOBLE!
    # 1. Verificar que estamos en /onboarding
    if pathname != '/onboarding' and pathname is not None:
        print(f"ðŸš« Completion callback prevenido: Estamos en {pathname}")
        raise dash.exceptions.PreventUpdate
    
    # 2. Verificar que el botÃ³n fue clickeado y estamos en el paso 5
    if not n_clicks or current_step != 5:
        raise dash.exceptions.PreventUpdate
    
    # 3. Verificar que hay usuario
    if not current_user:
        print("âš ï¸ No hay usuario para completar onboarding")
        raise dash.exceptions.PreventUpdate
    
    print(f"âœ… Marcando onboarding como completado para {current_user}")
    
    if current_user:
        success = mark_onboarding_completed(current_user)
        if success:
            print(f"âœ… Onboarding completado exitosamente")
            return True
    
    raise dash.exceptions.PreventUpdate

# CALLBACK SEPARADO PARA NAVEGACIÃ“N DESPUÃ‰S DE ONBOARDING

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("onboarding-completed", "data"),
    [State("url", "pathname")],  # Â¡AÃ‘ADE ESTO!
    prevent_initial_call=True
)
def redirect_after_onboarding(onboarding_completed, current_path):
    """Redirige a inicio despuÃ©s de completar onboarding"""
    
    # Â¡VERIFICAR QUE ESTAMOS EN ONBOARDING!
    if current_path != '/onboarding':
        raise dash.exceptions.PreventUpdate
    
    if onboarding_completed:
        print("ðŸŽ¯ Onboarding completado, redirigiendo a /inicio")
        return '/inicio'
    
    raise dash.exceptions.PreventUpdate

@app.callback(
    Output("selected-sports-store", "data"),
    [Input({"type": "sport-card", "index": dash.ALL}, "n_clicks")],
    [State({"type": "sport-card", "index": dash.ALL}, "className"),
     State("selected-sports-store", "data"),
     State("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def update_sports_selection_dynamic(clicks, class_names, current_selection, current_path):
    """Actualiza la selecciÃ³n de deportes - VERSIÃ“N CORREGIDA"""
    
    # SOLO EJECUTAR SI ESTAMOS EN ONBOARDING
    if current_path != '/onboarding' and current_path is not None:
        raise dash.exceptions.PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_selection or []
    
    # Verificar si hay algÃºn trigger vÃ¡lido
    triggered_prop = ctx.triggered[0]['prop_id']
    if triggered_prop == '.' or 'index' not in triggered_prop:
        return current_selection or []
    
    try:
        triggered_index = ctx.triggered[0]['prop_id'].split('"index":"')[1].split('"')[0]
        
        if current_selection is None:
            current_selection = []
        
        if triggered_index not in current_selection:
            current_selection.append(triggered_index)
        else:
            current_selection.remove(triggered_index)
        
        return current_selection
    except (IndexError, KeyError):
        # Si hay un error al parsear el Ã­ndice, devolver la selecciÃ³n actual
        return current_selection or []
    
@app.callback(
    [Output({"type": "sport-card", "index": sport["label"]}, "className") for sport in SPORTS_OPTIONS],
    [Input("selected-sports-store", "data"),
     Input("url", "pathname")],  # AÃ‘ADIR pathname
    prevent_initial_call=True
)
def update_sport_card_styles_dynamic(selected_sports, current_path):
    """Actualiza estilos de tarjetas de deporte - VERSIÃ“N CORREGIDA"""
    
    # SOLO EJECUTAR SI ESTAMOS EN ONBOARDING
    if current_path != '/onboarding' and current_path is not None:
        # Devolver estilos vacÃ­os para prevenir errores
        return ["radio-card"] * len(SPORTS_OPTIONS)
    
    styles = []
    selected = selected_sports or []
    
    for sport in SPORTS_OPTIONS:
        if sport["label"] in selected:
            styles.append("radio-card radio-card-checked")
        else:
            styles.append("radio-card")
    
    return styles

# ==========================================================
# ==========================================================
# CALLBACKS PARA SELECCIÓN DE TIPO DE USUARIO EN REGISTRO (NUEVOS)
# ==========================================================

_REG_TYPE_BUTTON_BASE_STYLE = {
    'borderRadius': '10px',
    'padding': '15px',
    'cursor': 'pointer',
    'transition': 'all 0.3s ease',
    'color': 'white',
    'textAlign': 'center',
    'flex': '1',
    'minWidth': '140px',
    'maxWidth': '160px',
    'minHeight': '100px',
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'center',
    'alignItems': 'center'
}


def _build_reg_type_button_style(role, selected):
    style = dict(_REG_TYPE_BUTTON_BASE_STYLE)

    if role == "athlete":
        if selected:
            style.update({
                'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                'border': '2px solid ' + HIGHLIGHT_COLOR,
                'boxShadow': f'0 0 10px {HIGHLIGHT_COLOR}'
            })
        else:
            style.update({
                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                'border': '2px solid rgba(0, 212, 255, 0.3)'
            })
    else:
        if selected:
            style.update({
                'backgroundColor': 'rgba(78, 205, 196, 0.2)',
                'border': '2px solid #4ecdc4',
                'boxShadow': '0 0 10px #4ecdc4'
            })
        else:
            style.update({
                'backgroundColor': 'rgba(78, 205, 196, 0.1)',
                'border': '2px solid rgba(78, 205, 196, 0.3)'
            })

    return style


def _build_reg_type_indicator(selected_type):
    if selected_type == "doctor":
        return "Seleccionado: Médico", {
            'marginTop': '15px',
            'padding': '8px 12px',
            'backgroundColor': 'rgba(78, 205, 196, 0.1)',
            'borderRadius': '6px',
            'textAlign': 'center',
            'fontSize': '0.9rem',
            'color': '#4ecdc4'
        }

    return "Seleccionado: Atleta", {
        'marginTop': '15px',
        'padding': '8px 12px',
        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
        'borderRadius': '6px',
        'textAlign': 'center',
        'fontSize': '0.9rem',
        'color': HIGHLIGHT_COLOR
    }


@app.callback(
    [Output("btn-reg-type-athlete", "style"),
     Output("btn-reg-type-doctor", "style"),
     Output("reg-user-type", "value"),
     Output("reg-type-indicator", "children"),
     Output("reg-type-indicator", "style")],
    [Input("btn-reg-type-athlete", "n_clicks"),
     Input("btn-reg-type-doctor", "n_clicks")],
    prevent_initial_call=True
)
def handle_user_type_selection(athlete_clicks, doctor_clicks):
    """Maneja la selección de tipo de usuario con botones visuales"""
    ctx = dash.callback_context

    selected_type = "athlete"
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == "btn-reg-type-doctor":
            selected_type = "doctor"

    athlete_style = _build_reg_type_button_style("athlete", selected_type == "athlete")
    doctor_style = _build_reg_type_button_style("doctor", selected_type == "doctor")
    indicator_text, indicator_style = _build_reg_type_indicator(selected_type)

    return athlete_style, doctor_style, selected_type, indicator_text, indicator_style
# CALLBACK PARA LOGIN (MODIFICADO - ÃšNICO)
# ==========================================================

@app.callback(
    [Output("current-user", "data", allow_duplicate=True),  # <-- AÃ‘ADE allow_duplicate=True
     Output("login-message", "children"),
     Output("onboarding-completed", "data", allow_duplicate=True),
     Output("onboarding-user-name", "data", allow_duplicate=True),
     Output("user-type-store", "data", allow_duplicate=True)],  # <-- AÃ‘ADE allow_duplicate=True
    [Input("login-btn", "n_clicks")],
    [State("login-username", "value"),
     State("login-password", "value")],
    prevent_initial_call=True
)

def handle_login(n_clicks, username, password):
    """Maneja el inicio de sesiÃ³n"""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    
    if not username or not password:
        return None, "Por favor ingresa usuario y contraseÃ±a", dash.no_update, dash.no_update, dash.no_update
    
    user_data = verify_user(username, password)
    if user_data:
        print(f"âœ… Login exitoso: {username}")
        
        # OBTENER EL ESTADO DE ONBOARDING DEL USUARIO
        user_type = user_data.get("user_type", "athlete")
        onboarding_status = False
        
        if user_type == "athlete":
            onboarding_status = force_onboarding_completed(username)
        elif user_type == "doctor":
            # Los mÃ©dicos no necesitan onboarding
            onboarding_status = True
        
        print(f"ðŸ“‹ Estado onboarding para {username}: {onboarding_status}")
        
        return username, "", onboarding_status, username, user_type
    else:
        print(f"âŒ Login fallido: {username}")
        return None, "Usuario o contraseÃ±a incorrectos", dash.no_update, dash.no_update, dash.no_update
    
# ==========================================================
# CALLBACK PARA REGISTRO (AGREGADO)
# ==========================================================
@app.callback(
    [Output("current-user", "data", allow_duplicate=True),
     Output("register-message", "children"),
     Output("onboarding-completed", "data", allow_duplicate=True),
     Output("onboarding-user-name", "data", allow_duplicate=True),
     Output("user-type-store", "data", allow_duplicate=True)],  
    [Input("register-btn", "n_clicks")],
    [State("reg-username", "value"),
     State("reg-email", "value"),
     State("reg-password", "value"),
     State("reg-password2", "value"),
     State("accept-terms", "value"),
     State("reg-user-type", "value")],
    prevent_initial_call=True
)
def handle_registration(n_clicks, username, email, password, password2, terms_accepted, user_type):
    """Maneja el registro de nuevos usuarios"""
    
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    def registration_error(message):
        return None, message, dash.no_update, dash.no_update, dash.no_update
    
    print(f"ðŸ“ Iniciando registro para: {username} como {user_type}")
    
    # Validaciones bÃ¡sicas
    if not username or not email or not password:
        print("âŒ Campos incompletos")
        return registration_error("âŒ Por favor completa todos los campos")
    
    if password != password2:
        print("âŒ ContraseÃ±as no coinciden")
        return registration_error("âŒ Las contraseÃ±as no coinciden")
    
    if not terms_accepted:
        print("âŒ TÃ©rminos no aceptados")
        return registration_error("âŒ Debes aceptar los tÃ©rminos y condiciones")
    
    # Verificar si el usuario ya existe (en ambas bases de datos)
    if username in USERS_DB or username in DOCTORS_DB:
        print(f"âŒ Usuario {username} ya existe")
        return registration_error("âŒ El nombre de usuario ya existe")
    
    # Verificar si el email ya existe
    email_owner = get_email_owner_type(email)
    if email_owner:
        owner_label = "atleta" if email_owner == "athlete" else "mÃ©dico"
        print(f"âŒ Email {email} ya registrado como {owner_label}")
        return registration_error("âŒ El email ya estÃ¡ registrado")
    
    # Crear nuevo usuario
    print(f"âœ… Creando usuario: {username}, email: {email}, tipo: {user_type}")
    
    # Usar la funciÃ³n save_user actualizada
    success = save_user(username, email, password, full_name=username, user_type=user_type)
    
    if success:
        print(f"ðŸŽ‰ Usuario {username} registrado exitosamente como {user_type}")
        
        # Mensaje de Ã©xito
        success_message = html.Div([
            html.I(className="bi bi-check-circle me-2", style={'color': 'green'}),
            f"Â¡Registro exitoso como {user_type}! Redirigiendo..."
        ])
        
        # Determinar estado de onboarding basado en tipo
        onboarding_needed = user_type == "athlete"  # Solo atletas necesitan onboarding
        
        return username, success_message, not onboarding_needed, username, user_type
    
    else:
        print(f"âŒ Error al registrar usuario {username}")
        return registration_error("âŒ Error al registrar usuario. Intenta nuevamente.")

# ==========================================================
# CALLBACK PARA REDIRECCIÃ“N DESPUÃ‰S DE REGISTRO (AGREGADO)
# ==========================================================

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input("current-user", "data")],
    [State("onboarding-completed", "data"),
     State("url", "pathname")],
    prevent_initial_call=True
)
def redirect_after_registration(current_user, onboarding_completed, current_path):
    """Redirige al onboarding despuÃ©s de registro exitoso"""
    
    print(f"ðŸ” REDIRECT AFTER REGISTRATION - user: {current_user}, onboarding: {onboarding_completed}, path: {current_path}")
    
    # Solo ejecutar si estamos en la pÃ¡gina de registro
    if current_path != '/register':
        print(f"âš ï¸ No estamos en /register, estamos en {current_path}")
        raise dash.exceptions.PreventUpdate
    
    # Si hay un usuario nuevo (reciÃ©n registrado)
    if current_user:
        print(f"ðŸŽ¯ Usuario {current_user} detectado en pÃ¡gina de registro")
        
        # Verificar si el usuario existe en la base de datos
        if current_user in USERS_DB:
            user_data = USERS_DB[current_user]
            onboarding_status = user_data.get("onboarding_completed", False)
            
            print(f"ðŸ“Š Estado onboarding de {current_user}: {onboarding_status}")
            
            if not onboarding_status:
                print(f"ðŸŽ¯ Usuario nuevo {current_user} necesita onboarding, redirigiendo...")
                return '/onboarding'
            else:
                print(f"âœ… Usuario {current_user} ya completÃ³ onboarding, redirigiendo a inicio")
                return '/inicio'
    
    print("âš ï¸ No se cumplen condiciones para redirigir")
    raise dash.exceptions.PreventUpdate
    
@app.callback(
    [Output("accept-terms", "value"),
     Output("terms-checkbox-visual", "children"),
     Output("terms-checkbox-visual", "style")],
    [Input("terms-checkbox-visual", "n_clicks")],
    [State("accept-terms", "value")],
    prevent_initial_call=True
)
def toggle_terms_checkbox(n_clicks, current_value):
    """Alterna el checkbox visual de tÃ©rminos"""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    
    if current_value and 'Acepto' in current_value:
        # Desmarcar
        return [], "â˜", {
            'display': 'inline-block',
            'marginLeft': '10px',
            'cursor': 'pointer',
            'fontSize': '1.2rem',
            'color': '#666'
        }
    else:
        # Marcar
        return ['Acepto'], "âœ…", {
            'display': 'inline-block',
            'marginLeft': '10px',
            'cursor': 'pointer',
            'fontSize': '1.2rem',
            'color': HIGHLIGHT_COLOR
        }

# ==========================================================
# CALLBACK CORREGIDO PARA VOLVER AL DASHBOARD MÃ‰DICO
# ==========================================================

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [Input("btn-back-to-doctor-dashboard", "n_clicks")],
    [State("current-user", "data"),
     State("user-type-store", "data"),
     State("url", "pathname")],
    prevent_initial_call=True
)
def handle_back_to_doctor_dashboard_corrected(n_clicks, current_user, user_type, current_path):
    """Maneja la navegaciÃ³n de vuelta al dashboard mÃ©dico - CORREGIDO"""
    
    # Solo ejecutar si hay un clic
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    
    # Verificar que sea mÃ©dico
    if user_type != "doctor":
        raise dash.exceptions.PreventUpdate
    
    print(f"ðŸ‘¨â€âš•ï¸ MÃ©dico {current_user} volviendo a dashboard desde {current_path}")
    
    return '/doctor-dashboard'
    
# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=True, port=8051)


