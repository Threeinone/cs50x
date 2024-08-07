SELECT songs.name AS song 
FROM songs INNER JOIN artists ON songs.artist_id=artists.id
WHERE song LIKE '%feat.%';
