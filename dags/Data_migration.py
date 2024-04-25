from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import psycopg2
import psycopg2.extras
from psycopg2 import sql

def transfer_data():
    src_conn = psycopg2.connect("dbname=db1 user=user1 password=password1 host=postgres-5433 port=5432")
    src_cursor = src_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    tgt_conn = psycopg2.connect("dbname=db2 user=user2 password=password2 host=postgres-5434 port=5432")
    tgt_cursor = tgt_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    table_names = ['customers', 'orders']

    for table_name in table_names:
        src_cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
        rows = src_cursor.fetchall()

        for row in rows:
            cols = list(row.keys())
            values = [row[col] for col in cols]
            
            insert_query = sql.SQL("""
                INSERT INTO {} ({}) VALUES ({})
                ON CONFLICT (id) DO UPDATE SET {}
            """).format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, cols)),
                sql.SQL(', ').join(sql.Placeholder() * len(cols)),
                sql.SQL(', ').join([
                    sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col))
                    for col in cols if col != 'id'
                ])
            )
            
            tgt_cursor.execute(insert_query, values)
            tgt_conn.commit()

    src_cursor.close()
    tgt_cursor.close()
    src_conn.close()
    tgt_conn.close()


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}

dag = DAG(
    'transfer_data_dag',
    default_args=default_args,
    description='DAG for incremental data transfer from one PostgreSQL to another',
    schedule_interval=timedelta(seconds=20),  # Ejecutar cada 20 segundos
    start_date=days_ago(1),
    tags=['example'],
)

t1 = PythonOperator(
    task_id='transfer_data',
    python_callable=transfer_data,
    dag=dag,
)
