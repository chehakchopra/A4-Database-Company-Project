DROP TABLE IF EXISTS app_user;
DROP INDEX IF EXISTS idx_employee_name;
DROP INDEX IF EXISTS idx_workson_pno;

CREATE TABLE app_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer'
);

INSERT INTO app_user (username, password_hash, role)
VALUES
    ('admin', 'scrypt:32768:8:1$PhncmQzv0oxH1KfF$e603eba9106c933b1d516ba61b73c94ff82e31b0cf1dcfedb33e506e4481bfeb45644d7523e361409ca119e98c89d5b1b8cb1191fae2f285ee59c3bf2890e095', 'admin');

CREATE INDEX idx_employee_name ON Employee (Lname, Fname);
CREATE INDEX idx_workson_pno ON Works_On (Pno);