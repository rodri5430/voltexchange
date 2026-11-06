Código para criação das tabelas

1 - Utilizadores ("users")
CREATE TABLE TAM.users (
    id SERIAL PRIMARY KEY,
    nif INT(9) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
)

2 - Valor Sensor Temperatura (temp_readings)
CREATE TABLE TAM.temp_readings(
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES devices(id) ON DELETE CASCADE,
    temperature_value NUMERIC(5,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

3 - Dados de Acesso (acess_logs) 
CREATE TABLE TAM.access_logs (
    id SERIAL PRIMARY KEY,
    id_user INT REFERENCES users(id) ON DELETE CASCADE,
    ip_address VARCHAR(45),
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'success' -- ex: success, failed
);

4 - Comandos (commands)
CREATE TABLE TAM.commands (
    id SERIAL PRIMARY KEY,
    id_user INT REFERENCES users(id) ON DELETE SET NULL,
    id_device INT REFERENCES devices(id) ON DELETE CASCADE,
    command_text TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

5 - Estado de Alarme (alarm_states)

CREATE TABLE TAM.alarm_states (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

6 - Dispositivos (devices) (Vai estar associado a tabela de alarmes)    

CREATE TABLE TAM.device(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model VARCHAR(50),
    serial_number VARCAR(100) UNIQUE,
    id_estado INT REFERENCES alarm_states(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);