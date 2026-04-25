# Hacaton - Space for Water
### Team name: Poland can into space
### Project name: SwS - Space Water Solutions

## How to run a project 

### 1. Prerequisites
Ensure you have **Python** installed (download it from [python.org](https://www.python.org/downloads/)). 

**Important:** During installation, make sure to check the box **"Add Python to PATH"**.

### 2. Download the Project
Open your terminal (on Windows: Command Prompt / CMD) and type the following:
```bash
git clone https://github.com/AleksandraPonikowska/space-water-solutions
cd space-water-solutions
```
### 3. Environment configuration
#### A. Create a virtual environment

```bash
python -m venv .venv
```

### B. Activate the environment:

Windows:
```bash
.venv\Scripts\activate
```

Linux:
```bash
source .venv/bin/activate
```
### 4. Install necessary libraries
```bash
pip install -r requirements.txt
```

### 5. Setup Credentials
1. Create a new file named .env in the main folder of the project.
2. Open the file and paste your credentials in the following format:
```
SH_ID=your_client_id_here
SH_SECRET=your_client_secret_here
```
You can obtain these from [here](https://shapps.dataspace.copernicus.eu/dashboard/#/account/settings)
In "OAuth clients" add an client, for now leave the box unchecked 

### 6. Run the application :3
```bash
streamlit run app/main.py

# if not works 4u, try: python -m streamlit run app/main.py
```


## Mały poradnik git'a
Git jest prosty i nie należy się go bać
To używanie jakiś 4 komend na krzyż, jeśli się nic nie popsuje
Jak wam się coś popsuje to naprawię ja albo ja i kolega Geminiusz

Mamy nasze repozytorium, czyli wspólną wersję
Każdy z nas ma kopię na swoim komputrze

### Pobieranie aktualnej wersji projektu
```bash
git pull
```

### Dodanie swoich zmian i wysłanie ich na serwer
```
git pull 
git add .
git commit -m "Krótki opis zmiany"
git push
```
