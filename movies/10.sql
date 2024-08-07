SELECT name as '>=9.0 directors'
FROM people WHERE id IN
(SELECT person_id FROM movies INNER JOIN directors ON movies.id=directors.movie_id WHERE movie_id IN
  (SELECT movie_id FROM movies INNER JOIN ratings ON movies.id=ratings.movie_id WHERE rating >= 9.0))
