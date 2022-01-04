from os import path
import sqlite3

class Credentials:
	def __init__(self):
		self.master_passwd_file=".masterPasswd.log"
		self.have_master_passwd=False
		self.master_passwd=""
		self.database_name="credentials.db"

		self.conn=sqlite3.connect(self.database_name)
		self.cursor=self.conn.cursor()
		self.create_database()
	
	def create_database(self):
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS credentials (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user text NOT NULL,
			passwd text NOT NULL,
			email text NOT NULL,
			account text NOT NULL
		)""")
		self.conn.commit()
		
	def check_for_master_passwd(self):
		if not path.exists(self.master_passwd_file):
			with open(self.master_passwd_file,"w"):
				self.have_master_passwd=False
		else:
			with open(self.master_passwd_file) as f:
				self.master_passwd=f.read().strip()
				if self.master_passwd:
					self.have_master_passwd=True
				else:
					self.have_master_passwd=False
		return self.have_master_passwd
		
	def get_master_passwd(self):
		with open(self.master_passwd_file) as f:
			self.master_passwd=f.read().strip()
		return self.master_passwd
	
	def set_master_passwd(self,new_password):
		if new_password:
			with open(self.master_passwd_file,"w") as f:
				f.write(new_password)
	
	def save_credentials(self,usr,em,passwd,acct):
		self.cursor.execute("INSERT INTO credentials (user,passwd,email,account) values (?,?,?,?)",(usr.strip(),passwd.strip(),em.strip(),acct.strip()))
		self.conn.commit()
		
	def get_credentials(self):
		res=self.cursor.execute("SELECT * from credentials")
		cred=[r for r in res]
		self.conn.commit()
		return cred

	def delete_credential(self,id):
		self.cursor.execute("DELETE from credentials WHERE id = ?",(id,))
		self.conn.commit()
	
	def get_id(self,acct,usr):
		the_id=0
		for data in self.get_credentials():
			if data[1]==usr and data[-1]==acct:
				the_id=data[0]
				return the_id
				
	def close_connection(self):
		self.cursor.close()
		self.conn.close()
				