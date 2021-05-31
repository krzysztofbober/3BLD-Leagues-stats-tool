from auth import *
import sqlite3

conn = sqlite3.connect('leagues.db')
c = conn.cursor()
d = conn.cursor()


class Table:
	def __init__(self, players, worksheet):
		self.players = players
		self.worksheet = worksheet
		

		self.players.sort(key=lambda x: x.RP, reverse=True)
		self.players.sort(key=lambda x: x.PTS, reverse=True)

		self.sort()
		self.show()
		self.export_to_sheet()

	def sort(self):
		self.sorted_table = []
		for player in self.players:
			self.sorted_table.append([player.name, player.M, player.Z, player.R, player.P, player.PZ, player.PS, player.RP, player.PTS])

	def show(self):
		for row in self.sorted_table:
			print(row)

		print()

	def export_to_sheet(self):
		target = 'H13:P{}'.format(12 + len(self.sorted_table))
		worksheet.update(target, self.sorted_table)



class Player:
	def __init__(self, name, league_id):
		self.name = name
		self.league_id = league_id

		self.M, self.PZ, self.PS, self.Z, self.R, self.P = 0,0,0,0,0,0

		self.import_matches()
		self.analysis()
		self.summary()

	def import_matches(self):
		c.execute("SELECT resultA, resultB FROM Match WHERE playerA=? AND league=?", (self.name, self.league_id,))
		d.execute("SELECT resultB, resultA FROM Match WHERE playerB=? AND league=?", (self.name, self.league_id,))
		self.matches = c.fetchall() + d.fetchall()

	def analysis(self):
		for match in self.matches:
			self.M += 1
			self.PZ += match[0]
			self.PS += match[1]
			if match[0] > match[1]: self.Z += 1
			elif match[0] == match[1]: self.R +=1
			else: self.P += 1

	def summary(self):
		self.RP = self.PZ - self.PS
		self.PTS = 2*self.Z + self.R




s, l = 1,1
c.execute("SELECT name FROM League")

for league in c.fetchall(): 
	league_players = []
	worksheet = spreadsheet.worksheet(league[0])
	lid = '0{}0{}'.format(s,l)
	
	players = worksheet.get("D5:D11")
	for p in players:
		league_players.append(Player(p[0], lid))
	Table(league_players, worksheet)


	l +=1


conn.commit()
conn.close()
