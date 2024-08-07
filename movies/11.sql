SELECT title as 'top 5 movies starring Chadwick Boseman'
FROM movies INNER JOIN ratings ON movies.id=ratings.movie_id WHERE id IN
(SELECT movie_id FROM stars INNER JOIN people ON people.id=stars.person_id WHERE name = 'Chadwick Boseman')
ORDER BY rating DESC
LIMIT 5;
