create type SENIORITY_LEVEL as enum('No reveal', 'junior', 'intermediate', 'senior', 'staff', 'manager');
create type INTEREST_CATEGORY as enum('interested_position', 'skill', 'topic');
create type PROFESSION_CATEGORY as enum('expertise', 'industry');
create type EXPERIENCE_CATEGORY as enum('work', 'education', 'link');
create type SCHEDULE_TYPE as enum('allow', 'forbidden');
create type BOOKING_STATUS as enum('accept', 'pending', 'reject');
create type ROLE_TYPE as enum('mentor', 'mentee');

CREATE TABLE mentor_profile (
    mentor_id SERIAL PRIMARY KEY,
    "name" TEXT NOT NULL,
    avatar TEXT DEFAULT '',
    "location" TEXT DEFAULT '',
    industry TEXT DEFAULT '',
    "position" TEXT DEFAULT '',
    linkedin_profile TEXT DEFAULT '',
    personal_statement TEXT DEFAULT '',
    about TEXT DEFAULT '',
    seniority_level SENIORITY_LEVEL NOT NULL,
    timezone INT DEFAULT 0,
    experience INT DEFAULT 0,
    interested_positions JSONB,
    skills JSONB,
    topics JSONB,
    expertises JSONB
);

CREATE TABLE mentor_experiences (
    experiences_id SERIAL PRIMARY KEY,
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
    "type" SCHEDULES_TYPE DEFAULT 'allow',
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
