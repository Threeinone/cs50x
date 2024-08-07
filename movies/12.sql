SELECT title AS 'movies starring both Bradley Cooper and Jennifer Lawrence'
FROM movies WHERE id IN
(SELECT movie_id FROM stars INNER JOIN people ON stars.person_id=people.id WHERE name = 'Bradley Cooper' OR name = 'Jennifer Lawrence')
