import sqlite3
import os 

def execute_sql_commands(db_path, commands):
    """Executes SQL commands on a specified database.

    Args:
        db_path: Path to the SQLite database file.
        commands: A list of SQL commands (strings) to execute.
    """

    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        for command in commands:
            try:
                cursor.execute(command)
                connection.commit()  # Save changes (if needed)
                # Process results (if SELECT query):
                if command.lstrip().upper().startswith("SELECT"):
                    results = cursor.fetchall()
                    print(results)
            except sqlite3.Error as e:
                print(f"Error executing command '{command}': {e}")

def hrdb():

    #CREATE tables 'Empresa', 'Departamento', 'Cargo', 'AFP', 'Prevision', 'Colaborador', 'Nomina', 'Evaluacion', 'Capacitacion'.
    sql_create_commands = ['''
        CREATE TABLE Empresa (
            RUT VARCHAR(20) PRIMARY KEY,
            NombreEmpresa VARCHAR(100),
            Direccion VARCHAR(255),
            Telefono VARCHAR(20),
            Giro VARCHAR(100)  -- Industry (e.g., salmon farming, manufacturing, public institution)
        );

        CREATE TABLE Departamento (
            IdDepartamento INTEGER PRIMARY KEY AUTOINCREMENT,
            NombreDepartamento VARCHAR(100),
            RUT_Empresa VARCHAR(20),
            FOREIGN KEY (RUT_Empresa) REFERENCES Empresa(RUT)
        );

        CREATE TABLE Cargo (
            IdCargo INTEGER PRIMARY KEY AUTOINCREMENT,
            NombreCargo VARCHAR(100),
            Descripcion VARCHAR(255),
            IdDepartamento INTEGER,
            FOREIGN KEY (IdDepartamento) REFERENCES Departamento(IdDepartamento)
        );

        CREATE TABLE AFP (
            IdAFP INTEGER PRIMARY KEY AUTOINCREMENT,
            NombreAFP VARCHAR(100),
            ComisionPorcentaje DECIMAL(5,2)  -- Commission percentage deducted from gross salary
        );

        CREATE TABLE Prevision (
            IdPrevision INTEGER PRIMARY KEY AUTOINCREMENT,
            NombrePrevision VARCHAR(100),  -- Generic health plan name (e.g., Public or Private)
            TipoPrevision VARCHAR(50),  -- Either "Fonasa" or "Isapre"
            IdFonasa INTEGER,  -- Foreign key to the Fonasa table (nullable)
            IdIsapre INTEGER,  -- Foreign key to the Isapre table (nullable)
            PlanSalud DECIMAL(10,2),  -- Monetary value of the health plan
            FOREIGN KEY (IdFonasa) REFERENCES Fonasa(IdFonasa),
            FOREIGN KEY (IdIsapre) REFERENCES Isapre(IdIsapre)
        );

        CREATE TABLE Fonasa (
            IdFonasa INTEGER PRIMARY KEY AUTOINCREMENT,
            GrupoFonasa VARCHAR(50),  -- Fonasa group
            Cobertura DECIMAL(5,2)  -- Coverage percentage
        );
        
        CREATE TABLE Isapre (
            IdIsapre INTEGER PRIMARY KEY AUTOINCREMENT,
            NombreIsapre VARCHAR(100),  -- Isapre company name
            PlanPrivado DECIMAL(10,2),  -- Private insurance plan value
            CoberturaPrivada DECIMAL(5,2)  -- Private coverage percentage
        );

        CREATE TABLE Colaborador (
            RUT VARCHAR(20) PRIMARY KEY,
            Nombre VARCHAR(50),
            Apellido VARCHAR(50),
            FechaNacimiento DATE,  -- Date of Birth
            FechaIngreso DATE,  -- Date of employment start
            Telefono VARCHAR(20),
            Salario DECIMAL(10,2),  -- Salary in local currency
            Nacionalidad VARCHAR(50),
            IdDepartamento INTEGER,  -- Relates Colaborador to Departamento
            FOREIGN KEY (IdDepartamento) REFERENCES Departamento(IdDepartamento)
        );

        CREATE TABLE ColaboradorCargo (
            RUT_Colaborador VARCHAR(20),
            IdCargo INTEGER,
            PRIMARY KEY (RUT_Colaborador, IdCargo),
            FOREIGN KEY (RUT_Colaborador) REFERENCES Colaborador(RUT),
            FOREIGN KEY (IdCargo) REFERENCES Cargo(IdCargo)
        );

        CREATE TABLE Bonus (
            IdBonus INTEGER PRIMARY KEY AUTOINCREMENT,
            MontoBonus DECIMAL(10,2),
            Descripcion VARCHAR(255)
        );

        CREATE TABLE Bienestar (
            IdBienestar INTEGER PRIMARY KEY AUTOINCREMENT,
            AporteBienestar DECIMAL(10,2),
            Beneficios DECIMAL(10,2)
        );

        CREATE TABLE Remuneraciones (
            IdRemuneracion INTEGER PRIMARY KEY AUTOINCREMENT,
            FechaPago DATE,  -- Payment date
            MontoBruto DECIMAL(10,2),  -- Gross amount before deductions
            Impuesto DECIMAL(5,2),  -- Tax percentage
            MontoLiquido DECIMAL(10,2),  -- Net amount after all deductions
            RUT_Colaborador VARCHAR(20),
            IdAFP INTEGER,  -- Foreign key to AFP table
            IdPrevision INTEGER,  -- Foreign key to Prevision table
            IdBonus INTEGER,  -- Foreign key to Bonus table
            IdBienestar INTEGER,  -- Foreign key to Bienestar table
            FOREIGN KEY (RUT_Colaborador) REFERENCES Colaborador(RUT),
            FOREIGN KEY (IdAFP) REFERENCES AFP(IdAFP),
            FOREIGN KEY (IdPrevision) REFERENCES Prevision(IdPrevision),
            FOREIGN KEY (IdBonus) REFERENCES Bonus(IdBonus),
            FOREIGN KEY (IdBienestar) REFERENCES Bienestar(IdBienestar)
        );

        CREATE TABLE Vacaciones (
            IdVacacion INTEGER PRIMARY KEY AUTOINCREMENT,
            FechaInicio DATE,  -- Vacation start date
            FechaTermino DATE,  -- Vacation end date
            ColaboradorAntiguo BOOLEAN,  -- Employee eligible for more vacation days if 15+ years
            DiasAcumulados INT,  -- Accumulated vacation days
            DiasUsados INT,  -- Vacation days used
            RUT_Colaborador VARCHAR(20),
            FOREIGN KEY (RUT_Colaborador) REFERENCES Colaborador(RUT)
        );

        CREATE TABLE Evaluacion (
            IdEvaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
            Evaluador VARCHAR(100),  -- The evaluator, usually a direct manager in public sector
            FechaEvaluacion DATE,
            FactorEvaluacion DECIMAL(3,2),  -- Evaluation factor
            Calificacion VARCHAR(50),  -- "Bueno", "Regular", "Malo/deficiente"
            Comentarios VARCHAR(255),
            RUT_Colaborador VARCHAR(20),
            FOREIGN KEY (RUT_Colaborador) REFERENCES Colaborador(RUT)
        );

        CREATE TABLE Capacitacion (
            IdCapacitacion INTEGER PRIMARY KEY AUTOINCREMENT,
            FechaCapacitacion DATE,
            Curso VARCHAR(100),  -- Course name
            Calificacion DECIMAL(3,2),  -- Course grade
            Institucion VARCHAR(100),  -- Institution providing the course
            Comentarios VARCHAR(255),
            RUT_Colaborador VARCHAR(20),
            FOREIGN KEY (RUT_Colaborador) REFERENCES Colaborador(RUT)
        );
    ''']
    execute_sql_commands(database_file, sql_create_commands)

    #Fill tables with information using INSERT
    sql_insert_commands = []
    execute_sql_commands(database_file, sql_insert_commands)


if __name__ == "__main__":
    database_file = "hrsystem.db"  # Replace with your actual path
    # Remove database_file if exists
    os.remove(database_file) if os.path.exists(database_file) else None

    hrdb()
