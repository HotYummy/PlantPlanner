DROP TABLE IF EXISTS plants;

CREATE TABLE plants(
    name VARCHAR(100) NULL,
    latin_name VARCHAR(100) NULL,
    price VARCHAR(10) NULL,
    category VARCHAR(20) NULL,
    color VARCHAR(50) NULL,
    url VARCHAR(200) NULL,
    flowering_season VARCHAR(100) NULL,
    min_height VARCHAR(5) NULL,
    max_height VARCHAR(5) NULL,
    light VARCHAR(50) NULL,
    image VARCHAR(400) NULL
);