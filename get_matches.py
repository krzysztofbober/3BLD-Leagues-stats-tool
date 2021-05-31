from auth import *
import sqlite3

def convert_time(t, to_secs=True):
	if t == 'DNF' or t == 'dnf' or t == 'Dnf' or t == 'DNS' or t == 'dns' or t == 'DMF': return 'DNF'
	if to_secs is True:
		pointer1 = [":", ";"]
		pointer2 = [',', '.']
		p1 = max([t.find(pointer1[0]), t.find(pointer1[1])])
		p2 = max([t.find(pointer2[0]), t.find(pointer2[1])])
		if p1 != -1:
			m = t[:p1]
			s = t[p1+1:p2]
			ms = t[p2+1:]
			try: conv_time = float(m)*60 + float(s) + float(ms)/100
			except: return 'DNF'
		elif p1 == -1 and p2 == -1:
			return float(t)
		else:
			s = t[:p2]
			ms = t[p2+1:]
			conv_time = float(s) + float(ms)/100
		return conv_time	
	else:
		if t < 60: return t
		else:
			t = str(t)
			pointer = t.find('.')
			s = float(t[0:pointer])
			ms = float(t[pointer+1:])
			m = s//60
			s = s - 60*m
			zero = ''
			if s < 10: zero = '0'
			return '{}:{}{}.{}'.format(int(m),zero,int(s),int(ms))

class Match:
	matches= []
	results= []
	def __init__(self, data1, data2, league, ses, game):
		self.data1 = data1
		self.data2 = data2
		self.league = league
		self.ses = ses
		self.game = game

		self.p1, self.p2 = self.data1[0], self.data2[0]
		self.pts1, self.pts2 = self.data1[1], self.data2[1]
		self.times = []

		self.split_results()


	def export_match(self):
		c.execute("SELECT * FROM Match")
		all_data = c.fetchall()

		c.execute("SELECT league_id FROM League WHERE name=? AND season=?", (self.league,self.ses,))
		league_id = c.fetchall()[0][0]
		
		wo_id = []
		for d in all_data:
			wo_id.append(d[1:])

		if (self.league, None, self.p1, self.p2, self.pts1, self.pts2) not in wo_id:
			match_id = 1 + len(all_data)
			to_export = (match_id, league_id, self.game, self.p1, self.p2, self.pts1, self.pts2)
			c.execute("INSERT INTO Match VALUES (?, ?, ?, ?, ?, ?, ?)", to_export)

			self.export_times(match_id)

	def export_times(self, match_id):
		for i in range(2, len(self.data1)):
			a = convert_time(convert_time(self.data1[i]), to_secs=False)
			b = convert_time(convert_time(self.data2[i]), to_secs=False)
			self.times.append((self.p1, match_id, a))
			self.times.append((self.p2, match_id, b))

		c.executemany("INSERT INTO Results(player, match, result) VALUES (?, ?, ?)", self.times)



	def split_results(self):
		if int(self.pts1) > 0 or int(self.pts2) > 0:
			print('{} {}-{} {}'.format(self.p1, self.pts1, self.pts2, self.p2))
			self.export_match()
				
		
class Row:
	def __init__(self, left_corner, league, ses):
		self.left_corner = left_corner
		target = 'R{}:BH{}'.format(left_corner, left_corner+16)
		self.data = worksheet.get(target)
		for m in (0, 8, 16, 24, 32, 40):
			res1, res2 = [], []
			try:
				game = self.data[0][m]
			except: continue
			for r in self.data:
				try:
					if r[m+1] == "" or r[m+2] == "": break
					res1.append(r[m+1])
					res2.append(r[m+2])

				except: pass
			if len(res1) < 2 or len(res2) < 2: continue
			Match(res1, res2, league, ses, game)
		
season = 1
conn = sqlite3.connect('leagues.db')
c = conn.cursor()
c.execute("SELECT name FROM League")


for league in c.fetchall():
	worksheet = spreadsheet.worksheet(league[0])

	for r in range(7):
		row = Row(6 + r*23, league[0], season)

	column = worksheet.get("D14:D55")
	games = worksheet.get("A14:A55")
	to_write = []
	for n in range(len(column)):
		match = column[n][0]
		g = games[n][0]
		pointer = match.find('-')
		p1 = match[:pointer-1]
		p2 = match[pointer+2:]
		print(p1, p2, g)

		c.execute("SELECT resultA, resultB FROM Match WHERE playerA=? AND playerB=? AND game=?", (p1, p2,g,))
		res = c.fetchall()
		if len(res) != 0:
			res1, res2 = res[0][0], res[0][1]
			to_write.append(['{}-{}'.format(res1, res2)])
		else:
			to_write.append(['-'])

	print(to_write)
	print(len(to_write))
	worksheet.update("E14:E55", to_write)





conn.commit()
conn.close()