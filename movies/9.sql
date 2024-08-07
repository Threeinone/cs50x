SELECT name as '2004 stars'
FROM people WHERE id IN
(SELECT person_id FROM movies INNER JOIN stars ON movies.id=stars.movie_id WHERE year = 2004)
ORDER BY birth;
