import sqlite3
import json
import pandas as pd


class database:
    def __init__(self,dbName):
        self.connection = sqlite3.connect(dbName)
        self.cursor=self.connection.cursor()
        self.createTable('users',{
            'id':'int unique',
            'username':'varchar(60)',
            'firstName':'varchar(60)',
            'lastName':'varchar(60)',
            'checked':'bit default 0'
            })
        self.createTable('leads',{
            'id':'bigint unique',
            'phone':'varchar(60)',
            'interested':'bit default 0'
        })



    def disconnect(self):
        self.connection.close()

    def createTable(self,tableName:str,columns:dict):
        '''        
            Creates new table in the database
            Parameters:
                tableName:str - table name
                columns:dict - dictonary contains the columns:
                {column name:column type, ...}
        '''
        mycursor = self.connection.cursor()
        quary = 'CREATE TABLE IF NOT EXISTS '+tableName+' ('
        for key,value in columns.items():
            if quary[-1]=='(':
                quary += key+' '+value
            else:
                quary += ', '+key+' '+value
        quary +=')'

        mycursor.execute(quary)

    def dropTable(self,tableName:str):
        '''
            drops tableName table
            Parameters:
                tableName:str - table to drop
        '''
        mycursor = self.connection.cursor()
        mycursor.execute('DROP TABLE '+tableName)

    def addColumn(self,tableName:str, columnName:str, columnType:str):
        '''
            add column to a table
            Parameters:
            tableName:str - table name
            columnName:str - column to add
            columnType:str - column type
        '''
        mycursor = self.connection.cursor()
        mycursor.execute(f"ALTER TABLE {tableName} ADD COLUMN {columnName} {columnType}")
        self.connection.commit()


    def insert(self,table:str,values:dict):
        mycursor = self.connection.cursor()
        columns = ', '.join(values.keys())
        placeHolhers = ', '.join(map(lambda x:'?', values.values()))
        values = tuple(values.values())
        sql = f"REPLACE INTO {table} ({columns}) VALUES ({placeHolhers})"
        mycursor.execute(sql,values)
        self.connection.commit()

    def insertAll(self,table:str,values:list):
        mycursor = self.connection.cursor()
        columns = ', '.join(values.pop().keys())
        placeHolhers = ', '.join(map(lambda x:'?', values.pop().values()))
        values = [tuple(i.values()) for i in values]
        sql = f"REPLACE INTO {table} ({columns}) VALUES ({placeHolhers})"
        mycursor.executemany(sql,values)
        self.connection.commit()

    def insertIgnoreAll(self,table:str,values:list):
        mycursor = self.connection.cursor()
        columns = ', '.join(values.pop().keys())
        placeHolhers = ', '.join(map(lambda x:'?', values.pop().values()))
        values = [tuple(i.values()) for i in values]
        sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeHolhers})"
        mycursor.executemany(sql,values)
        self.connection.commit()


    def insertOrUpdate(self,tableName:str,data:dict, idField='id'):
        '''
            insert or update data:dict into tableName:str\n
            Parameters:\n
            tableName:str - table name\n
            data:dict - dictonary contains data to insert {columnName: data,...}\n
            Returns:\n
            inserted row id
        '''
        for key,val in data.items():
            if type(val) == dict:
                data[key] = json.dumps(val)
            
        mycursor = self.connection.cursor()
        columns = ', '.join(data.keys())
        placeHolhers = ', '.join(['?' for i in data.values()])
        updateParams = ', '.join([f'{x} = ?' for x in data.keys()])
        values = tuple(data.values())
        values2 = tuple(data.values())+tuple([data[idField],])
        sql = f"INSERT OR IGNORE INTO {tableName} ({columns}) VALUES ({placeHolhers})"
        mycursor.execute(sql,values)
        sql2 = f'UPDATE {tableName} SET {updateParams} WHERE {idField} = ?'
        print(sql2,values2)
        mycursor.execute(sql2,values2)

        self.connection.commit()
        return mycursor.lastrowid

    def update(self,tableName:str,colVals:dict,where:dict):
        mycursor = self.connection.cursor()
        wheres = [f'{x}=?' for x,y in where.items()]
        whereStr = ' AND '.join(wheres)
        updates = ', '.join([f'{key} = {value}' for key,value in colVals.items()])
        sql = f'UPDATE {tableName} SET {updates} WHERE {whereStr}'
        mycursor.execute(sql,tuple(where.values()))
        self.connection.commit()
        return mycursor.lastrowid

    def selectAll(self,tableName:str):
        '''
            selects all rows and fields from table tableName
            Returns: list of dictionaries
        '''
        mycursor = self.connection.cursor()
        sql = f"SELECT * FROM {tableName}"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        colNames = list(map(lambda c:c['Field'],self.listColumns(tableName)))
        resarr = list(map(lambda r:dict(zip(colNames,r)),myresult))
        self.connection.commit()
        return resarr

    def selectLimit(self,tableName:str,limit):
        '''
            selects all rows and fields from table tableName
            Returns: list of dictionaries
        '''
        mycursor = self.connection.cursor()
        sql = f"SELECT * FROM {tableName} LIMIT {limit}"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        colNames = list(map(lambda c:c['Field'],self.listColumns(tableName)))
        resarr = list(map(lambda r:dict(zip(colNames,r)),myresult))
        self.connection.commit()
        return resarr

    def selectWhere(self,tableName:str,colsVals:dict):
        '''
            selects from tableName rows where value of colsVals.key is colsVals.value \n
            Returns: list of dictionaries
            Parameters:
                tableName:str - table name
                colsVals:dict - dictonary contains the columns and values:
                {column name:value, ...}
        '''
        mycursor = self.connection.cursor()
        keys = list(map(lambda a:str(a)+' = ?',colsVals.keys()))
        keystr = ' AND '.join(keys)
        sql = f"SELECT * FROM {tableName} WHERE "+keystr
        values = tuple(colsVals.values())
        mycursor.execute(sql,values)
        myresult = mycursor.fetchall()
        colNames = list(map(lambda c:c['Field'],self.listColumns(tableName)))
        resarr = list(map(lambda r:dict(zip(colNames,r)),myresult))
        self.connection.commit()
        return resarr

    def selectWhereLimit(self,tableName:str,colsVals:dict,limit:int):
        '''
            selects from tableName rows where value of colsVals.key is colsVals.value \n
            Returns: list of dictionaries
            Parameters:
                tableName:str - table name
                colsVals:dict - dictonary contains the columns and values:
                {column name:value, ...}
        '''
        mycursor = self.connection.cursor()
        keys = list(map(lambda a:str(a)+' = ?',colsVals.keys()))
        keystr = ' AND '.join(keys)
        sql = f"SELECT * FROM {tableName} WHERE {keystr} LIMIT {limit}"
        values = tuple(colsVals.values())
        mycursor.execute(sql,values)
        myresult = mycursor.fetchall()
        colNames = list(map(lambda c:c['Field'],self.listColumns(tableName)))
        resarr = list(map(lambda r:dict(zip(colNames,r)),myresult))
        self.connection.commit()
        return resarr


    def selectAllOrderBy(self,tableName,order):
        '''
            selects all rows and fields from table tableName
            Returns: list of dictionaries
        '''
        mycursor = self.connection.cursor()
        sql = f"SELECT * FROM {tableName} ORDER BY {order}"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        colNames = list(map(lambda c:c['Field'],self.listColumns(tableName)))
        resarr = list(map(lambda r:dict(zip(colNames,r)),myresult))
        self.connection.commit()
        return resarr

    def selectJoin(self,table1,table2,on:tuple):
        """select join

        Args:
            table1 (str): first table name
            table2 (str): second table name
            on (tuple): tuple holding the first table field and the second table field to join
        """
        mycursor = self.connection.cursor()
        sql = f'SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{on[0]} = {table2}.{on[1]}'
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        colNames = list(map(lambda c:c['Field'],self.listColumns(table1)+self.listColumns(table2)))
        resarr = list(map(lambda r:dict(zip(colNames,r)),myresult))
        self.connection.commit()
        return resarr

    def selectLeftJoin(self,table1,table2,on):
        """select join

        Args:
            table1 (str): first table name
            table2 (str): second table name
            on (tuple): tuple holding the first table field and the second table field to join
        """
        table1Cols = [i['Field'] for i in self.listColumns(table1)]
        table2Cols = [i['Field'] for i in self.listColumns(table2)]
        table2Cols=[(i+'_'+table2 if i in table1Cols else i )for i in table2Cols]
        # print(table1Cols,table2Cols)
        columns = [f'{table1}.{col} AS' for col in self.listColumns(table1)]
        mycursor = self.connection.cursor()
        sql = f'SELECT * FROM {table1} LEFT JOIN {table2} ON {table1}.{on[0]} = {table2}.{on[1]}'
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        colNames = table1Cols+table2Cols
        resarr = list(map(lambda r:dict(zip(colNames,r)),myresult))
        self.connection.commit()
        return resarr

    def selectColumnsOrderBy(self,tableName,columns,order):
        '''
            selects all rows and fields from table tableName
            Returns: list of dictionaries
        '''
        mycursor = self.connection.cursor()
        cols = ','.join(columns)
        sql = f"SELECT {cols} FROM {tableName} ORDER BY {order}"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        resarr = list(map(lambda r:dict(zip(columns,r)),myresult))
        self.connection.commit()
        return resarr

    def runQuary(self,quary):
        mycursor = self.connection.cursor()
        mycursor.execute(quary)
        myresult = mycursor.fetchall()
        self.connection.commit()
        return myresult



    def listColumns(self,tableName:str):
        '''
            lists all columns in tableName:str
            Returns: 
                list of dictionaries
        '''
        mycursor = self.connection.cursor()
        mycursor.execute(f"PRAGMA table_info([{tableName}])")
        
        cols = []
        keys = ('index','Field','Type','Null','Key','Default','Extra')
        for x in mycursor:
            cols.append(dict(zip(keys,x)))
        return cols


if __name__=='__main__':
    db = database('users.db')
    # db.createTable('users',{'id':'int unique','username':'varchar(60)','firstName':'varchar(60)','lastName':'varchar(60)'})
    # users = db.runQuary('SELECT users.id AS id, users.username AS name, leads.phone AS phone FROM users INNER JOIN leads ON users.id = leads.id')
    # users = pd.DataFrame(db.selectLeftJoin('users','leads',('id','id')))
    # db.update('users',{'checked':1},{'id':88439707})
    # db.runQuary('ALTER TABLE users1 rename to users')
    # db.createTable('users',{
    #         'id':'int unique',
    #         'username':'varchar(60)',
    #         'firstName':'varchar(60)',
    #         'lastName':'varchar(60)',
    #         'checked':'bit default 0'
    #         })
    users = pd.DataFrame(db.selectWhereLimit('users',{'checked':False},10))
    # users = [{key:( val if key!= 'checked' else 0) for key,val in i.items()} for i in db.selectAll('users')]
    # users['checked'] = users['checked'].fillna(0)
    # db.insertAll('users1',users)

    print(users)