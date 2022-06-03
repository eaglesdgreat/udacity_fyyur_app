#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from sqlalchemy import func, or_, case, desc
from datetime import date
from models import db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# TODO: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# shows = db.Table('shows',
#   db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
#   db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
#   db.Column('start_time', db.DateTime(timezone=True))
# )
# TODO: implement any missing fields, as a database migration using Flask-Migrate  
from models import Venue, Artist, Show
# class Venue(db.Model):
#   __tablename__ = 'venues'

#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(), nullable=False)
#   description = db.Column(db.String(), nullable=True)
#   genres = db.Column(db.String(), nullable=False)
#   city = db.Column(db.String(120), nullable=False)
#   state = db.Column(db.String(120), nullable=False)
#   address = db.Column(db.String(300), nullable=False)
#   phone = db.Column(db.String(120), nullable=True, unique=True)
#   image_link = db.Column(db.String(500), nullable=True)
#   facebook_link = db.Column(db.String(300), nullable=False)
#   website_link = db.Column(db.String(300), nullable=True)
#   looking_for_talent = db.Column(db.Boolean, nullable=False, default=False)
#   # artists = db.relationship('Artist', secondary="shows")
#   # artists = db.relationship('Artist', secondary="shows", backref=db.backref('venues', lazy=True))
  
#   def __repr__(self):
#     return f'''<Venue {self.id}, {self.description} {self.name} {self.genres}
#       {self.city}, {self.state} {self.address} {self.phone}
#       {self.image_link}, {self.facebook_link} {self.website_link} {self.looking_for_talent}
#   >'''
#     # return '<Venue #%s:%r>' % (self.id, self.name)
  
#   # @property
#   # def genres(self):
#   #   return list(self._genres.split(" "))

#   # @genres.setter
#   # def genres(self, value):
#   #   self._genres = value

#   # genres = synonym('_genres', descriptor=genres) 

# # TODO: implement any missing fields, as a database migration using Flask-Migrate
# class Artist(db.Model):
#   __tablename__ = 'artists'

#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(), nullable=False)
#   description = db.Column(db.String(), nullable=False)
#   city = db.Column(db.String(120), nullable=False)
#   state = db.Column(db.String(120), nullable=False)
#   phone = db.Column(db.String(120), nullable=False)
#   genres = db.Column(db.String(), nullable=False)
#   image_link = db.Column(db.String(500), nullable=False)
#   facebook_link = db.Column(db.String(120), nullable=False)
#   website_link = db.Column(db.String(300), nullable=False)
#   looking_for_venue = db.Column(db.Boolean, nullable=False, default=False)
#   # venues = db.relationship('Venue', secondary="shows")

#   def __repr__(self):
#     return '<Artist #%s:%r>' % (self.id, self.name)
# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# class Show(db.Model):
#   __tablename__ = "shows"
#   id = db.Column(db.Integer, primary_key=True)
#   artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
#   venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
#   start_time = db.Column(db.DateTime(timezone=True))
#   artist = db.relationship("Artist", backref=db.backref("shows", cascade="all, delete-orphan"))
#   venue = db.relationship("Venue", backref=db.backref("shows", cascade="all, delete-orphan"))
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  venues = Venue.query.order_by(desc(Venue.id)).limit(10).all()
  
  return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues',  methods=['GET'])
