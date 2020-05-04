#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

#TODO:connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.create_all()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))

    
    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    venue_name = db.relationship('Venue', backref=db.backref('shows'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows'))

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    
    # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]

  venue_location = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  for city in venue_location:
      city_venues = db.session.query(Venue.id, Venue.name).filter(Venue.city == city).filter(Venue.state == city)
      data.append({
        "city": venue_location.city,
        "state": venue_location.state,
        "venues": city_venues
      })
  return render_template('pages/venues.html', areas=data);

#  Search Venue
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
    
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  search_venue = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []

  for venue in search_venue:
      data.append({
        "id": venue.id,
        "name": venue.name,
        
      })

  response={
        "count": len(search_venue),
        "data": data
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
      # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  shows_list = db.session.query(Show).filter(Show.venue_id == venue_id)
  past_shows = []
  upcoming_shows = []

  for show in shows_list:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id)
    add_shows = {
        "artist_id": artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    if show.start_time < datetime.now():
       
        past_shows.append(add_shows)
    else:
        upcoming_shows.append(add_shows)

  data = {
      "id": venue.id,
      "name": venue.name,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "genres": venue.genres,
      "website": venue.website,
      "image_link": venue.image_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
     # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
    
  form = VenueForm(request.form)

  venue = Venue(
    name = form.name.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website.data,
    genres = form.genres.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
   
  )
  try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was added successfully!')
 
# TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
      flash('An error has occured !. Venue ' + form.name.data + ' was not added successfully !')
  finally:
      db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def venue_edit(venue_id):
     # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
    form = VenueForm()
   
        venue_edit = Venues.query.get(venue_id)  
        venue_edit.name = form.name.data,
        venue_edit.genres= form.genres.data,
        venue_edit.address= form.address.data,
        venue_edit.city= form.city.data,
        venue_edit.state= form.state.data,
        venue_edit.phone= form.phone.data,
        venue_edit.website= form.website.data,
        venue_edit.facebook_link= form.facebook_link.data,
        venue_edit.seeking_talent= form.seeking_talent.data,
        venue_edit.seeking_description= form.seeking_description.data,
        venue_edit.image_link= form.image_link.data
   
        db.session.add(venue_edit)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except: 
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' was not succesfully updated. ')

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
     # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist.id, Artist.name).all()
 
  
  return render_template('pages/artists.html', artists=data)


# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
    data = []

    for artist in search_artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            
        })
    response={
        "count": len(search_artists),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Show Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
     # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

    shows_list = db.session.query(Show).filter(Show.artist_id == artist_id)
    past_shows = []
    upcoming_shows = []

    for show in shows_list:
        venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()

        show_add = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
            }

        if (show.start_time < datetime.now()):
           
            past_shows.append(add_shows)
        else:
            
            upcoming_shows.append(add_shows)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
    
     # TODO: populate form with fields from artist with ID <artist_id>

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
     # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    
    try:

    form = ArtistForm(request.form)
        edit_artist.name: form.name.data,
        edit_artist.address: form.address.data,
        edit_artist.city: form.city.data,
        edit_artist.state: form.state.data,
        edit_artist.phone: form.phone.data,
        edit_artist.website: form.website.data,
        edit_artist.genres: form.genres.data,
        edit_artist.facebook_link: form.facebook_link.data,
        edit_artist.seeking_venue: form.seeking_venue.data,
        edit_artist.seeking_description: form.seeking_description.data,
        edit_artist.image_link: form.image_link.data,
    

    db.session.add(edit_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + request.form['genres] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + request.form['genres] +' was not succesfully updated ! ')

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))
    
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
     # on successful db insert, flash success
    form = ArtistForm(request.form)

    artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data,
        website = form.website.data,
        facebook_link = form.facebook_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data,
        image_link = form.image_link.data,
    )
    try:
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully added !')
        # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    except:
        flash('An error occurred. Artist ' + form.name.data + 'was not succesfully added !')
    finally:
        db.session.close()
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
     # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    

   shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()
  for show, venue, artist in shows:
        data.append({
            "venue_id": venue_id,
            "venue_name": venue.name,
            "artist_id": artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image.link,
            "start_time": str(show[1])
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
     # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
    form = ShowForm()

    show = Show(
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data
    )

    try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully added')
        # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        flash('Error! Show could not be added')
    finally:
        db.session.close()
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
