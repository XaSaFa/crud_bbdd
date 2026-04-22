from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
import database as db

app = FastAPI(title="Aventura CRUD")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== RUTES PRINCIPALS ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ==================== LOCALITZACIONS ====================

@app.get("/localitzacions", response_class=HTMLResponse)
async def list_localitzacions(request: Request):
    localitzacions = db.execute_query("SELECT * FROM localitzacions ORDER BY id")
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
    return templates.TemplateResponse("localitzacio_form.html", {"request": request})

@app.post("/localitzacions/nova")
async def crear_localitzacio(
    nom: str = Form(...),
    descripcio: str = Form(""),
    imatge: str = Form("")
):
    query = "INSERT INTO localitzacions (nom, descripcio, imatge) VALUES (%s, %s, %s)"
    descripcio_bytes = descripcio.encode('utf-8') if descripcio else b''
    db.execute_query(query, (nom, descripcio_bytes, imatge), fetch=False)
    return RedirectResponse(url="/localitzacions", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/localitzacions/{id}/editar", response_class=HTMLResponse)
async def editar_localitzacio_form(request: Request, id: int):
    localitzacio = db.execute_single("SELECT * FROM localitzacions WHERE id = %s", (id,))
    if localitzacio and isinstance(localitzacio.get('descripcio'), bytes):
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
    query = "UPDATE localitzacions SET nom = %s, descripcio = %s, imatge = %s WHERE id = %s"
    descripcio_bytes = descripcio.encode('utf-8') if descripcio else b''
    db.execute_query(query, (nom, descripcio_bytes, imatge, id), fetch=False)
    return RedirectResponse(url="/localitzacions", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/localitzacions/{id}/eliminar")
async def eliminar_localitzacio(id: int):
    check_query = "SELECT COUNT(*) as count FROM camins WHERE localitzacio1 = %s OR localitzacio2 = %s"
    result = db.execute_single(check_query, (id, id))
    if result['count'] > 0:
        return RedirectResponse(url="/localitzacions", status_code=status.HTTP_303_SEE_OTHER)
    db.execute_query("DELETE FROM localitzacions WHERE id = %s", (id,), fetch=False)
    return RedirectResponse(url="/localitzacions", status_code=status.HTTP_303_SEE_OTHER)


# ==================== CAMINS ====================

@app.get("/camins", response_class=HTMLResponse)
async def list_camins(request: Request):
    query = """
        SELECT
            c.id, c.nom1, c.nom2, c.localitzacio1, c.localitzacio2, c.tancat,
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
    localitzacions = db.execute_query("SELECT id, nom FROM localitzacions ORDER BY nom")
    return templates.TemplateResponse(
        "cami_form.html",
        {"request": request, "localitzacions": localitzacions}
    )

@app.post("/camins/nou")
async def crear_cami(
    nom1: str = Form(...),
    nom2: str = Form(...),
    localitzacio1: int = Form(...),
    localitzacio2: int = Form(...),
    tancat: str = Form("off")
):
    query = "INSERT INTO camins (nom1, nom2, localitzacio1, localitzacio2, tancat) VALUES (%s, %s, %s, %s, %s)"
    db.execute_query(query, (nom1, nom2, localitzacio1, localitzacio2, tancat == "on"), fetch=False)
    return RedirectResponse(url="/camins", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/camins/{id}/editar", response_class=HTMLResponse)
async def editar_cami_form(request: Request, id: int):
    cami = db.execute_single("SELECT * FROM camins WHERE id = %s", (id,))
    localitzacions = db.execute_query("SELECT id, nom FROM localitzacions ORDER BY nom")
    return templates.TemplateResponse(
        "cami_form.html",
        {"request": request, "cami": cami, "localitzacions": localitzacions}
    )

@app.post("/camins/{id}/editar")
async def actualitzar_cami(
    id: int,
    nom1: str = Form(...),
    nom2: str = Form(...),
    localitzacio1: int = Form(...),
    localitzacio2: int = Form(...),
    tancat: str = Form("off")
):
    query = "UPDATE camins SET nom1=%s, nom2=%s, localitzacio1=%s, localitzacio2=%s, tancat=%s WHERE id=%s"
    db.execute_query(query, (nom1, nom2, localitzacio1, localitzacio2, tancat == "on", id), fetch=False)
    return RedirectResponse(url="/camins", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/camins/{id}/eliminar")
async def eliminar_cami(id: int):
    db.execute_query("DELETE FROM camins WHERE id = %s", (id,), fetch=False)
    return RedirectResponse(url="/camins", status_code=status.HTTP_303_SEE_OTHER)


# ==================== OBJECTES ====================

def decode_descripcio(obj):
    if obj and isinstance(obj.get('descripcio'), bytes):
        try:
            obj['descripcio'] = obj['descripcio'].decode('utf-8')
        except:
            obj['descripcio'] = ''
    return obj

@app.get("/objectes", response_class=HTMLResponse)
async def list_objectes(request: Request):
    query = """
        SELECT
            o.id, o.nom, o.descripcio, o.imatge,
            o.localitzacio_id, o.pos_x, o.pos_y,
            o.agafable, o.usos,
            l.nom as nom_localitzacio
        FROM objectes o
        LEFT JOIN localitzacions l ON o.localitzacio_id = l.id
        ORDER BY o.id
    """
    objectes = [decode_descripcio(o) for o in db.execute_query(query)]
    return templates.TemplateResponse(
        "objectes_list.html",
        {"request": request, "objectes": objectes}
    )

@app.get("/objectes/nou", response_class=HTMLResponse)
async def nou_objecte_form(request: Request):
    localitzacions = db.execute_query("SELECT id, nom FROM localitzacions ORDER BY nom")
    return templates.TemplateResponse(
        "objecte_form.html",
        {"request": request, "localitzacions": localitzacions}
    )

@app.post("/objectes/nou")
async def crear_objecte(
    nom: str = Form(...),
    descripcio: str = Form(""),
    imatge: str = Form(""),
    localitzacio_id: str = Form(""),
    pos_x: float = Form(50.0),
    pos_y: float = Form(50.0),
    agafable: str = Form("off"),
    usos: int = Form(-1),
    mida: float = Form(100.0)
):
    query = """
        INSERT INTO objectes (nom, descripcio, imatge, localitzacio_id, pos_x, pos_y, agafable, usos, mida)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    descripcio_bytes = descripcio.encode('utf-8') if descripcio else b''
    loc_id = int(localitzacio_id) if localitzacio_id else None
    db.execute_query(query, (nom, descripcio_bytes, imatge, loc_id, pos_x, pos_y, agafable == "on", usos, mida), fetch=False)
    return RedirectResponse(url="/objectes", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/objectes/{id}/editar", response_class=HTMLResponse)
async def editar_objecte_form(request: Request, id: int):
    objecte = decode_descripcio(db.execute_single("SELECT * FROM objectes WHERE id = %s", (id,)))
    localitzacions = db.execute_query("SELECT id, nom FROM localitzacions ORDER BY nom")
    return templates.TemplateResponse(
        "objecte_form.html",
        {"request": request, "objecte": objecte, "localitzacions": localitzacions}
    )

@app.post("/objectes/{id}/editar")
async def actualitzar_objecte(
    id: int,
    nom: str = Form(...),
    descripcio: str = Form(""),
    imatge: str = Form(""),
    localitzacio_id: str = Form(""),
    pos_x: float = Form(50.0),
    pos_y: float = Form(50.0),
    agafable: str = Form("off"),
    usos: int = Form(-1),
    mida: float = Form(100.0)
):
    query = """
        UPDATE objectes
        SET nom=%s, descripcio=%s, imatge=%s, localitzacio_id=%s,
            pos_x=%s, pos_y=%s, agafable=%s, usos=%s, mida=%s
        WHERE id=%s
    """
    descripcio_bytes = descripcio.encode('utf-8') if descripcio else b''
    loc_id = int(localitzacio_id) if localitzacio_id else None
    db.execute_query(query, (nom, descripcio_bytes, imatge, loc_id, pos_x, pos_y, agafable == "on", usos, mida, id), fetch=False)
    return RedirectResponse(url="/objectes", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/objectes/{id}/eliminar")
async def eliminar_objecte(id: int):
    db.execute_query("DELETE FROM objectes WHERE id = %s", (id,), fetch=False)
    return RedirectResponse(url="/objectes", status_code=status.HTTP_303_SEE_OTHER)


# ==================== COMBINACIONS ====================

@app.get("/combinacions", response_class=HTMLResponse)
async def list_combinacions(request: Request):
    query = """
        SELECT
            c.id,
            oa.nom as nom_a, oa.id as objecte_a,
            ob.nom as nom_b, ob.id as objecte_b,
            or_.nom as nom_resultat, or_.id as resultat_id
        FROM combinacions c
        JOIN objectes oa  ON c.objecte_a   = oa.id
        JOIN objectes ob  ON c.objecte_b   = ob.id
        JOIN objectes or_ ON c.resultat_id = or_.id
        ORDER BY c.id
    """
    combinacions = db.execute_query(query)
    return templates.TemplateResponse(
        "combinacions_list.html",
        {"request": request, "combinacions": combinacions}
    )

@app.get("/combinacions/nova", response_class=HTMLResponse)
async def nova_combinacio_form(request: Request):
    objectes = db.execute_query("SELECT id, nom FROM objectes ORDER BY nom")
    return templates.TemplateResponse(
        "combinacio_form.html",
        {"request": request, "objectes": objectes}
    )

@app.post("/combinacions/nova")
async def crear_combinacio(
    objecte_a: int = Form(...),
    objecte_b: int = Form(...),
    resultat_id: int = Form(...)
):
    query = "INSERT INTO combinacions (objecte_a, objecte_b, resultat_id) VALUES (%s, %s, %s)"
    db.execute_query(query, (objecte_a, objecte_b, resultat_id), fetch=False)
    return RedirectResponse(url="/combinacions", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/combinacions/{id}/editar", response_class=HTMLResponse)
async def editar_combinacio_form(request: Request, id: int):
    combinacio = db.execute_single("SELECT * FROM combinacions WHERE id = %s", (id,))
    objectes = db.execute_query("SELECT id, nom FROM objectes ORDER BY nom")
    return templates.TemplateResponse(
        "combinacio_form.html",
        {"request": request, "combinacio": combinacio, "objectes": objectes}
    )

@app.post("/combinacions/{id}/editar")
async def actualitzar_combinacio(
    id: int,
    objecte_a: int = Form(...),
    objecte_b: int = Form(...),
    resultat_id: int = Form(...)
):
    query = "UPDATE combinacions SET objecte_a=%s, objecte_b=%s, resultat_id=%s WHERE id=%s"
    db.execute_query(query, (objecte_a, objecte_b, resultat_id, id), fetch=False)
    return RedirectResponse(url="/combinacions", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/combinacions/{id}/eliminar")
async def eliminar_combinacio(id: int):
    db.execute_query("DELETE FROM combinacions WHERE id = %s", (id,), fetch=False)
    return RedirectResponse(url="/combinacions", status_code=status.HTTP_303_SEE_OTHER)


# ==================== INTERACCIONS ====================

@app.get("/interaccions", response_class=HTMLResponse)
async def list_interaccions(request: Request):
    query = """
        SELECT
            i.id,
            o.nom  as nom_objecte,  i.objecte_id,
            i.target_tipus,         i.target_id,
            i.resultat_tipus,       i.resultat_id,
            i.resultat_missatge,    i.consumeix,
            CASE
                WHEN i.target_tipus = 'cami'    THEN c.nom1
                WHEN i.target_tipus = 'objecte' THEN ot.nom
            END as nom_target,
            or_.nom as nom_resultat
        FROM interaccions i
        JOIN objectes o ON i.objecte_id = o.id
        LEFT JOIN camins c   ON i.target_tipus = 'cami'    AND i.target_id = c.id
        LEFT JOIN objectes ot ON i.target_tipus = 'objecte' AND i.target_id = ot.id
        LEFT JOIN objectes or_ ON i.resultat_id = or_.id
        ORDER BY i.id
    """
    interaccions = db.execute_query(query)
    return templates.TemplateResponse(
        "interaccions_list.html",
        {"request": request, "interaccions": interaccions}
    )

@app.get("/interaccions/nova", response_class=HTMLResponse)
async def nova_interaccio_form(request: Request):
    objectes = db.execute_query("SELECT id, nom FROM objectes ORDER BY nom")
    camins   = db.execute_query("SELECT id, nom1, nom2 FROM camins ORDER BY id")
    return templates.TemplateResponse(
        "interaccio_form.html",
        {"request": request, "objectes": objectes, "camins": camins}
    )

@app.post("/interaccions/nova")
async def crear_interaccio(
    objecte_id: int = Form(...),
    target_tipus: str = Form(...),
    target_id: int = Form(...),
    resultat_tipus: str = Form(...),
    resultat_id: str = Form(""),
    resultat_missatge: str = Form(""),
    consumeix: str = Form("off")
):
    query = """
        INSERT INTO interaccions
            (objecte_id, target_tipus, target_id, resultat_tipus, resultat_id, resultat_missatge, consumeix)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    res_id = int(resultat_id) if resultat_id else None
    db.execute_query(query, (objecte_id, target_tipus, target_id, resultat_tipus, res_id, resultat_missatge, consumeix == "on"), fetch=False)
    return RedirectResponse(url="/interaccions", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/interaccions/{id}/editar", response_class=HTMLResponse)
async def editar_interaccio_form(request: Request, id: int):
    interaccio = db.execute_single("SELECT * FROM interaccions WHERE id = %s", (id,))
    objectes   = db.execute_query("SELECT id, nom FROM objectes ORDER BY nom")
    camins     = db.execute_query("SELECT id, nom1, nom2 FROM camins ORDER BY id")
    return templates.TemplateResponse(
        "interaccio_form.html",
        {"request": request, "interaccio": interaccio, "objectes": objectes, "camins": camins}
    )

@app.post("/interaccions/{id}/editar")
async def actualitzar_interaccio(
    id: int,
    objecte_id: int = Form(...),
    target_tipus: str = Form(...),
    target_id: int = Form(...),
    resultat_tipus: str = Form(...),
    resultat_id: str = Form(""),
    resultat_missatge: str = Form(""),
    consumeix: str = Form("off")
):
    query = """
        UPDATE interaccions
        SET objecte_id=%s, target_tipus=%s, target_id=%s,
            resultat_tipus=%s, resultat_id=%s, resultat_missatge=%s, consumeix=%s
        WHERE id=%s
    """
    res_id = int(resultat_id) if resultat_id else None
    db.execute_query(query, (objecte_id, target_tipus, target_id, resultat_tipus, res_id, resultat_missatge, consumeix == "on", id), fetch=False)
    return RedirectResponse(url="/interaccions", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/interaccions/{id}/eliminar")
async def eliminar_interaccio(id: int):
    db.execute_query("DELETE FROM interaccions WHERE id = %s", (id,), fetch=False)
    return RedirectResponse(url="/interaccions", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