def venues():
    # TODO: replace with real venues data.
    # Raw Query
    # #########################################
    # select v.city, v.state, v.name, v.id, sum(case when s.start_time >= '2022-06-03 16:47:22+01'::date then 1 else 0 end) 
    # as upcoming_show from venues v 
    # left join shows s on v.id = s.venue_id 
    # where s.start_time >= CURRENT_DATE or s.start_time < CURRENT_DATE or s.start_time is null 
    # group by v.city, v.state, v.name, v.id  
    #########################################
    
    # SQLAlchemy
    query = Venue.query.join(Show, isouter=True).with_entities(
      Venue.city, Venue.state, Venue.name, Venue.id,
      func.sum(case((Show.start_time >= date.today(), 1), else_=0)).label('num_upcoming_shows'),
      # func.count(Show.start_time)
    ).filter(or_(Show.start_time >= date.today(), Show.start_time < date.today(), Show.start_time.is_(None))).group_by(
      Venue.city, Venue.state, Venue.name, Venue.id
    )
    results = {}
    data = [];
    for city, state, name, id, num_upcoming_shows in query:
      location = (city, state)
      if location not in results:
        results[location] = []
        data.append({"city": city, "state": state, "venues": results[location]})
        
      results[location].append({"id": id, "name": name, "num_upcoming_shows": num_upcoming_shows})
      
      if location in results:
        for item in data:
          if item['city'] == city and item['state'] == state:
            item['venues'] = results[location]
  
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    
    # RAW QUERY
    ###################################################
    # SELECT v.name, v.id, SUM(CASE WHEN s.start_time >= CURRENT_DATE::date THEN 1 ELSE 0 END) AS num_upcoming_shows
    # FROM venues v 
    # LEFT JOIN shows s ON v.id = s.venue_id 
    # WHERE v.name LIKE 'sherano club' 
    # AND s.start_time >= CURRENT_DATE OR s.start_time IS NULL 
    # GROUP BY v.name, v.id;
    ##################################################
    
    # SQL ALchemy
    searches= request.form.get("search_term", "").split(", ")
    print(searches)
    query = Venue.query.join(Show, isouter=True).with_entities(
      Venue.name, Venue.id,
      func.sum(case((Show.start_time >= date.today(), 1), else_=0)).label('num_upcoming_shows'),
      # func.count(Show.start_time)
    ).filter(or_(
        *[Venue.name.ilike(prefix + '%') for prefix in searches],
        *[Venue.city.ilike(prefix + '%') for prefix in searches],
        *[Venue.state.ilike(prefix + '%') for prefix in searches],
      )
    ).filter(
      or_(Show.start_time >= date.today(), Show.start_time < date.today(), Show.start_time.is_(None))
    ).group_by(
      Venue.name, Venue.id
    )
    data = []
    for name, id, num_upcoming_shows in query:
      data.append({"id": id, "name": name, "num_upcoming_shows": num_upcoming_shows})
    
    response = { "count": len(data), "data": data }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>',  methods=['GET'])
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    
    # RAW QUERY
    ##########################################################
    # SELECT v.*, a.id AS artist_id, a.name AS artist_name, a.image_link AS artist_image_link, s.start_time, 
    # SUM(CASE WHEN s.start_time::date >= '2022-05-31 16:47:22+01'::date THEN 1 ELSE 0 END) AS upcoming_show_count, 
    # SUM(CASE WHEN s.start_time::date < '2022-05-31 16:47:22+01'::date THEN 1 ELSE 0 END) AS past_show_count 
    # FROM venues v 
    # LEFT JOIN shows s ON v.id = s.venue_id 
    # RIGHT JOIN artists a ON a.id = s.artist_id 
    # WHERE v.id = 3 AND (s.start_time >= CURRENT_DATE OR s.start_time IS NULL OR s.start_time < CURRENT_DATE) 
    # GROUP BY v.id, a.id, s.start_time;
    ##########################################################
    
    # SQL ALchemy
    query = Venue.query.join(Show, isouter=True).join(Artist, Artist.id ==  Show.artist_id).with_entities(
      Venue.id, Venue.name, Venue.image_link, Venue.genres, Venue.address,
      Venue.city, Venue.state, Venue.phone, Venue.description, Venue.facebook_link,
      Venue.website_link, Venue.looking_for_talent, Artist.id.label('artist_id'),
      Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time,
      func.sum(case((Show.start_time >= date.today(), 1), else_=0)).label('upcoming_show_count'),
      func.sum(case((Show.start_time < date.today(), 1)), else_=0).label('past_show_count'),
    ).filter(Venue.id == venue_id).filter(
      or_(Show.start_time >= date.today(), Show.start_time < date.today(), Show.start_time.is_(None))
    ).group_by(
      Venue.id, Artist.id, Show.start_time
    )
    data = {
      "id": "",
      "name": "",
      "genres": "",
      "address": "",
      "city": "",
      "state": "",
      "phone": "",
      "website": "",
      "facebook_link": "",
      "seeking_talent": False,
      "seeking_description": "",
      "image_link": "",
      "past_shows_count": 0,
      "upcoming_shows_count": 0,
      "upcoming_shows": [],
      "past_shows": [],
    }
    if len(query.all()) > 0:
      for result in query:
        data["id"] = result.id
        data["name"] = result.name
        data["genres"] = list(result.genres.split("_"))
        data["address"] = result.address
        data["city"] = result.city
        data["state"] = result.state
        data["phone"] = result.phone
        data["website"] = result.website_link
        data["facebook_link"] = result.facebook_link
        data["seeking_talent"] = result.looking_for_talent
        data["seeking_description"] = result.description
        data["image_link"] = result.image_link
        if result.upcoming_show_count > 0:
          data['upcoming_shows_count'] += result.upcoming_show_count
          data['upcoming_shows'].append({
            "artist_id": result.artist_id,
            "artist_name": result.artist_name,
            "artist_image_link": result.artist_image_link,
            "start_time": str(result.start_time)
          })
        if result.past_show_count != None and result.past_show_count > 0:
          data['past_shows_count'] += result.past_show_count
          data['past_shows'].append({
            "artist_id": result.artist_id,
            "artist_name": result.artist_name,
            "artist_image_link": result.artist_image_link,
            "start_time": str(result.start_time)
          })
    else:
      query = Venue.query.filter_by(id = venue_id).all()
      for result in query:
        data["id"] = result.id
        data["name"] = result.name
        data["genres"] = list(result.genres.split("_"))
        data["address"] = result.address
        data["city"] = result.city
        data["state"] = result.state
        data["phone"] = result.phone
        data["website"] = result.website_link
        data["facebook_link"] = result.facebook_link
        data["seeking_talent"] = result.looking_for_talent
        data["seeking_description"] = result.description
        data["image_link"] = result.image_link
          
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False
  if form.validate():
    genres = '_'.join(map(str, form.genres.data))
    try:
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      venue = Venue(
        name=form.name.data,
        description=form.seeking_description.data,
        genres=genres,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        looking_for_talent=form.seeking_talent.data,
      )
      db.session.add(venue)
      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] +
            ' was successfully listed!')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' +
            request.form['name'] + ' could not be listed.')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      db.session.close()
      
  if error:
    abort(400)
  else:
    return render_template('pages/home.html')
  
