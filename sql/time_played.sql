SELECT i.init_time start_time, "go".time end_time, "go".time-i.init_time time_played, i.player
FROM initializations i
INNER JOIN game_overs "go"
ON i.game_id = "go".game_id;