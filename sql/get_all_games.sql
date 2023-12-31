SELECT i.player, "go".score, "go".collision_type, 
EXTRACT(EPOCH FROM ("go".time-i.init_time)) time_played, 
TO_CHAR("go".time , 'YYYY-MM-DD HH24:MI:SS')
FROM game_overs "go"
JOIN initializations i
ON "go".game_id = i.game_id
ORDER BY "go".score DESC;