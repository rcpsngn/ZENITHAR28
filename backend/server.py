from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timedelta, date
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
import bcrypt
import os
from bson import ObjectId

app = FastAPI(title="ZENITHAR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "zenithar_db")
SECRET_KEY = os.getenv("JWT_SECRET", "zenithar-secret-2026")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

security = HTTPBearer()

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str
    company_name: Optional[str] = ""
    phone: Optional[str] = ""

class UserLogin(BaseModel):
    username: str
    password: str

class Employee(BaseModel):
    id: Optional[str] = Field(alias="_id")
    full_name: str
    identity_number: str
    phone: str
    email: Optional[str] = ""
    address: Optional[str] = ""
    position: str
    department: Optional[str] = ""
    hire_date: str
    salary: float
    is_active: bool = True
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class Invoice(BaseModel):
    id: Optional[str] = Field(alias="_id")
    type: str
    invoice_number: str
    customer_name: str
    customer_tax_id: Optional[str] = ""
    customer_address: Optional[str] = ""
    amount: float
    vat_amount: float = 0
    total_amount: float
    vat_rate: float = 20
    status: str = "draft"
    issue_date: str
    due_date: Optional[str] = None
    notes: Optional[str] = ""
    items: List[dict] = []
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["id"] = str(user["_id"])
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
async def root():
    return {"message": "ZENITHAR API", "status": "running"}

@app.post("/api/auth/register/")
async def register(user: UserRegister):
    if user.password != user.password_confirm:
        raise HTTPException(status_code=400, detail="Şifreler eşleşmiyor")
    
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten kullanılıyor")
    
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pw.decode(),
        "company_name": user.company_name,
        "phone": user.phone,
        "role": "viewer",
        "created_at": datetime.now()
    }
    
    result = await db.users.insert_one(user_doc)
    
    await db.subscriptions.insert_one({
        "user_id": str(result.inserted_id),
        "plan": "trial",
        "status": "active",
        "start_date": datetime.now(),
        "end_date": datetime.now() + timedelta(days=7)
    })
    
    token = jwt.encode({
        "user_id": str(result.inserted_id),
        "exp": datetime.utcnow() + timedelta(days=7)
    }, SECRET_KEY, algorithm="HS256")
    
    return {
        "user": {
            "id": str(result.inserted_id),
            "username": user.username,
            "email": user.email,
            "company_name": user.company_name
        },
        "tokens": {
            "access": token,
            "refresh": token
        }
    }

@app.post("/api/auth/login/")
async def login(user: UserLogin):
    db_user = await db.users.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")
    
    if not bcrypt.checkpw(user.password.encode(), db_user["password"].encode()):
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")
    
    token = jwt.encode({
        "user_id": str(db_user["_id"]),
        "exp": datetime.utcnow() + timedelta(days=7)
    }, SECRET_KEY, algorithm="HS256")
    
    return {
        "user": {
            "id": str(db_user["_id"]),
            "username": db_user["username"],
            "email": db_user.get("email", ""),
            "company_name": db_user.get("company_name", ""),
            "role": db_user.get("role", "viewer")
        },
        "tokens": {
            "access": token,
            "refresh": token
        }
    }

@app.get("/api/auth/subscription/")
async def get_subscription(user = Depends(get_current_user)):
    sub = await db.subscriptions.find_one({"user_id": user["id"]})
    if not sub:
        return {"plan": "trial", "status": "active", "end_date": datetime.now() + timedelta(days=7), "is_active": True}
    return {
        "plan": sub.get("plan", "trial"),
        "status": sub.get("status", "active"),
        "end_date": sub.get("end_date"),
        "is_active": sub.get("end_date", datetime.now()) > datetime.now()
    }

@app.get("/api/personnel/employees/")
async def get_employees(user = Depends(get_current_user)):
    employees = await db.employees.find({"user_id": user["id"]}).to_list(1000)
    for emp in employees:
        emp["id"] = str(emp["_id"])
        del emp["_id"]
    return employees

@app.post("/api/personnel/employees/")
async def create_employee(employee: Employee, user = Depends(get_current_user)):
    emp_dict = employee.dict(by_alias=True, exclude={"id"})
    emp_dict["user_id"] = user["id"]
    result = await db.employees.insert_one(emp_dict)
    return {"id": str(result.inserted_id), **emp_dict}

@app.post("/api/personnel/employees/{emp_id}/toggle_active/")
async def toggle_employee(emp_id: str, user = Depends(get_current_user)):
    emp = await db.employees.find_one({"_id": ObjectId(emp_id), "user_id": user["id"]})
    if not emp:
        raise HTTPException(status_code=404, detail="Personel bulunamadı")
    new_status = not emp.get("is_active", True)
    await db.employees.update_one({"_id": ObjectId(emp_id)}, {"$set": {"is_active": new_status}})
    return {"status": "success", "is_active": new_status}

