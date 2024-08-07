SELECT AVG(ratings.rating) AS 'average ratings for 2012'
FROM movies INNER JOIN ratings ON movies.id=ratings.movie_id
WHERE movies.year = 2012;
