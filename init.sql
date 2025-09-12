    CREATE TABLE IF NOT EXISTS farm_data (
      id SERIAL PRIMARY KEY,
      soil_moisture DECIMAL(5, 2),
      air_temperature DECIMAL(5, 2),
      air_humidity DECIMAL(5, 2),
      ndvi DECIMAL(5, 2),
      health_status VARCHAR(255),
      insurance_risk VARCHAR(255),
      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
