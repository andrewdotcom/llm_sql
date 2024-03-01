#!/usr/bin/env python3

import sqlite3
import duckdb
import argparse
from openai import OpenAI
import sys

class DatabaseSchemaTool:
    def __init__(self, database_path, openai_api_key=None):
        self.database_path = database_path
        self.openai_api_key = openai_api_key
        self.db_schema_string = ""

        self.get_database_schema()

    def get_database_schema(self):

        sql = """SELECT 'CREATE TABLE ' || t.table_name || ' (' ||
            STRING_AGG(c.column_name || ' ' || c.data_type ||
                    CASE
                        WHEN c.character_maximum_length IS NOT NULL THEN '(' || c.character_maximum_length || ')'
                        ELSE ''
                    END, ', ') ||
            CASE
                WHEN COUNT(DISTINCT k.constraint_name) > 0 THEN ', PRIMARY KEY (' || STRING_AGG(c.column_name, ', ') || ')'
                ELSE ''
            END ||
            ');' AS create_statement
        FROM temp.information_schema.tables t
        LEFT JOIN temp.information_schema.columns c ON t.table_name = c.table_name
        LEFT JOIN temp.information_schema.key_column_usage k ON t.table_name = k.table_name AND c.column_name = k.column_name
        WHERE t.table_schema = 'main'
        GROUP BY t.table_name;"""

        connection = duckdb.connect(self.database_path)
        cursor = connection.cursor()

        output_string = ""

        duckdb.sql("INSTALL sqlite;")
        duckdb.sql("LOAD sqlite;")

        cursor.execute(sql)
        tables = cursor.fetchall()
        for table in tables:
            self.db_schema_string = output_string + "\n" + str(table[0])

        connection.close()
        print(output_string)

    def execute_sql_query(self, query):
        try:
            connection = duckdb.connect(self.database_path)
            connection.sql(query).show()

            print(f"SQL query executed in DuckDB: {query}")

        except duckdb.Error as e:
            print(f"Error executing SQL query: {e}")

    def openai_chat_prompt(self, prompt):
        if self.openai_api_key:

            client = OpenAI(
                base_url = 'http://localhost:11434/v1',
                api_key=self.openai_api_key, # required, but unused
            )

            response = client.chat.completions.create(
              model="duckdb-nsql",
              temperature = 0.1,
              messages=[
                {"role": "system", "content": f"Provided this schema:\n\n{self.db_schema_string}"},
                {"role": "user", "content": f"{prompt}"},
              ]
            )

            return response.choices[0].message.content.strip()
        else:
            print("API key not provided.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get the schema of a SQLite or DuckDB database.")
    parser.add_argument("database_path", help="Path to the database file")
    parser.add_argument("-p", "--prompt", help="Text prompt for OpenAI chat completion API")
    parser.add_argument("-e", "--execute-query", help="SQL query to execute on the database")
    parser.add_argument("-er", "--execute-response", action="store_true", default=None, help="execute the SQL query provided by the llm")

    args = parser.parse_args()

    if args.database_path:
        schema_tool = DatabaseSchemaTool(args.database_path, "ollama")

        if args.execute_query:
                schema_tool.execute_sql_query(args.execute_query)

        if args.prompt:
            llm_response = schema_tool.openai_chat_prompt(args.prompt)
            print("\nModel Response:")
            print(llm_response)
            #Danger Will Robinson
            if args.execute_response:
                schema_tool.execute_sql_query(llm_response)
        else:
            print("No prompt")
    else:
        sys.exit()
