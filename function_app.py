import azure.functions as func
import logging
import os
import pymssql
import json
from datetime import datetime

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="TestDbConnection")
def TestDbConnection(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('TestDbConnection function triggered.')

    try:
        server = "sqlserver-func-project.database.windows.net"
        database = "free-sql-db-3420554"
        username = "sqladmin"
        password = os.environ.get("SQL_PASSWORD")

        conn = pymssql.connect(server=server, user=username, password=password, database=database, timeout=10)
        cursor = conn.cursor()

        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TestTable' AND xtype='U')
            CREATE TABLE TestTable (id INT IDENTITY PRIMARY KEY, message NVARCHAR(200), created_at DATETIME)
        """)
        conn.commit()

        cursor.execute("INSERT INTO TestTable (message, created_at) VALUES (%s, %s)",
                       ("Hello from private Function App!", datetime.utcnow()))
        conn.commit()

        cursor.execute("SELECT TOP 5 id, message, created_at FROM TestTable ORDER BY id DESC")
        rows = cursor.fetchall()

        result = [{"id": r[0], "message": r[1], "created_at": str(r[2])} for r in rows]

        conn.close()

        return func.HttpResponse(
            json.dumps({"status": "success", "data": result}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            mimetype="application/json",
            status_code=500
        )