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
from sqlalchemy import distinct
import datetime
import sys
from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # DONE
  
    data = []

    try:
      venue_areas = db.session.query(distinct(Venue.city), Venue.state).all()
      current_time = datetime.datetime.now()

      for area in venue_areas:
          city = area[0]
          state = area[1]
          area_data = {"city": city, "state": state, "venues": []}
          venues = Venue.query.filter_by(city=city, state=state).all()

          for venue in venues:
              venue_name = venue.name
              venue_id = venue.id

              upcoming_shows = (
                  Show.query.filter_by(venue_id=venue_id).filter(Show.start_time > current_time).all()
              )

              venue_data = {
                  "id": venue_id,
                  "name": venue_name,
                  "num_upcoming_shows": len(upcoming_shows),
              }

              area_data["venues"].append(venue_data)

          data.append(area_data)

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong.")
        return render_template("pages/home.html")

    finally:
        return render_template("pages/venues.html", areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # DONE

    response = {}
    search = "%{}%".format(request.form.get('search_term', ''))
    result = Venue.query.filter(Venue.name.ilike(search)).all()
    response['data'] = result
    response['count'] = len(result)
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # DONE

    venue = Venue.query.get(venue_id)
    shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).all()
    past_shows = []
    upcoming_shows = []
    current_time = datetime.datetime.now()

    for show in shows:
      data = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
          }
      if show.start_time > current_time:
        upcoming_shows.append(data)
      else:
        past_shows.append(data)

    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "genres": venue.genres,
      "seeking_talent": venue.seeking_talent,
      "seeking_description":venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
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
  error = False


  try:

    newVenue = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      image_link = request.form['image_link'],
      seeking_description = request.form['seeking_description']
      )

    db.session.add(newVenue)
    db.session.commit()

 


  except:
    db.session.rollback()
    error = True
    print(sys.exc_info)
   
   


  finally:


    db.session.close()
    if error:
        flash('Something wenty wrong. Venue ' + request.form['name'] + ' Could not be listed!')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')




    





  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # DONE

  return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    vName = venue.name
    db.session.delete(venue)
    db.session.commit()
    flash('Venue' + vName + 'deleted successfully')
  
  
  except:
    db.session.rollback()
    flash('Something went wrong, please try again')
  
  
  finally:
    db.session.close()

  return None 
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # DONE
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # Done
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  search = "%{}%".format(request.form.get('search_term', ''))
  result = Artist.query.filter(Artist.name.ilike(search)).all()
  response['data'] = result
  response['count'] = len(result)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# DONE

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # DONE
  artist = Artist.query.get(artist_id)
  shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).all()
  past_shows = []
  upcoming_shows = []
  current_time = datetime.datetime.now()

  for show in shows:
    data = {
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
    if show.start_time > current_time:
      upcoming_shows.append(data)
    else:
      past_shows.append(data)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "genres": artist.genres,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "genres": artist.genres,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  # DONE
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_update = Artist.query.get(artist_id)
  artist_update.name = request.form['name']
  artist_update.city = request.form['city']
  artist_update.state = request.form['state']
  artist_update.genres = request.form['genres']
  artist_update.phone = request.form['phone']
  artist_update.facebook_link = request.form['facebook_link']
  artist_update.image_link = request.form['image_link']
  artist_update.website_link = request.form['website_link']
  artist_update.seeking_description = request.form['seeking_description']
  
  
  try:
    db.session.commit()
    flash("Successfully updated.")
  
  
  except:
    db.session.rollback()
    flash("Something went wrong, please try again.")
  
  
  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  data = {
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "genres": venue.genres,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue_update = Venue.query.get(venue_id)
  venue_update.name = request.form['name']
  venue_update.city = request.form['city']
  venue_update.state = request.form['state']
  venue_update.genres = request.form['genres']
  venue_update.assress = request.form['address']
  venue_update.phone = request.form['phone']
  venue_update.facebook_link = request.form['facebook_link']
  venue_update.image_link = request.form['image_link']
  venue_update.website_link = request.form['website_link']
  venue_update.seeking_description = request.form['seeking_description']
  
  
  
  try:
    db.session.commit()
    flash("Successfully updated.")
  
  
  except:
    db.session.rollback()
    flash("Something went wrong, please try again.")
  
  
  finally:
    db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False


  try:

    newArtist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      facebook_link = request.form['facebook_link'],
      image_link = request.form['image_link'],
      website_link = request.form['website_link'],
      seeking_description = request.form['seeking_description']
      )

    db.session.add(newArtist)
    db.session.commit()

 


  except:
    db.session.rollback()
    error = True
    print(sys.exc_info)
   
   


  finally:


    db.session.close()
    if error:
        flash('An error occured. Artist ' + request.form['name'] + ' Could not be listed!')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  

  return render_template('pages/home.html')
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # DONE
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # Done


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False


  try:

    newShow = Show(
      venue_id = request.form['venue_id'],
      artist_id = request.form['artist_id'],
      start_time = request.form['start_time']
      )

    db.session.add(newShow)
    db.session.commit()

 


  except:
    db.session.rollback()
    error = True
    #print(sys.exc_info)
   
   


  finally:


    db.session.close()
    if error:
        flash('An error occurred Show could not be listed!')
    else:
        flash('Show was successfully listed!')
  

  return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # Done

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
