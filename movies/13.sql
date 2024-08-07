SELECT name as 'stars alongside Kevin Bacon (b.y. 1958)'
FROM people INNER JOIN stars ON people.id=stars.person_id
WHERE movie_id IN
(SELECT movie_id FROM people INNER JOIN stars ON people.id=stars.person_id WHERE name = 'Kevin Bacon' AND birth = 1958)
AND name <> 'Kevin Bacon' --id NOT IN (SELECT id FROM people WHERE name = 'Kevin Bacon' AND birth = '1958')
