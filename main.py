from fastapi import FastAPI, File, Form, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from DB_Maker import Insert_User,Find_User,Check_On

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/MakeUser')
def MakeUser(User_ID,PassWord):
    결과 = Insert_User(User_ID,PassWord)
    return 결과

@app.post('/Login')
def Login(User_ID,PassWord):
    결과 = Find_User(User_ID,PassWord)
    return 결과

@app.post('/Check')
def Check(User_ID):
    결과 = Check_On(User_ID)
    return 결과