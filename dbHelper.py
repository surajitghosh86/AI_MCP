import pyodbc

class ItemDatabase:
    def __init__(self):
        self.connection = pyodbc.connect('DRIVER={SQL SERVER};Server=SURAJIT-PC\\MSSQLSERVER01;Database=TestDB;Uid=sa;Pwd=Surajit007;')
        self.cursor = self.connection.cursor()
        
    def getCustomers(self):
        query = "SELECT * FROM TestCustomer"
        self.cursor.execute(query)
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
        query = f"SELECT * FROM TestCustomer WHERE Id = {id}"
        self.cursor.execute(query)
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
        query = f"INSERT INTO TestCustomer (FirstName, LastName) VALUES ('{data['FirstName']}', '{data['LastName']}')"
        self.cursor.execute(query)
        self.connection.commit()
        return {"message": "Item created successfully"}
    
    def updateCustomer(self, id, data):
        val = self.getCustomer(id)
        if val:
            query = f"UPDATE TestCustomer SET FirstName = '{data['FirstName']}', LastName = '{data['LastName']}' WHERE Id = {id}"
            self.cursor.execute(query)
            self.connection.commit()
            return {"message": "Item updated successfully"}
        else:
            return {"message": "Data not found"}
    
    def deleteCustomer(self, id):
        val = self.getCustomer(id)
        if val:
            query = f"DELETE FROM TestCustomer WHERE Id = {id}"
            self.cursor.execute(query)
            self.connection.commit()
            return {"message": "Item deleted successfully"}
        else:
            return {"message": "Data not found"}

# db = ItemDatabase()
# print(db.getCustomers())  # Example usage to fetch all items




















