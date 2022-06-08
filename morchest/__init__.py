"""
Copyright (c) 2022, Miles Frantz
All rights reserved.
This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""
import os, sys, orchest, pandas as pd, funbelts as ut, pickle
from telegram import Bot
from copy import deepcopy as dc

def clean_row_of_dicts(frame:pd.DataFrame):
	easy_frame,rename,remove = ut.frame_dycts(frame), {},[]
	for key in easy_frame[0].keys():
		if " " in key:
			rename[key] = key.replace('','_')
		elif key.startswith('_'):
			remove += [key]

	for row in easy_frame:
		for old_name, new_name in rename.items():
			row[new_name] = row[old_name]
			row.pop(old_name)
		for to_remove in remove:
			row.pop(to_remove)
	return ut.arr_to_pd(easy_frame)

def get_param(param, default: str = None):
	return orchest.get_step_param(param, default)

class wrapper():
	def __init__(self, latestStep: str, setName: str = "DUMB", load: bool = False, telegram: bool = False, localDataFile:str=None):
		"""
		In case of testing

pipeline = orchest.get_inputs()['DUMB']
if True:
	#<ACTION>

pipeline['LatestStep'] = __file__
orchest.output(pipeline, name="DUMB")
		"""
		self.setName = setName
		self.current_results = None
		self.setlatestStep = latestStep
		self.load = load
		self.telegram = None
		self.call_path = []
		if telegram:
			self.telegram = Bot(os.environ["TbotID"])
			self.chatID = os.environ["TchatID"]
		# ut.telegramBot(os.environ["TbotID"],os.environ["TchatID"])
		self.local = localDataFile
		if self.local is not None and not self.local.endswith(".pkl"):
			self.local += ".pkl"

	def __getitem__(self, key):
		if not isinstance(key, str) or key not in self.current_results.keys():
			return None
		return self.current_results[key]

	def __setitem__(self, key, value):
		if not isinstance(key, str):
			return None
		self.current_results[key] = value

	def __enter__(self):
		print(f"Starting at step {self.setlatestStep}")
		if self.load:
			self.current_results = {
				'Results': {
					'Photos': {},
					'Text': {},
				}, 'CallChain': []
			}
		elif self.local is not None:
			with open(self.local, "rb") as reader:
				self.current_results = pickle.load(reader)
			os.remove(self.local)
		else:
			try:
				self.current_results = orchest.get_inputs()[self.setName]
			except Exception as e:
				self.local = "_temp_morchest.pkl"
				print(f"Error Resolving Orchest :> {e}")
				print(f"Defaulting to temp_pickle_file {self.local}")
				self.current_results = {
					'Results': {
						'Photos': {},
						'Text': {},
					}, 'CallChain': []
				}
				


		self['LatestStep'] = self.setlatestStep
		self['CallChain'] += [self.setlatestStep]
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.local is not None:
			os.remove(self.local)
			with open(self.local, "wb+") as writer:
				pickle.dump(self.current_results, writer)
		else:
			orchest.output(self.current_results, name=self.setName)

		print(f"Exiting at step {self.setlatestStep}")
		return self

	def param(self, param, default: str = None):
		return orchest.get_step_param(param, default)

	@property
	def data(self):
		return "/data/"

	@property
	def clean(self):
		for ext in [".xlsx", ".csv", ".png", ".jpg", ".json", ".puml", ".svg"]:
			try:
				os.system(f"yes|rm -r *{ext}")
			except:
				pass
		return

	def temp(self, file):
		prefix = "results"
		return f"{prefix}/{file}"

	def keys(self):
		return self.current_results.keys()

	def values(self):
		return self.current_results.values()

	def items(self):
		return self.current_results.items()

	def msg(self, string: str = ""):
		if self.telegram:
			try:
				self.telegram.send_message(self.chatID, string)
			except Exception as e:
				print(f"Exception :> {e}")
				pass
		print(string)

	def get_last_working_step(self, get_last: int = 2):
		synthed, ktr = dc(self['CallChain']), 0
		synthed.reverse()
		for step in synthed:
			if not step.startswith("Report_") and not step.startswith("Util_"):
				ktr += 1
				if ktr == get_last:
					return step
		return None

	def upload(self, path, string: str = "", delete: bool = True):
		if self.telegram:
			ext = path.split(".")[-1].lower()
			if ext in ["png", "jpeg"]:
				self.upload_photo(path, string, delete)
			elif ext in [".mp4"]:
				self.upload_video(path, string, delete)
			else:
				try:
					self.telegram.send_document(chat_id=self.chatID, document=open(path, 'rb'), caption=string)
					if delete:
						os.remove(path)
				except Exception as e:
					print(f"Exception :> {e}")
					pass

	def upload_frame(self, frame, name: str = "CurrentFrame", string: str = "", delete: bool = True, useIndex:bool=False):
		import time

		prep_name = self.get_last_working_step().replace(".py", "")

		foil_name, ktr = f"{prep_name}_10.xlsx", 10
		while os.path.exists(foil_name):
			cur_num = ktr
			ktr += 1
			foil_name = foil_name.replace(str(cur_num), str(ktr))
			time.sleep(.2)

		print(f"Made file {foil_name}")
		print(frame)
		with ut.xcyl(foil_name, useIndex=useIndex) as writer:
			writer.add_frame(name, frame)
			writer.add_frame("SystemInformation", ut.get_system_info())
			print(f"G")
			print(f"{writer.cur_data_sets.keys()}")
		print("")

		self.upload(foil_name, string, delete)

	def upload_photo(self, path, string: str = "", delete: bool = True):
		"""
		> https://docs.python-telegram-bot.org/en/stable/telegram.bot.html?highlight=send_video#telegram.Bot.send_photo
		"""
		if self.telegram:
			try:
				self.telegram.send_photo(chat_id=self.chatID, photo=open(path, 'rb'), caption=string)
				if delete:
					os.remove(path)
			except Exception as e:
				print(f"Exception :> {e}")
				pass

	def upload_video(self, path, string: str = "", delete: bool = True):
		"""
		> https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html?highlight=send_video#telegram.Bot.send_video
		"""
		if self.telegram:
			try:
				self.telegram.send_video(chat_id=self.chatID, video=open(path, 'rb'), caption=string,
										 supports_streaming=True)
				if delete:
					os.remove(path)
			except Exception as e:
				print(f"Exception :> {e}")
				pass
