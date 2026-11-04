CREATE TABLE IF NOT EXISTS Admin (
    AdminID INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Coach (
    CoachID INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Client (
    ClientID INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    AdminID INT NOT NULL,
    FOREIGN KEY (AdminID) REFERENCES Admin(AdminID)
);

CREATE TABLE IF NOT EXISTS Record (
    RecordID INTEGER PRIMARY KEY,
    time VARCHAR(20) NOT NULL,
    date VARCHAR(20) NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled')),
    ClientID INT NOT NULL,
    AdminID INT NOT NULL,
    CoachID INT NOT NULL,
    FOREIGN KEY (ClientID) REFERENCES Client(ClientID),
    FOREIGN KEY (AdminID) REFERENCES Admin(AdminID),
    FOREIGN KEY (CoachID) REFERENCES Coach(CoachID)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_coach_slot
ON Record(CoachID, date, time)
WHERE status = 'active';
