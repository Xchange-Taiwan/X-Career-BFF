CREATE TYPE SENIORITY_LEVEL AS ENUM('NO_REVEAL', 'JUNIOR', 'INTERMEDIATE', 'SENIOR', 'STAFF', 'MANAGER');
CREATE TYPE INTEREST_CATEGORY AS ENUM('INTERESTED_POSITION', 'SKILL', 'TOPIC');
CREATE TYPE PROFESSION_CATEGORY AS ENUM('EXPERTISE', 'INDUSTRY');
CREATE TYPE EXPERIENCE_CATEGORY AS ENUM('WORK', 'EDUCATION', 'LINK');
CREATE TYPE SCHEDULE_TYPE AS ENUM('ALLOW', 'FORBIDDEN');
CREATE TYPE BOOKING_STATUS AS ENUM('ACCEPT', 'PENDING', 'REJECT');
CREATE TYPE ROLE_TYPE AS ENUM('MENTOR', 'MENTEE');

CREATE TABLE mentor_profile (
    user_id SERIAL PRIMARY KEY,
    "name" TEXT NOT NULL,
    avatar TEXT DEFAULT '',
    "location" TEXT DEFAULT '',
    "position" TEXT DEFAULT '',
    linkedin_profile TEXT DEFAULT '',
    personal_statement TEXT DEFAULT '',
    about TEXT DEFAULT '',
    company TEXT DEFAULT '',
    seniority_level SENIORITY_LEVEL NOT NULL,
    timezone INT DEFAULT 0,
    experience INT DEFAULT 0,
	industry INT,
    interested_positions JSONB,
    skills JSONB,
    topics JSONB,
    expertises JSONB
);

CREATE TABLE mentor_experiences (
    mentor_experiences_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL, --might include mentor or mentee?
    category PROFESSION_CATEGORY NOT NULL,
    "order" INT NOT NULL,
    mentor_experiences_metadata JSONB
);

CREATE TABLE professions (
    professions_id SERIAL PRIMARY KEY,
    profession_category PROFESSION_CATEGORY ,
    subject TEXT DEFAULT '',
    professions_metadata JSONB
);

CREATE TABLE mentor_schedules (
    mentor_schedules_id SERIAL PRIMARY KEY,
    "type" SCHEDULE_TYPE DEFAULT 'allow',
    "year" INT DEFAULT -1,
    "month" INT DEFAULT -1,
    day_of_month INT NOT NULL,
    day_of_week INT NOT NULL,
    start_time INT NOT NULL,
    end_time INT NOT NULL,
    cycle_start_date BIGINT,
    cycle_end_date BIGINT
);

CREATE INDEX mentor_schedule_index ON mentor_schedules("year", "month", day_of_month, day_of_week, start_time, end_time);

CREATE TABLE canned_message (
    canned_message_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    "role" ROLE_TYPE NOT NULL,
    MESSAGE TEXT
);

CREATE TABLE reservations (
    reservations_id SERIAL PRIMARY KEY,
    mentor_id INT NOT NULL,
    mentee_id INT NOT NULL,
    start_datetime BIGINT,
    end_datetime BIGINT,
    my_status BOOKING_STATUS ,
    status BOOKING_STATUS,
    "role" ROLE_TYPE,
    message_from_others TEXT DEFAULT ''
);

CREATE INDEX reservations_index ON reservations(mentor_id, start_datetime, end_datetime);

CREATE TABLE interests (
    id SERIAL PRIMARY KEY,
    category INTEREST_CATEGORY,
    subject TEXT,
    desc JSONB
);