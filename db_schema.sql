-- =============================
-- USERS TABLE
-- =============================
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    last_login TIMESTAMP,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    birthdate DATE,
    email VARCHAR(254) UNIQUE,
    address TEXT,
    role VARCHAR(15) CHECK (role IN ('superadmin','admin','owner','renter')) DEFAULT 'renter' , 
    balance DECIMAL(12,2) NOT NULL DEFAULT 0,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- CARS TABLE
-- =============================
CREATE TABLE cars (
    car_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    owner_id INTEGER NOT NULL ,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    production_year INTEGER NOT NULL,
    color VARCHAR(20),
    seats INTEGER,
    category VARCHAR(20) CHECK (category IN ('sedan','suv','hatchback','truck','van')),
    only_with_driver BOOLEAN DEFAULT FALSE,
    with_driver BOOLEAN DEFAULT TRUE,
    gearbox VARCHAR(10) CHECK (gearbox IN ('manual','automatic')),
    fuel VARCHAR(10) CHECK (fuel IN ('gasoline','diesel','electric','hybrid')),
    fee DECIMAL(10,2) NOT NULL,
    max_days INTEGER NOT NULL DEFAULT 7 CHECK (max_days >= 1),
    status VARCHAR(15) CHECK (status IN ('available','suspended','unavailable')) DEFAULT 'available',
    country TEXT,
    province TEXT,
    city TEXT,
    description TEXT,
    image_path TEXT , 
    CONSTRAINT fk_car_owner
        FOREIGN KEY (owner_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE 
);

-- =============================
-- RENTS TABLE
-- =============================
CREATE TABLE rents (
    rent_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    car_id INTEGER NOT NULL ,
    renter_id INTEGER NOT NULL ,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pending payment','on your rent', 'not yet' , 'over')) DEFAULT 'pending payment',
    total_fee DECIMAL(10,2) , 
    CONSTRAINT fk_rent_car
        FOREIGN KEY (car_id)
        REFERENCES cars(car_id)
        ON DELETE CASCADE , 
    CONSTRAINT fk_rent_renter
        FOREIGN KEY (renter_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE 
);

-- =============================
-- PAYMENTS TABLE
-- =============================
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    rent_id INTEGER UNIQUE NOT NULL REFERENCES rents(rent_id) ON DELETE CASCADE,
    total_amount DECIMAL(10,2) NOT NULL,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(10) CHECK (method IN ('online','cash')),
    tracking_code VARCHAR(50),
    status VARCHAR(15) CHECK (status IN ('pending','successful','failed')) DEFAULT 'pending' , 
    CONSTRAINT fk_payment_rent
        FOREIGN KEY (rent_id)
        REFERENCES rents(rent_id)
        ON DELETE CASCADE 
);

-- =============================
-- REVIEWS TABLE
-- =============================
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    car_id INTEGER NOT NULL , 
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    comment TEXT, 
    CONSTRAINT fk_review_car
        FOREIGN KEY (car_id)
        REFERENCES cars(car_id)
        ON DELETE CASCADE , 
    CONSTRAINT fk_review_user 
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE 
);

-- =============================
-- SCORES TABLE
-- =============================
CREATE TABLE scores (
    score_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    car_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    score SMALLINT CHECK (score BETWEEN 1 AND 5) NOT NULL,
    CONSTRAINT fk_score_car
        FOREIGN KEY (car_id)
        REFERENCES cars(car_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_score_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT uq_score_car_user UNIQUE (car_id, user_id)
);

-- =============================
-- LOGINS TABLE
-- =============================
CREATE TABLE logins (
    login_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INTEGER NOT NULL,
    is_signup BOOLEAN NOT NULL,
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    CONSTRAINT fk_login_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE 
);
