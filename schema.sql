-- ==========================================
-- 1. สร้างโครงสร้างตาราง (Table Schema)
-- ==========================================

-- ตารางแอดมิน (ตามข้อ 6 Authentication)
CREATE TABLE admins (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

-- ตารางนักเรียน (ตามข้อ 2)
CREATE TABLE students (
    id TEXT PRIMARY KEY, -- รหัส 8 หลัก เริ่มต้น 69xxxxxx
    prefix TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    dob DATE NOT NULL,   -- ใช้คำนวณอายุ (ข้อ 4: ต้อง >= 15 ปี)
    school TEXT NOT NULL,
    email TEXT NOT NULL,
    curriculum_id TEXT NOT NULL,
    password TEXT DEFAULT '1234' -- รหัสผ่านเบื้องต้น
);

-- ตารางรายวิชา (ตามข้อ 2)
CREATE TABLE subjects (
    id TEXT PRIMARY KEY, -- รหัส 8 หลัก เริ่ม 0550 (คณะ) หรือ 9069 (GenEd)
    name TEXT NOT NULL,
    credit INTEGER NOT NULL CHECK (credit > 0),
    instructor TEXT NOT NULL,
    prerequisite_id TEXT -- รหัสวิชาบังคับก่อน (ถ้ามี)
);

-- ตารางโครงสร้างหลักสูตร (ตามข้อ 2: เฉพาะปี 1)
CREATE TABLE subject_structure (
    curriculum_id TEXT NOT NULL, -- รหัส 8 หลัก ตัวแรกไม่เป็น 0
    curriculum_name TEXT NOT NULL,
    department TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

-- ตารางลงทะเบียนเรียน (ตามข้อ 2)
CREATE TABLE registered_subjects (
    student_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    grade TEXT CHECK (grade IN ('A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F', NULL)),
    PRIMARY KEY (student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

-- ==========================================
-- 2. ข้อมูลตัวอย่าง (Sample Data - ข้อ 5)
-- ==========================================

-- 2.1 แอดมิน (1 คน)
INSERT INTO admins VALUES ('admin', 'admin123');

-- 2.2 รายวิชา (12 วิชา >= 10 วิชา)
-- หมวดวิชาคอมพิวเตอร์ (คณะ 0550)
INSERT INTO subjects VALUES ('05506001', 'Intro to Computer Science', 3, 'Dr. Alan', NULL);
INSERT INTO subjects VALUES ('05506002', 'Computer Programming I', 3, 'Dr. Bell', NULL);
INSERT INTO subjects VALUES ('05506003', 'Computer Programming II', 3, 'Dr. Bell', '05506002'); -- มี Prereq
INSERT INTO subjects VALUES ('05506004', 'Discrete Mathematics', 3, 'Dr. Carl', NULL);
INSERT INTO subjects VALUES ('05506005', 'Data Structures', 3, 'Dr. Dave', '05506003'); -- มี Prereq ซ้อน
INSERT INTO subjects VALUES ('05506006', 'Web Technology', 3, 'Dr. Eve', NULL);

-- หมวดวิชาวิทยาศาสตร์ทั่วไป (คณะ 0550)
INSERT INTO subjects VALUES ('05501001', 'General Biology I', 3, 'Dr. Frank', NULL);
INSERT INTO subjects VALUES ('05501002', 'General Biology II', 3, 'Dr. Frank', '05501001'); -- มี Prereq
INSERT INTO subjects VALUES ('05502001', 'General Chemistry', 3, 'Dr. George', NULL);

-- หมวดวิชาศึกษาทั่วไป (GenEd 9069)
INSERT INTO subjects VALUES ('90690001', 'English for Communication', 2, 'Aj. Helen', NULL);
INSERT INTO subjects VALUES ('90690002', 'Academic English', 2, 'Aj. Helen', '90690001'); -- มี Prereq
INSERT INTO subjects VALUES ('90690003', 'Thai Society', 2, 'Aj. Ivan', NULL);

-- 2.3 โครงสร้างหลักสูตร (2 หลักสูตร, เทอมละ >= 3 วิชา)
-- หลักสูตร 1: Computer Science (10000001)
INSERT INTO subject_structure VALUES ('10000001', 'Computer Science', 'CS Dept', '05506001', 1);
INSERT INTO subject_structure VALUES ('10000001', 'Computer Science', 'CS Dept', '05506002', 1); -- Prog I
INSERT INTO subject_structure VALUES ('10000001', 'Computer Science', 'CS Dept', '90690001', 1); -- Eng I
INSERT INTO subject_structure VALUES ('10000001', 'Computer Science', 'CS Dept', '05506004', 1);
-- เทอม 2
INSERT INTO subject_structure VALUES ('10000001', 'Computer Science', 'CS Dept', '05506003', 2); -- Prog II (ต้องผ่าน Prog I)
INSERT INTO subject_structure VALUES ('10000001', 'Computer Science', 'CS Dept', '05506006', 2);
INSERT INTO subject_structure VALUES ('10000001', 'Computer Science', 'CS Dept', '90690002', 2); -- Eng II

-- หลักสูตร 2: Applied Biology (20000001)
INSERT INTO subject_structure VALUES ('20000001', 'Applied Biology', 'Bio Dept', '05501001', 1); -- Bio I
INSERT INTO subject_structure VALUES ('20000001', 'Applied Biology', 'Bio Dept', '05502001', 1);
INSERT INTO subject_structure VALUES ('20000001', 'Applied Biology', 'Bio Dept', '90690001', 1);
INSERT INTO subject_structure VALUES ('20000001', 'Applied Biology', 'Bio Dept', '90690003', 1);
-- เทอม 2
INSERT INTO subject_structure VALUES ('20000001', 'Applied Biology', 'Bio Dept', '05501002', 2); -- Bio II (ต้องผ่าน Bio I)
INSERT INTO subject_structure VALUES ('20000001', 'Applied Biology', 'Bio Dept', '90690002', 2);
INSERT INTO subject_structure VALUES ('20000001', 'Applied Biology', 'Bio Dept', '05506001', 2);

-- 2.4 นักเรียน (10 คน)
-- สมมติวันปัจจุบันคือปี 2026 (เพื่อให้คำนวณอายุได้ถูกต้องตาม Business Rules)
-- อายุ 15 ปี = เกิดปี 2011 หรือก่อนหน้า

-- คนที่ 1: ปกติ (CS)
INSERT INTO students VALUES ('69000001', 'นาย', 'สมชาย', 'ใจดี', '2010-01-01', 'รร.กทม', 's1@demo.com', '10000001', '1234');
-- คนที่ 2: ปกติ (CS)
INSERT INTO students VALUES ('69000002', 'น.ส.', 'สมหญิง', 'รักเรียน', '2010-05-20', 'รร.ตจว', 's2@demo.com', '10000001', '1234');
-- คนที่ 3: ปกติ (Bio)
INSERT INTO students VALUES ('69000003', 'นาย', 'เก่ง', 'กล้า', '2009-02-14', 'รร.สาธิต', 's3@demo.com', '20000001', '1234');
-- คนที่ 4: *** อายุไม่ถึง 15 ปี (สำหรับ Test Rule) เกิด 2013 = อายุ 13 ***
INSERT INTO students VALUES ('69000004', 'ด.ญ.', 'น้อย', 'หน่า', '2013-01-01', 'รร.อนุบาล', 's4@demo.com', '10000001', '1234');
-- คนที่ 5-10: คละกันไป
INSERT INTO students VALUES ('69000005', 'นาย', 'หนึ่ง', 'สอง', '2008-11-11', 'รร.วัด', 's5@demo.com', '20000001', '1234');
INSERT INTO students VALUES ('69000006', 'น.ส.', 'มีนา', 'เมษา', '2009-03-03', 'รร.เอกชน', 's6@demo.com', '10000001', '1234');
INSERT INTO students VALUES ('69000007', 'นาย', 'อาทิตย์', 'จันทร์', '2009-04-04', 'รร.นานาชาติ', 's7@demo.com', '20000001', '1234');
INSERT INTO students VALUES ('69000008', 'น.ส.', 'จันทร์', 'อังคาร', '2009-05-05', 'รร.กทม', 's8@demo.com', '10000001', '1234');
INSERT INTO students VALUES ('69000009', 'นาย', 'พุธ', 'พฤหัส', '2009-06-06', 'รร.ตจว', 's9@demo.com', '20000001', '1234');
INSERT INTO students VALUES ('69000010', 'น.ส.', 'ศุกร์', 'เสาร์', '2009-07-07', 'รร.สาธิต', 's10@demo.com', '10000001', '1234');

-- 2.5 ข้อมูลการลงทะเบียน (เพื่อ Test Prerequisite Logic)

-- กรณี 1: นายสมชาย (69000001) ผ่าน Prog I (05506002) แล้วด้วยเกรด A -> ควรลง Prog II ได้
INSERT INTO registered_subjects VALUES ('69000001', '05506002', 'A');

-- กรณี 2: น.ส.สมหญิง (69000002) เคยเรียน Prog I แต่ได้เกรด F -> ไม่ควรลง Prog II ได้ (ติด Prereq)
INSERT INTO registered_subjects VALUES ('69000002', '05506002', 'F');

-- กรณี 3: นายเก่ง (69000003) ผ่าน Bio I แล้ว -> ควรลง Bio II ได้
INSERT INTO registered_subjects VALUES ('69000003', '05501001', 'B+');