# from app import db
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Venue Model.
#----------------------------------------------------------------------------#
class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  description = db.Column(db.String(), nullable=True)
  genres = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(300), nullable=False)
  phone = db.Column(db.String(120), nullable=True, unique=True)
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(300), nullable=False)
  website_link = db.Column(db.String(300), nullable=True)
  looking_for_talent = db.Column(db.Boolean, nullable=False, default=False)
  # artists = db.relationship('Artist', secondary="shows")
  
  def __repr__(self):
    return f'''<Venue {self.id}, {self.description} {self.name} {self.genres}
      {self.city}, {self.state} {self.address} {self.phone}
      {self.image_link}, {self.facebook_link} {self.website_link} {self.looking_for_talent}
  >'''
    # return '<Venue #%s:%r>' % (self.id, self.name)
  
  # @property
  # def genres(self):
  #   return list(self._genres.split(" "))

  # @genres.setter
  # def genres(self, value):
  #   self._genres = value

  # genres = synonym('_genres', descriptor=genres)
  

#----------------------------------------------------------------------------#
# Artist Model.
#----------------------------------------------------------------------------#
class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  description = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.String(), nullable=False)
  image_link = db.Column(db.String(500), nullable=False)
  facebook_link = db.Column(db.String(120), nullable=False)
  website_link = db.Column(db.String(300), nullable=False)
  looking_for_venue = db.Column(db.Boolean, nullable=False, default=False)
  # venues = db.relationship('Venue', secondary="shows")

  def __repr__(self):
    return '<Artist #%s:%r>' % (self.id, self.name)
  

#----------------------------------------------------------------------------#
# Show Model.
#----------------------------------------------------------------------------#
class Show(db.Model):
  __tablename__ = "shows"
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
  start_time = db.Column(db.DateTime(timezone=True))
  artist = db.relationship("Artist", backref=db.backref("shows", cascade="all, delete-orphan"))
  venue = db.relationship("Venue", backref=db.backref("shows", cascade="all, delete-orphan"))
