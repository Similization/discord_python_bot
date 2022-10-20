CREATE DATABASE IF NOT EXISTS discord_bot;
USE discord_bot;

CREATE TABLE IF NOT EXISTS users
(
    id            bigint primary key auto_increment,
    name          varchar(45),
    discriminator varchar(8),
    mention       varchar(45)
);

CREATE TABLE IF NOT EXISTS bulls_and_cows
(
    id          bigint primary key auto_increment,
    user_id     bigint,
    game_result bool,
    time        time,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS guess_number
(
    id          bigint primary key auto_increment,
    user_id     bigint,
    game_result bool,
    FOREIGN KEY (user_id) REFERENCES users (id)
);


CREATE TABLE IF NOT EXISTS rock_paper_scissors
(
    id          bigint primary key auto_increment,
    user_id     bigint,
    game_result bool,
    move        ENUM('rock', 'paper', 'scissors'),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
