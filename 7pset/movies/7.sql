SELECT title, rating FROM ratings JOIN movies ON movie_id = id AND year = 2010 AND rating NOT NULL ORDER BY rating DESC, title ASC;