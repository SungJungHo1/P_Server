from pymongo import MongoClient,ASCENDING
from datetime import datetime, timedelta, timezone

client = MongoClient('mongodb://tjdwjdgh12:asd64026@43.200.229.41', 27017)
mydb = client['P_ServerDB']
UserDatas = mydb['UserDatas']

def Insert_User(id,Password):
    datas =UserDatas.find_one({"UserName":id})
    if datas is None:
        timezone_kst = timezone(timedelta(hours=9))
        datetime_utc2 = datetime.now(timezone_kst)
        AddDays = timedelta(days=10)
        Last_datetime = datetime_utc2 + AddDays
        format = '%Y-%m-%d %H:%M:%S'

        # UserDatas.insert_one({'Start_Day':datetime_utc2,'UserName':"JungHo",'Password':"a","Swichs":True,"End_Days":Last_datetime})
        UserDatas.insert_one({'Start_Day':datetime_utc2,'UserName':str(id),'Password':str(Password),"Swichs":True,"End_Days":Last_datetime,"Level":1})
        
        return True
    else:
        return False

def Find_User(id,Password,Mac):
    datas =UserDatas.find_one({"UserName":id})
    if datas is not None:
        if datas['Password'] == str(Password):
            if 'Mac' in datas:
                if len(datas['Mac']) >= datas["Level"]:
                    if Mac in datas['Mac']:
                        return 1
                    else:
                        return 4

                else:
                    UserDatas.update_one({"UserName":id}, {'$addToSet': {'Mac': Mac}})
                    return 1
            else:
                UserDatas.update_one({"UserName":id}, {'$addToSet': {'Mac': Mac}})
                return 1
        else:
            return 2
    else:
        return 3
    # return datas

def Check_On(id):
    datas =UserDatas.find_one({"UserName":id})
    if datas is not None:
        EndDays = datas["End_Days"]
        now = datetime.now()
        
        if now >= EndDays:
            UserDatas.update_one({"UserName":id},{"$set":{"Swichs":False}})
            return False

        return datas["Swichs"]
    else:
        return False

# UserDatas.update_one({"UserName":"JungHo"},{"$set":{"Swichs":True}})
# print(Insert_User("JungHo","a"))
# print(Find_User("JungH","a"))
# UserDatas.update_one({"UserName":"asd64026"},{"$set":{"Level":3}})
# print(Check_On("asd64026"))
# UserDatas.delete_many({})
# datas =UserDatas.find({})
# for i in datas:
#     print(i)