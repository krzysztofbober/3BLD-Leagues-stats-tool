import sqlite3
from authorization import *
from statistics import stdev, mean


class Player:
	all_players = []
	def __init__(self, name, group):
		self.name = name
		self.group = group
		self.converted_times = []
		self.successes = []


	@staticmethod
	def convert_time(t, to_secs=True):
		if to_secs is True:
			pointer1 = [":", ";"]
			pointer2 = [',', '.']
			p1 = max([t.find(pointer1[0]), t.find(pointer1[1])])
			p2 = max([t.find(pointer2[0]), t.find(pointer2[1])])
			if p1 != -1:
				m = t[:p1]
				s = t[p1+1:p2]
				ms = t[p2+1:]
				conv_time = float(m)*60 + float(s) + float(ms)/100
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



	@classmethod
	def import_from_database(cls, target):
		conn = sqlite3.connect('3bldautumntournament.db')
		c = conn.cursor()

		#command = "SELECT * FROM {}".format(target)
		c.execute('SELECT * FROM {}'.format(target))

		imported_players = c.fetchall()

		for p in imported_players:
			cls.all_players.append(cls(p[0], p[1]))
			c.execute("SELECT * FROM results WHERE player=?", (p[0],))
			
			for line in c.fetchall():
				t = line[1].upper()
				if t == "DNF": cls.all_players[-1].converted_times.append(t)
				else:
					conv_t = Player.convert_time(t, to_secs=True)
					cls.all_players[-1].converted_times.append(conv_t)
					cls.all_players[-1].successes.append(conv_t)
		conn.commit()
		conn.close()
		Player.do_stats()

		return cls.all_players
		
	@classmethod
	def do_stats(cls):
		data_to_export = []
		for n in range(24):
			p = cls.all_players[n]
			p.acc = int(100*len(p.successes)/len(p.converted_times))
			p.times_mean = round(mean(p.successes),2)
			p.best = min(p.successes)
			if len(p.successes) < 2: p.sd = 0
			else: p.sd = round(stdev(p.successes),2)
			data_to_export.append([p.name, p.times_mean, p.best, p.acc, p.sd, len(p.successes), len(p.converted_times)])

		data_to_export.sort(key=lambda x: x[1])
		data_to_show = []
		for line in data_to_export:
			n = str(line[0])
			m = str(Player.convert_time(line[1], to_secs=False))
			b = str(Player.convert_time(line[2], to_secs=False))
			a = '{}/{} ({}%)'.format(line[5], line[6], line[3])
			sd = str(Player.convert_time(line[4], to_secs=False))
			data_to_show.append([n, m, b, a, sd])
		worksheet = spreadsheet.worksheet("Statystyki")
		
		worksheet.update("N2:R25", data_to_show)



		



		

data = Player.import_from_database("players")





