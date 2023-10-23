CREATE TABLE Patients (
    PatientID int,
    FirstName varchar(50),
    LastName varchar(50),
    DateOfBirth datetime,
    Gender varchar(10),
    PRIMARY KEY (PatientID)
);

CREATE TABLE Doctors (
    DoctorID int,
    FirstName varchar(50),
    LastName varchar(50),
    Specialization varchar(50),
    PRIMARY KEY (DoctorID)
);

CREATE TABLE Prescriptions (
    PrescriptionID int,
    PatientID int,
    DoctorID int,
    DateIssued datetime,
    PRIMARY KEY (PrescriptionID)
);

CREATE TABLE Medications (
    MedicationID int,
    MedicationName varchar(50),
    Dosage varchar(50),
    PRIMARY KEY (MedicationID)
);

CREATE TABLE PrescriptionDetails (
    PrescriptionDetailID int,
    PrescriptionID int,
    MedicationID int,
    Quantity int,
    PRIMARY KEY (PrescriptionDetailID)
);