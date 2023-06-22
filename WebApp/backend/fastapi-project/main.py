from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from typing import Dict

app = FastAPI(title="LTB Cases API",
              description="API to access and update DB of all Ontario Landlord and Tenant Board decisions")

# Enable CORS
origins = [
    "http://localhost:3000",  # Replace with your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Database configuration
DATABASE = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'cases',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.get("/api/", tags=["Case Operations"])
async def get_cases():
    # Establish a new database connection
    connection = pymysql.connect(**DATABASE)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM cases")
        result = cursor.fetchall()

    # Close the database connection
    connection.close()

    return result

@app.get("/api/{case_id}", tags=["Case Operations"])
async def get_case_by_id(case_id: int):
    # Establish a new database connection
    connection = pymysql.connect(**DATABASE)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM cases WHERE id=%s", (case_id,))
        result = cursor.fetchone()

    # Close the database connection
    connection.close()

    if result is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return result

@app.put("/api/{case_id}", tags=["Case Operations"])
async def update_case_by_id(case_id: int, case_details: Dict):
    # Establish a new database connection
    connection = pymysql.connect(**DATABASE)

    with connection.cursor() as cursor:
        # Construct the SQL query
        sql = "UPDATE cases SET " + ", ".join([f"{key} = %s" for key in case_details.keys()]) + " WHERE id = %s"

        # Execute the query with the values
        cursor.execute(sql, list(case_details.values()) + [case_id])

        # Commit the transaction
        connection.commit()

    # Close the database connection
    connection.close()

    return {"message": "Case updated successfully"}