@app.get("/api/personnel/attendance/")
async def get_attendance(user = Depends(get_current_user)):
    attendance = await db.attendance.find({"user_id": user["id"]}).sort("date", -1).to_list(100)
    for att in attendance:
        att["id"] = str(att["_id"])
        del att["_id"]
        emp = await db.employees.find_one({"_id": ObjectId(att["employee_id"])})
        att["employee_name"] = emp["full_name"] if emp else "Unknown"
    return attendance

@app.post("/api/personnel/attendance/quick_entry/")
async def quick_attendance(data: dict, user = Depends(get_current_user)):
    emp_id = data.get("employee")
    att_type = data.get("type", "entry")
    
    await db.attendance.insert_one({
        "employee_id": emp_id,
        "user_id": user["id"],
        "type": att_type,
        "date": date.today().isoformat(),
        "time": datetime.now().strftime("%H:%M:%S"),
        "created_at": datetime.now()
    })
    
    return {"status": "success", "message": "Kayıt eklendi"}

@app.get("/api/personnel/salaries/")
async def get_salaries(user = Depends(get_current_user)):
    salaries = await db.salaries.find({"user_id": user["id"]}).sort("year", -1).to_list(100)
    for sal in salaries:
        sal["id"] = str(sal["_id"])
        del sal["_id"]
        emp = await db.employees.find_one({"_id": ObjectId(sal["employee_id"])})
        sal["employee_name"] = emp["full_name"] if emp else "Unknown"
        months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        sal["month_name"] = months[sal["month"] - 1] if 1 <= sal["month"] <= 12 else str(sal["month"])
    return salaries

@app.post("/api/personnel/salaries/{sal_id}/mark_paid/")
async def mark_salary_paid(sal_id: str, user = Depends(get_current_user)):
    await db.salaries.update_one(
        {"_id": ObjectId(sal_id), "user_id": user["id"]},
        {"$set": {"status": "paid", "payment_date": date.today().isoformat()}}
    )
    return {"status": "success", "message": "Maaş ödendi olarak işaretlendi"}

@app.get("/api/personnel/leaves/")
async def get_leaves(user = Depends(get_current_user)):
    leaves = await db.leaves.find({"user_id": user["id"]}).sort("start_date", -1).to_list(100)
    for leave in leaves:
        leave["id"] = str(leave["_id"])
        del leave["_id"]
        emp = await db.employees.find_one({"_id": ObjectId(leave["employee_id"])})
        leave["employee_name"] = emp["full_name"] if emp else "Unknown"
    return leaves

@app.post("/api/personnel/leaves/{leave_id}/approve/")
async def approve_leave(leave_id: str, user = Depends(get_current_user)):
    await db.leaves.update_one(
        {"_id": ObjectId(leave_id), "user_id": user["id"]},
        {"$set": {"status": "approved"}}
    )
    return {"status": "success", "message": "İzin onaylandı"}

@app.post("/api/personnel/leaves/{leave_id}/reject/")
async def reject_leave(leave_id: str, data: dict, user = Depends(get_current_user)):
    await db.leaves.update_one(
        {"_id": ObjectId(leave_id), "user_id": user["id"]},
        {"$set": {"status": "rejected", "notes": data.get("notes", "")}}
    )
    return {"status": "success", "message": "İzin reddedildi"}

@app.get("/api/invoices/")
async def get_invoices(user = Depends(get_current_user)):
    invoices = await db.invoices.find({"user_id": user["id"]}).sort("issue_date", -1).to_list(1000)
    for inv in invoices:
        inv["id"] = str(inv["_id"])
        del inv["_id"]
    return invoices

@app.post("/api/invoices/")
async def create_invoice(invoice: Invoice, user = Depends(get_current_user)):
    inv_dict = invoice.dict(by_alias=True, exclude={"id"})
    inv_dict["user_id"] = user["id"]
    result = await db.invoices.insert_one(inv_dict)
    return {"id": str(result.inserted_id), **inv_dict}

@app.put("/api/invoices/{inv_id}/")
async def update_invoice(inv_id: str, invoice: Invoice, user = Depends(get_current_user)):
    inv_dict = invoice.dict(by_alias=True, exclude={"id"})
    await db.invoices.update_one(
        {"_id": ObjectId(inv_id), "user_id": user["id"]},
        {"$set": inv_dict}
    )
    return {"id": inv_id, **inv_dict}

@app.delete("/api/invoices/{inv_id}/")
async def delete_invoice(inv_id: str, user = Depends(get_current_user)):
    await db.invoices.delete_one({"_id": ObjectId(inv_id), "user_id": user["id"]})
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
