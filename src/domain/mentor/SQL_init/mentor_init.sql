create type SENIORITY_LEVEL as enum('No reveal', 'junior', 'intermediate', 'senior', 'staff', 'manager');
create type CATEGORY as enum('No reveal', 'outdoor', 'indoor'); --這邊不知放啥
create type SCHEDULES_STATUS as enum('allow', 'forbidden'); --這邊不知放啥
create type ACCEPT_STATUS as enum('accept', 'pending', 'reject');
create type MEMBER_ROLE as enum('mentor', 'mentee');

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
    category CATEGORY NOT NULL,
    "order" INT NOT NULL,
    metadata JSONB
);

CREATE TABLE professions (
    professions_id SERIAL PRIMARY KEY,
    category CATEGORY DEFAULT 'No reveal',
    subject TEXT DEFAULT '',
    metadata JSONB
);

CREATE TABLE mentor_schedules (
    mentor_schedules_id SERIAL PRIMARY KEY,
    "type" SCHEDULES_STATUS DEFAULT 'allow',
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
    user_id CATEGORY NOT NULL,
    "role" MEMBER_ROLE NOT NULL,
    MESSAGE TEXT
);

CREATE TABLE reservations (
    reservations_id SERIAL PRIMARY KEY,
    mentor_id INT NOT NULL,
    mentee_id INT NOT NULL,
    start_datetime BIGINT,
    end_datetime BIGINT,
    my_status ACCEPT_STATUS,
    status ACCEPT_STATUS,
    "role" MEMBER_ROLE,
    message_from_others TEXT DEFAULT ''
);

CREATE INDEX reservations_index ON reservations(mentor_id, start_datetime, end_datetime);