#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  query =  Venue.query.filter_by(id = venue_id).first()
  venue = {
      "id": query.id,
      "name": query.name,
      "genres": list(query.genres.split("_") or query.genres.split(" ")),
      "address": query.address,
      "city": query.city,
      "state": query.state,
      "phone": query.phone,
      "website_link": query.website_link,
      "facebook_link": query.facebook_link,
      "seeking_talent": query.looking_for_talent,
      "seeking_description": query.description,
      "image_link": query.image_link,
  }
  form = VenueForm(**venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  error = False
  print(form.seeking_talent.data)
  if form.validate():
    genres = '_'.join(map(str, form.genres.data))
    try:
      venue =  Venue.query.get(venue_id)
      venue.name = form.name.data,
      venue.description = form.seeking_description.data,
      venue.genres = genres,
      venue.city = form.city.data,
      venue.state = form.state.data,
      venue.address = form.address.data,
      venue.phone = form.phone.data,
      venue.image_link = form.image_link.data,
      venue.facebook_link = form.facebook_link.data,
      venue.website_link = form.website_link.data,
      venue.looking_for_talent = form.seeking_talent.data
      db.session.commit()
      
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] +
            ' was successfully updated.')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' +
            request.form['name'] + ' could not be updated with new value.')
    finally:
      db.session.close()
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
  
  if error:
   abort(400)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/delete/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  name = ""
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
    
    flash('Venue ' + name +
            ' was successfully deleted.')
  except:
    db.session.rollback()
    print(sys.exc_info())
    
    flash('An error occurred. Venue ' +
            name + ' could not be deleted.')
  finally:
    db.session.rollback()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))
  # return render_template('pages/home.html')




