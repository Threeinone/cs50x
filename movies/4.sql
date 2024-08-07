SELECT count(*) as '10/10 movies'
FROM movies INNER JOIN ratings ON movies.id=ratings.movie_id
WHERE ratings.rating = 10.0;
