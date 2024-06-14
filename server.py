import os
import sys
from fastapi import FastAPI, Request
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, HTMLResponse, JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates

from db import get_round_list, get_match_json, get_match_results_list, get_config_yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

templates = Jinja2Templates(directory='templates')


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/submissions')
async def submissions(request: Request):
    submissions=get_round_list()
    return templates.TemplateResponse('submissions.html', {'request': request, 'submissions': submissions})


@app.get('/config')
async def config(id:str = ''):
    if len(id) > 0:
        logger.info(f'request config id={id}')
        res = get_config_yaml(id)
        return PlainTextResponse(content=res, status_code=200)
    
    raise HTTPException(status_code=404)

@app.get('/matches')
async def matches(request: Request, id:str=''):
    query_params = request.query_params
    if len(id) > 0:
        logger.info(f'request match id={id}')
        res = get_match_results_list(id)
        return templates.TemplateResponse("matches.html", {'request': request, "results": res})
    
    return HTMLResponse(content="-", status_code=200)


@app.get("/visualizer")
async def visualizer(request: Request):
    return FileResponse("visualizer/test.html")

@app.get('/game.json')
async def game(request: Request):
    logger.info(f'game.json')
    referer = request.headers.get('Referer', '')
    result_id = referer.split('?')[-1].split('id=')[-1]
    logger.info(f'request game id={result_id}')
    j = get_match_json(result_id)
    logger.info(j)
    if j is not None:
        resp = PlainTextResponse(content=j, media_type='application/json')
    else:
        resp = FileResponse('visualizer/game.json')
    resp.headers.append('Cache-Control', 'max-age=0')
    resp.headers.append('Expires', '-1')
    return resp

@app.get('/assets/assets/{file_path:path}')
async def static_files_assets_dup(request: Request, file_path: str):
    path = f'visualizer/assets/{file_path}'
    if os.path.exists(path) == False:
        return HTTPException(404)
    return FileResponse(path)

@app.get('/assets/{file_path:path}')
async def static_files_assets(request: Request, file_path: str):
    path = f'visualizer/assets/{file_path}'
    if os.path.exists(path) == False:
        return HTTPException(404)
    return FileResponse(path)

@app.get('/{file_path:path}')
async def static_files(request: Request, file_path: str):
    logger.info(file_path)
    if file_path == 'game.json':
        return game(request)
    path = f'visualizer/{file_path}'
    if os.path.exists(path) == False:
        return HTTPException(404)
    return FileResponse(path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)