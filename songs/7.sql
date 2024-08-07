SELECT AVG(energy) AS 'avg energy from Drake'
FROM songs INNER JOIN artists ON songs.artist_id=artists.id
WHERE artists.name = 'Drake';
