from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from DB_Maker import Check_On
from pydantic import BaseModel
app = FastAPI()

# MongoDB 클라이언트 설정
client = MongoClient('mongodb://tjdwjdgh12:asd64026@43.200.229.41', 27017)
mydb = client['P_ServerDB']
UserDatas = mydb['UserDatas']

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 사용자 로그인 세션을 저장할 딕셔너리
user_sessions = {}

# 사용자 추가 함수
def insert_user(id, password):
    existing_user = UserDatas.find_one({"UserName": id})
    if existing_user:
        return False, "User already exists."
    
    timezone_kst = timezone(timedelta(hours=9))
    datetime_utc2 = datetime.now(timezone_kst)
    add_days = timedelta(days=10)
    last_datetime = datetime_utc2 + add_days

    user_data = {
        'Start_Day': datetime_utc2,
        'UserName': str(id),
        'Password': str(password),
        'Swichs': True,
        'End_Days': last_datetime,
        'Device_Count':5,
        'Level': 1
    }
    
    UserDatas.insert_one(user_data)
    return True, "User added successfully."

# 사용자 찾기 함수
def find_user(id, password, mac):
    user_data = UserDatas.find_one({"UserName": id})
    if user_data:
        if user_data['Password'] == str(password):
            if 'Mac' in user_data:
                if len(user_data['Mac']) >= user_data["Level"]:
                    if mac in user_data['Mac']:
                        return 1
                    else:
                        return 4

                else:
                    UserDatas.update_one({"UserName": id}, {'$addToSet': {'Mac': mac}})
                    return 1
            else:
                UserDatas.update_one({"UserName": id}, {'$addToSet': {'Mac': mac}})
                return 1
        else:
            return 2
    else:
        return 3
@app.post('/login')
def make_user(id, password):
    state,text = insert_user(id, password)
    return state, text

# 로그인 상태 확인 함수
def check_login_status(id):
    user_data = UserDatas.find_one({"UserName": id})
    if user_data:
        end_days = user_data["End_Days"]
        now = datetime.now()
        
        if now >= end_days:
            UserDatas.update_one({"UserName": id}, {"$set": {"Swichs": False}})
            return False

        return user_data["Swichs"]
    else:
        return False

class LoginRequest(BaseModel):
    user_id: str
    password: str
    mac: str
class Ses(BaseModel):
    user_id: str

# 사용자 로그인 라우트
@app.post('/login')
def login(req: LoginRequest):
    
    # 사용자를 찾고 로그인을 시도합니다.
    login_result = find_user(req.user_id, req.password, req.mac)
    
    
    if login_result == 1:
        # 로그인이 성공했을 경우 세션을 생성하고 성공 메시지를 반환합니다.
        user_sessions[req.user_id] = req.mac
        return {"authenticated": True, "message": "Login successful."}
    elif login_result == 2:
        # 비밀번호가 일치하지 않는 경우
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    elif login_result == 3:
        # 사용자가 존재하지 않는 경우
        raise HTTPException(status_code=404, detail="User not found.")
    elif login_result == 4:
        # 기기가 등록되지 않은 경우
        raise HTTPException(status_code=403, detail="Unauthorized device.")

# 사용자 로그아웃 라우트
@app.post('/logout')
def logout(req:Ses):
    # 사용자 로그아웃 처리: 세션에서 사용자 정보 제거
    if req.user_id in user_sessions:
        del user_sessions[req.user_id]
        return {"message": "Logged out successfully."}
    else:
        raise HTTPException(status_code=404, detail="User not found.")

# 세션 확인 라우트
@app.post('/check_session')
def check_session(req: Ses):
    # 세션 확인
    if req.user_id in user_sessions:
        return {"session_valid": True, "message": "Session is valid."}
    else:
        return {"session_valid": False, "message": "Session is invalid."}

@app.post('/Check')
def Check(User_ID):
    결과 = Check_On(User_ID)
    return 결과