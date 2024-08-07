SELECT people.name AS 'toy story stars'
FROM people WHERE people.id IN
(SELECT person_id FROM movies INNER JOIN stars ON movies.id=stars.movie_id WHERE title = 'Toy Story')
