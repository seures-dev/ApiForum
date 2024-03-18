import json
import time
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Text, JSON, String
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from validate_email_address import validate_email
from src import db


class Thread_(db.Model):
	__tablename__ = "threads"

	thread_id = Column(Integer, primary_key=True)

	creator_id = Column(Integer, ForeignKey("users.user_id", name="user_threads"))
	creator = relationship("User")
	name = Column(String(30), nullable=False, default="New threat")
	created_date = Column(DateTime)
	branch_count = Column(Integer, default=0, nullable=False)
	branches = relationship("Branch")

	def __init__(self, creator=None, name=None, delta_time=0):
		if creator is None:
			creator = 1
		self.creator_id = creator
		self.created_date = datetime.now()
		time_ = time.time() - delta_time
		self.created_date = datetime.fromtimestamp(time_)
		if name:
			self.name = name
		
	def to_dict(self):
		dict_data = {
			"name": self.name,
			"thread_id": self.thread_id,
			"creator_id": self.creator_id,
			"created_date": self.created_date.strftime("%Y-%m-%d-%H:%M:%S"),
			"branch_count": self.branch_count,
		}
		return dict_data
	
	def get_branches(self, offset=0, all_branches=None):
		if all_branches:
			return db.session.query(Branch).filter_by(thread_id=self.thread_id).all()
		if offset == 0:
			return db.session.query(Branch).filter_by(thread_id=self.thread_id).order_by(Branch.id).limit(
				30).all()
		return db.session.query(Branch).filter_by(thread_id=self.thread_id).order_by(Branch.id).offset(
			offset).limit(30).all()


class Branch(db.Model):
	__tablename__ = "branches"

	id = Column(Integer, primary_key=True, autoincrement=True)
	thread_id = Column(Integer, ForeignKey("threads.thread_id", name="thread_branches"))
	thread = relationship("Thread_", back_populates="branches")
	name = Column(String(30), nullable=False, default="New branch")
	creator_id = Column(Integer, ForeignKey("users.user_id", name="user_branches"), nullable=False)
	creator = relationship("User")
	created_date = Column(DateTime, nullable=False)
	message_count = Column(Integer, default=0, nullable=False)

	posts = relationship("Post")

	def __init__(self, thread_id, creator, delta_time=0, name=None):

		self.thread_id = thread_id
		self.creator_id = creator
		time_ = time.time() - delta_time
		self.created_date = datetime.fromtimestamp(time_)

		if name:
			self.name = name

	def __repr__(self):
		return f"Post: {self.id},  {self.intobranch_id},  {self.creator_id},  {self.created_date}\n content:{self.content}"



	def get_posts(self, offset=0, all_post=None):
		if self.message_count < 1:
			return []
		if all_post:
			return Post.query.filter_by(branch_id=self.id).all()
		if offset == 0:
			return Post.query.filter_by(branch_id=self.id).order_by(Post.created_date).limit(30).all()
		return Post.query.filter_by(branch_id=self.id).order_by(Post.created_date).offset(offset).limit(30).all()

	def to_dict(self):
		data = {
			"branch_name": self.name,
			"branch_id": self.id,
			"thread_id": self.thread_id,
			"creator_id": self.creator_id,
			"created_date": self.created_date.strftime("%Y-%m-%d-%H:%M:%S"),
			"message_count": self.message_count
		}

		return data

class Post(db.Model):
	__tablename__ = "posts"
	u_id = Column(Integer, primary_key=True, autoincrement=True)
	branch_id = Column(Integer, ForeignKey("branches.id", name="branch_posts"), primary_key=True)
	branch = relationship("Branch", back_populates="posts")
	into_branch_id = Column(Integer, nullable=False)
	creator_id = Column(Integer, ForeignKey("users.user_id", name="user_posts"), nullable=False)
	creator = relationship("User")
	created_date = Column(DateTime, nullable=False)
	content = Column(Text, nullable=False)
	extra = Column(JSON)

	def __init__(self, b_id, ib_id, creator, content, u_id=-1, delta_time=0):

		self.branch_id = b_id
		self.into_branch_id = ib_id
		self.creator_id = creator
		time_ = time.time() - delta_time
		self.created_date = datetime.fromtimestamp(time_)
		self.content = content

	# def __repr__(self):
	# 	return f"Post: {self.b_id},  {self.intobranch_id},  {self.creator_id},  {self.created_date}\n content:{self.content}"

	def to_dict(self):
		return {
			"u_id": self.u_id,
			"branch_id": self.branch_id,
			"into_branch_id": self.into_branch_id,
			"creator_id": self.creator_id,
			"created_date": self.created_date.strftime("%Y-%m-%d-%H:%M:%S"),
			"content": self.content
		}


class User(db.Model):
	__tablename__ = "users"

	user_id = Column(Integer, primary_key=True)
	nickname = Column(String(30), unique=True, nullable=False)
	email = Column(String(30), unique=True, nullable=False)
	password_hash = Column(String(255), nullable=False)
	created_date = Column(DateTime, nullable=False)
	access_level = Column(Integer, nullable=False)
	posts = relationship("Post", overlaps="creator")
	branches = relationship("Branch", overlaps="creator")
	threads = relationship("Thread_", overlaps="creator")

	def __init__(self, nick, password, email, access_level=0):
		if not validate_email(email):
			raise ValueError("Wrong format")
		if str.isdigit(nick[0]):
			raise ValueError("Nick name begin by digit")
		self.email = email
		self.nickname = nick
		self.password_hash = password #generate_password_hash(password)
		self.access_level = access_level
		self.created_date = datetime.now()

	@staticmethod
	def get_user_by_id(user_id: int) -> 'User':
		return db.session.query(User).filter_by(user_id=user_id).first()

	@staticmethod
	def get_user_by_nick(nickname: str) -> 'User':
		return db.session.query(User).filter_by(nickname=nickname).first()

	def password_check(self, password):
		return check_password_hash(self.password_hash, password)

	def to_dict(self, threads=None, branches=None, posts=None, all_info=None):
		data = {
			"user_id": self.user_id,
			"name": self.nickname,
			"access_level": self.access_level,
			"created": self.created_date.strftime("%Y-%m-%d-%H:%M:%S"),
		}
		if all_info:
			data["email"] = self.email
			data["password_hash"] = self.password_hash
		if threads:
			data["threads"] = threads
		if branches:
			data["branches"] = branches
		if posts:
			data["posts"] = posts
		return data
