import mysqlconfig
import pymysql



def mysqlconnect():
	return pymysql.connect(host = mysqlconfig.host,
		user = mysqlconfig.user,
		passwd = mysqlconfig.password,
		db = mysqlconfig.db)

