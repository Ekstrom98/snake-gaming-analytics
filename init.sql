CREATE TABLE IF NOT EXISTS initializations (
id SERIAL PRIMARY KEY,
game_id varchar(64),
player varchar(50),
screen_width smallint,
screen_height smallint,
platform varchar(7),
init_time timestamp
);

CREATE TABLE IF NOT EXISTS food_positions (
id SERIAL PRIMARY KEY,
game_id varchar(64),
food_x smallint,
food_y smallint,
time timestamp
);

CREATE TABLE IF NOT EXISTS snake_head_positions (
id SERIAL PRIMARY KEY,
game_id varchar(64),
head_x smallint,
head_y smallint,
time timestamp
);

CREATE TABLE IF NOT EXISTS events (
id SERIAL PRIMARY KEY,
game_id varchar(64),
event_key int,
time timestamp
);

CREATE TABLE IF NOT EXISTS scores (
id SERIAL PRIMARY KEY,
game_id varchar(64),
score smallint,
time timestamp
);

CREATE TABLE IF NOT EXISTS game_overs (
id SERIAL PRIMARY KEY,
game_id varchar(64),
collision_type varchar(8),
score smallint,
time timestamp
);