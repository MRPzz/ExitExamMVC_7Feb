DROP TABLE IF EXISTS Compensations;
DROP TABLE IF EXISTS Claims;
DROP TABLE IF EXISTS Claimants;
DROP TABLE IF EXISTS Policies;
DROP TABLE IF EXISTS Users;


-- 1. ตารางผู้ขอเยียวยา
CREATE TABLE Claimants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    salary REAL NOT NULL,
    type TEXT NOT NULL
);

-- 2. ตารางคำขอเยียวยา
CREATE TABLE Claims (
    claim_id TEXT PRIMARY KEY,
    claimant_id INTEGER,
    request_date DATE DEFAULT CURRENT_DATE,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY(claimant_id) REFERENCES Claimants(id)
);

-- 3. ตารางผลการคำนวณ
CREATE TABLE Compensations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id TEXT,
    amount REAL NOT NULL,
    calc_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY(claim_id) REFERENCES Claims(claim_id)
);

-- 4. ตาราง Users (เชื่อมกับ Claimants)
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL, -- 'admin' หรือ 'citizen'
    claimant_id INTEGER,
    FOREIGN KEY(claimant_id) REFERENCES Claimants(id)
);

-- 5. ตารางนโยบาย
CREATE TABLE Policies (
    policy_id INTEGER PRIMARY KEY,
    max_amount REAL DEFAULT 20000,
    income_condition TEXT
);
INSERT INTO Policies (max_amount, income_condition) VALUES (20000, 'Standard Policy');


-- ==========================================
-- ข้อมูลตัวอย่าง (Seed Data)
-- ==========================================

-- 1. สร้างประชาชน 
INSERT INTO Claimants (first_name, last_name, salary, type) VALUES 
('สมชาย', 'ใจดี', 15000, 'General'),      -- ID 1
('สมศรี', 'ยากจน', 4000, 'LowIncome'),    -- ID 2
('บารมี', 'มั่งมี', 100000, 'HighIncome'), -- ID 3
('วิชัย', 'ขยัน', 45000, 'General'),       -- ID 4
('มานะ', 'อดทน', 6000, 'LowIncome');       -- ID 5

-- 2. สร้าง Users 
-- Admin
INSERT INTO Users (username, password, role, claimant_id) VALUES ('admin', '123', 'admin', NULL);

-- Users 
INSERT INTO Users (username, password, role, claimant_id) VALUES ('somchai', '123', 'citizen', 1); -- สมชาย
INSERT INTO Users (username, password, role, claimant_id) VALUES ('somsri', '123', 'citizen', 2);  -- สมศรี
INSERT INTO Users (username, password, role, claimant_id) VALUES ('baramee', '123', 'citizen', 3); -- บารมี
INSERT INTO Users (username, password, role, claimant_id) VALUES ('wichai', '123', 'citizen', 4);  -- วิชัย

-- 3. สร้างประวัติคำขอ 
INSERT INTO Claims (claim_id, claimant_id, request_date, status) VALUES ('81234567', 4, DATE('now'), 'Approved');
INSERT INTO Compensations (claim_id, amount, calc_date) VALUES ('81234567', 20000, DATE('now'));

INSERT INTO Claims (claim_id, claimant_id, request_date, status) VALUES ('89998887', 5, DATE('now'), 'Approved');
INSERT INTO Compensations (claim_id, amount, calc_date) VALUES ('89998887', 6500, DATE('now'));