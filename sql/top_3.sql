SELECT "go".score,  "i".player, DATE("go".time)
FROM game_overs "go"
INNER JOIN initializations "i"
ON "go".game_id = "i".game_id
ORDER BY score DESC
LIMIT 3;