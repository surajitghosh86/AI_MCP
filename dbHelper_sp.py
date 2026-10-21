import pyodbc

class ItemDatabase:
    def __init__(self):
        self.connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};Server=SURAJIT-PC\\MSSQLSERVER01;Database=TestDB;Uid=sa;Pwd=Surajit007;Encrypt=yes;TrustServerCertificate=yes;')
        self.cursor = self.connection.cursor()

    def getCustomers(self):
        self.cursor.execute("{CALL GetTestCustomerDetails}")
        items = self.cursor.fetchall()
        
        result = []
        for row in items:
            result.append({
                "Id": row[0],
                "FirstName": row[1],
                "LastName": row[2]
            })
        return result
    
    def getCustomer(self, id):
        self.cursor.execute("{CALL GetTestCustomerDetailsById (?)}", id)
        item = self.cursor.fetchone()
        
        if item:
            return {
                "Id": item[0],
                "FirstName": item[1],
                "LastName": item[2]
            }
        else:
            return None
    
    def createCustomer(self, data):
        self.cursor.execute("{CALL AddTestCustomerDetails (?, ?)}", (f"{data['FirstName']}", f"{data['LastName']}"))
        self.connection.commit()
        return {"message": "Item created successfully"}
    
    def updateCustomer(self, id, data):
        val = self.getCustomer(id)
        if val:
            self.cursor.execute("{CALL UpdateTestCustomerDetails (?, ?, ?)}", (id, f"{data['FirstName']}", f"{data['LastName']}"))
            self.connection.commit()
            return {"message": "Item updated successfully"}
        else:
            return {"message": "Data not found"}
    
    def deleteCustomer(self, id):
        val = self.getCustomer(id)
        if val:
            self.cursor.execute("{CALL DeleteTestCustomerDetails (?)}", id)
            self.connection.commit()
            return {"message": "Item deleted successfully"}
        else:
            return {"message": "Data not found"}

    def getPatientInfoDetails(self):
            self.cursor.execute("{CALL GetTestPatientInfoDetails}")
            items = self.cursor.fetchall()
            
            result = []
            for row in items:
                result.append({
                    "LeadNumber": row[0],
                    "FirstName": row[1],
                    "LastName": row[2],
                    "DOB": row[3],
                    "BedStatus": row[4],
                    "PatientStatus": row[5],
                    "PatientType": row[6],
                    "IVRStatus": row[7],
                    "MedicalGroup": row[8]
                })
            return result

# db = ItemDatabase()
# print(db.getCustomers())  # Example usage to fetch all items
