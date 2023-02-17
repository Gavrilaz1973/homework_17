# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


"""определяем поля для схемы"""
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description =fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

api = Api(app)
movie_ns = api.namespace('movies')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


#класс для /movies
@movie_ns.route('/')
class MoviesView(Resource):


#все фильмы, выбор по режиссеру и жанру
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movies = Movie.query.filter(Movie.director_id == director_id)
        elif genre_id:
            movies = Movie.query.filter(Movie.genre_id == genre_id)
        else:
            movies = Movie.query.all()
        return movies_schema.dump(movies), 200

#новый фильм
    def post(self):
        movie_jsn = request.json
        movie_new = Movie(**movie_jsn)
        db.session.add(movie_new)
        db.session.commit()
        return "", 201


#класс по ID фильма
@movie_ns.route('/<int:uid>')
class MoviesView(Resource):


#выбор фильма по id
    def get(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return "", 404
        return movie_schema.dump(movie), 200


#изменения в фильме
    def put(self, uid):
        movie_jsn = request.json
        movie_put = Movie.query.get(uid)
        if not movie_put:
            return "", 404
        movie_put.title = movie_jsn.get('title')
        movie_put.description = movie_jsn.get('description')
        movie_put.trailer = movie_jsn.get('trailer')
        movie_put.year = movie_jsn.get('year')
        movie_put.rating = movie_jsn.get('rating')
        movie_put.genre_id = movie_jsn.get('genre_id')
        movie_put.director_id = movie_jsn.get('director_id')
        db.session.add(movie_put)
        db.session.commit()
        return "", 204


#удаление фильма
    def delete(self, uid):
        movie_del = Movie.query.get(uid)
        if not movie_del:
            return "", 404
        db.session.delete(movie_del)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
