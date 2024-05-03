CREATE TABLE mentor_profile (
    mentor_id SERIAL PRIMARY KEY,
    personal_statement TEXT,
    seniority_level TEXT,
    about TEXT
);


CREATE TABLE mentor_expertises (
    expertises_id SERIAL PRIMARY KEY,
    expertises TEXT,
    industry TEXT
);


CREATE TABLE mentor_expertises_inter (
    expertises_id INTEGER REFERENCES mentor_expertises(expertises_id),
    mentor_id INTEGER REFERENCES mentor_profile(mentor_id),
    PRIMARY KEY (expertises_id, mentor_id)
);