#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.with_entities(
    Artist.id, Artist.name
  ).group_by(Artist.id).all()
  
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searches= request.form.get("search_term", "").split(", ")

  query = Artist.query.join(Show, isouter=True).with_entities(
    Artist.name, Artist.id,
    func.sum(case((Show.start_time >= date.today(), 1), else_=0)).label('num_upcoming_shows'),
    # func.sum(Show.start_time).label(num_upcoming_shows)
  ).filter(or_(
      *[Artist.name.ilike(prefix + '%') for prefix in searches],
      *[Artist.city.ilike(prefix + '%') for prefix in searches],
      *[Artist.state.ilike(prefix + '%') for prefix in searches],
      # Artist.name.ilike(f"%{search}%"),
      # Artist.city.ilike(f"%{search}%"),
      # Artist.state.ilike(f"%{search}%"),
    )
  ).filter(
    or_(Show.start_time >= date.today(), Show.start_time < date.today(), Show.start_time.is_(None))
  ).group_by(
    Artist.name, Artist.id
  )
  
  data = []
  for name, id, num_upcoming_shows in query:
    data.append({"id": id, "name": name, "num_upcoming_shows": num_upcoming_shows})
  response = {
    "count": len(data),
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  query = Artist.query.join(Show).join(Venue).with_entities(
    Artist.id, Artist.name, Artist.image_link, Artist.genres, Artist.city,
    Artist.state, Artist.phone, Artist.description, Artist.facebook_link,
    Artist.website_link, Artist.looking_for_venue, Venue.id.label('venue_id'),
    Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link'), Show.start_time,
    func.sum(case((Show.start_time >= date.today(), 1), else_=0)).label('upcoming_show_count'),
    func.sum(case((Show.start_time < date.today(), 1)), else_=0).label('past_show_count'),
  ).filter(Artist.id == artist_id).filter(
    or_(Show.start_time >= date.today(), Show.start_time < date.today(), Show.start_time.is_(None))
  ).group_by(
    Artist.id, Venue.id, Show.start_time
  )
  data = {
    "id": "",
    "name": "",
    "genres": "",
    "city": "",
    "state": "",
    "phone": "",
    "website": "",
    "facebook_link": "",
    "seeking_venue": False,
    "seeking_description": "",
    "image_link": "",
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
    "upcoming_shows": [],
    "past_shows": [],
  }
  if len(query.all()) > 0:
    for result in query:
      data["id"] = result.id
      data["name"] = result.name
      data["genres"] = list(result.genres.split("_"))
      data["city"] = result.city
      data["state"] = result.state
      data["phone"] = result.phone
      data["website"] = result.website_link
      data["facebook_link"] = result.facebook_link
      data["seeking_venue"] = result.looking_for_venue
      data["seeking_description"] = result.description
      data["image_link"] = result.image_link
      if result.upcoming_show_count > 0:
        data['upcoming_shows_count'] += result.upcoming_show_count
        data['upcoming_shows'].append({
          "venue_id": result.venue_id,
          "venue_name": result.venue_name,
          "venue_image_link": result.venue_image_link,
          "start_time": str(result.start_time)
        })
      if result.past_show_count != None and result.past_show_count > 0:
        data['past_shows_count'] += result.past_show_count
        data['past_shows'].append({
          "venue_id": result.venue_id,
          "venue_name": result.venue_name,
          "venue_image_link": result.venue_image_link,
          "start_time": str(result.start_time)
        })
  else:
    query = Artist.query.filter_by(id = artist_id).all()
    for result in query:
      data["id"] = result.id
      data["name"] = result.name
      data["genres"] = list(result.genres.split("_"))
      data["city"] = result.city
      data["state"] = result.state
      data["phone"] = result.phone
      data["website"] = result.website_link
      data["facebook_link"] = result.facebook_link
      data["seeking_venue"] = result.looking_for_venue
      data["seeking_description"] = result.description
      data["image_link"] = result.image_link
 
  return render_template('pages/show_artist.html', artist=data)

#  Update Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  query =  Artist.query.filter_by(id = artist_id).first()
  print(query)
  artist = {
      "id": query.id,
      "name": query.name,
      "genres": list(query.genres.split("_")),
      "city": query.city,
      "state": query.state,
      "phone": query.phone,
      "website_link": query.website_link,
      "facebook_link": query.facebook_link,
      "seeking_venue": query.looking_for_venue,
      "seeking_description": query.description,
      "image_link": query.image_link,
  }
  form = ArtistForm(**artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  error = False
  print(form.seeking_venue.data)
  if form.validate():
    genres = '_'.join(map(str, form.genres.data))
    try:
      artist =  Artist.query.get(artist_id)
      artist.name = form.name.data,
      artist.description = form.seeking_description.data,
      artist.genres = genres,
      artist.city = form.city.data,
      artist.state = form.state.data,
      artist.phone = form.phone.data,
      artist.image_link = form.image_link.data,
      artist.facebook_link = form.facebook_link.data,
      artist.website_link = form.website_link.data,
      artist.looking_for_venue = form.seeking_venue.data
      db.session.commit()
      
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] +
            ' was successfully updated.')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be updated with new value.')
    finally:
      db.session.close()
  
  if error:
   abort(400)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  error = False
  if form.validate():
    genres = '_'.join(map(str, form.genres.data))
    try:
      artist = Artist(
        name=form.name.data,
        description=form.seeking_description.data,
        genres=genres,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        looking_for_venue=form.seeking_venue.data,
      )
      db.session.add(artist)
      db.session.commit()
      # called upon submitting the new artist listing form
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion

      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
      flash('An error occurred. Artist ' +
          request.form['name'] + ' could not be listed.')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
      db.session.close()
    
  if error:
    abort(400)
  else:
    return render_template('pages/home.html')
  

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/delete/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  name = ""
  try:
    artist = Artist.query.get(artist_id)
    name = artist.name
    db.session.delete(artist)
    db.session.commit()
    
    flash('Artist ' + name +
            ' was successfully deleted.')
  except:
    db.session.rollback()
    print(sys.exc_info())
    
    flash('An error occurred. Artist ' +
            name + ' could not be deleted.')
  finally:
    db.session.rollback()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))
  # return render_template('pages/home.html')
  
  
  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  query = Show.query.join(Venue, isouter=True).join(Artist, Artist.id ==  Show.artist_id).with_entities(
    Show.id, Show.venue_id, Show.artist_id, Show.start_time,
    Venue.name.label('venue_name'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'),
  ).group_by(
    Show.id, Venue.id, Artist.id,
  )
    
  data = []
  for result in query:
    data.append({
      "venue_id": result.venue_id,
      "venue_name": result.venue_name,
      "artist_id": result.artist_id,
      "artist_name": result.artist_name,
      "artist_image_link": result.artist_image_link,
      "start_time": str(result.start_time)
    })
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  error = False
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    # db.engine.execute(
    #   "INSERT INTO shows(artist_id, venue_id, start_time) VALUES(%s, %s, %s);",
    #   (form.artist_id.data, form.venue_id.data, form.start_time.data)
    # )
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  
  if error:
    abort(400)
  else:
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
