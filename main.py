from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
import database as db

app = FastAPI(title="Aventura CRUD")

# Configurar templates i arxius estàtics
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== RUTAS PRINCIPALES ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ==================== LOCALITZACIONS ====================

@app.get("/localitzacions", response_class=HTMLResponse)
async def list_localitzacions(request: Request):
    """Mostra totes les localitzacions"""
    localitzacions = db.execute_query("SELECT * FROM localitzacions ORDER BY id")
    
    # Decodificar el camp blob descripcio de bytes a string
    for loc in localitzacions:
        if loc.get('descripcio') and isinstance(loc['descripcio'], bytes):
            try:
                loc['descripcio'] = loc['descripcio'].decode('utf-8')
            except:
                loc['descripcio'] = ''
    
    return templates.TemplateResponse(
        "localitzacions_list.html", 
        {"request": request, "localitzacions": localitzacions}
    )

@app.get("/localitzacions/nova", response_class=HTMLResponse)
async def nova_localitzacio_form(request: Request):
    """Formulari per crear nova localització"""
    return templates.TemplateResponse("localitzacio_form.html", {"request": request})

@app.post("/localitzacions/nova")
async def crear_localitzacio(
    nom: str = Form(...),
    descripcio: str = Form(""),
    imatge: str = Form("")
):
    """Crea una nova localització"""
    query = """
        INSERT INTO localitzacions (nom, descripcio, imatge) 
        VALUES (%s, %s, %s)
    """
    # Convertir descripció a bytes UTF-8 pel camp blob
    descripcio_bytes = descripcio.encode('utf-8') if descripcio else b''
    db.execute_query(query, (nom, descripcio_bytes, imatge), fetch=False)
    return RedirectResponse(url="/localitzacions", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/localitzacions/{id}/editar", response_class=HTMLResponse)
async def editar_localitzacio_form(request: Request, id: int):
    """Formulari per editar localització"""
    localitzacio = db.execute_single("SELECT * FROM localitzacions WHERE id = %s", (id,))
    
    # Decodificar el camp blob descripció
    if localitzacio and localitzacio.get('descripcio') and isinstance(localitzacio['descripcio'], bytes):
        try:
            localitzacio['descripcio'] = localitzacio['descripcio'].decode('utf-8')
        except:
            localitzacio['descripcio'] = ''
    
    return templates.TemplateResponse(
        "localitzacio_form.html", 
        {"request": request, "localitzacio": localitzacio}
    )

@app.post("/localitzacions/{id}/editar")
async def actualitzar_localitzacio(
    id: int,
    nom: str = Form(...),
    descripcio: str = Form(""),
    imatge: str = Form("")
):
    """Actualitza una localització"""
    query = """
        UPDATE localitzacions 
        SET nom = %s, descripcio = %s, imatge = %s 
        WHERE id = %s
    """
    # Convertir descripció a bytes UTF-8 pel camp blob
    descripcio_bytes = descripcio.encode('utf-8') if descripcio else b''
    db.execute_query(query, (nom, descripcio_bytes, imatge, id), fetch=False)
    return RedirectResponse(url="/localitzacions", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/localitzacions/{id}/eliminar")
async def eliminar_localitzacio(id: int):
    """Elimina una localització"""
    # Verificar si hay camins usando esta localización
    check_query = """
        SELECT COUNT(*) as count FROM camins 
        WHERE localitzacio1 = %s OR localitzacio2 = %s
    """
    result = db.execute_single(check_query, (id, id))
    
    if result['count'] > 0:
        # Si hi ha camins utilitzant aquesta localització, redirigir amb error
        return RedirectResponse(url="/localitzacions", status_code=status.HTTP_303_SEE_OTHER)
    
    db.execute_query("DELETE FROM localitzacions WHERE id = %s", (id,), fetch=False)
    return RedirectResponse(url="/localitzacions", status_code=status.HTTP_303_SEE_OTHER)


# ==================== CAMINS ====================

@app.get("/camins", response_class=HTMLResponse)
async def list_camins(request: Request):
    """Llista tots els camins amb les seves localitzacions"""
    query = """
        SELECT 
            c.id,
            c.nom,
            c.localitzacio1,
            c.localitzacio2,
            l1.nom as nom_localitzacio1,
            l2.nom as nom_localitzacio2
        FROM camins c
        LEFT JOIN localitzacions l1 ON c.localitzacio1 = l1.id
        LEFT JOIN localitzacions l2 ON c.localitzacio2 = l2.id
        ORDER BY c.id
    """
    camins = db.execute_query(query)
    return templates.TemplateResponse(
        "camins_list.html", 
        {"request": request, "camins": camins}
    )

@app.get("/camins/nou", response_class=HTMLResponse)
async def nou_cami_form(request: Request):
    """Formulari per crear nou camí"""
    localitzacions = db.execute_query("SELECT id, nom FROM localitzacions ORDER BY nom")
    return templates.TemplateResponse(
        "cami_form.html", 
        {"request": request, "localitzacions": localitzacions}
    )

@app.post("/camins/nou")
async def crear_cami(
    nom: str = Form(...),
    localitzacio1: int = Form(...),
    localitzacio2: int = Form(...)
):
    """Crea un nou camí"""
    query = """
        INSERT INTO camins (nom, localitzacio1, localitzacio2) 
        VALUES (%s, %s, %s)
    """
    db.execute_query(query, (nom, localitzacio1, localitzacio2), fetch=False)
    return RedirectResponse(url="/camins", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/camins/{id}/editar", response_class=HTMLResponse)
async def editar_cami_form(request: Request, id: int):
    """Formulari per editar camí"""
    cami = db.execute_single("SELECT * FROM camins WHERE id = %s", (id,))
    localitzacions = db.execute_query("SELECT id, nom FROM localitzacions ORDER BY nom")
    return templates.TemplateResponse(
        "cami_form.html", 
        {"request": request, "cami": cami, "localitzacions": localitzacions}
    )

@app.post("/camins/{id}/editar")
async def actualitzar_cami(
    id: int,
    nom: str = Form(...),
    localitzacio1: int = Form(...),
    localitzacio2: int = Form(...)
):
    """Actualitza un camí"""
    query = """
        UPDATE camins 
        SET nom = %s, localitzacio1 = %s, localitzacio2 = %s 
        WHERE id = %s
    """
    db.execute_query(query, (nom, localitzacio1, localitzacio2, id), fetch=False)
    return RedirectResponse(url="/camins", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/camins/{id}/eliminar")
async def eliminar_cami(id: int):
    """Elimina un camí"""
    db.execute_query("DELETE FROM camins WHERE id = %s", (id,), fetch=False)
    return RedirectResponse(url="/camins", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
