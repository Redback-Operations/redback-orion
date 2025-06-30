from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
from datetime import datetime

# Function to be executed in the virtual environment
def hello_world():
    print("Hello, World!")

# Define the DAG
with DAG(
    dag_id="venv_example_dag",
    schedule_interval=None,  # Manual trigger
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

    # Task to create a virtual environment and execute the function
    create_venv_task = PythonVirtualenvOperator(
        task_id="create_venv_and_hello_world",
        python_callable=hello_world,
        requirements="requirements.txt",  # Path to your requirements.txt
        system_site_packages=False,  # Isolate the virtual environment
    )

    create_venv_task