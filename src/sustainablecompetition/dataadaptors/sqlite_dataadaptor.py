import polars as pl
import sqlite3
from typing import Optional

import polars as pl

from sustainablecompetition.dataadaptors.dataadaptor import DataAdaptor


__all__ = ["CsvDataAdaptor"]


class CsvDataAdaptor(DataAdaptor):
    """
    Implement the data adaptor for sqlite data.
    """

    def __init__(self, database_path: str):
        """
        Reads the database from sustainablecompetition package
        """
        
        self.database_path=database_path
        
        
    def get_performances(
        self,
        benchmark_id: Optional[str] = None,
        solver_id: Optional[str] = None,
        hardware_id: Optional[str] = None,
    ) -> pl.DataFrame:
        """
        Get as a DataFrame all performances for the specified benchmark_id, solver_id, and hardware_id.
        If none are specified, returns all the data (not recommended).

        Args:
            benchmark_id (str, optional): The id of the instance (inst_hash) to get the performances about.
            solver_id (str, optional): If set, only gives the performance with the specified solver_hash. Defaults to None.
            hardware_id (str, optional): If set, only gives the performance with the specified env_hash. Defaults to None.

        Returns:
            pl.DataFrame: A DataFrame containing the performances.
        """
        # Connect to the SQLite database (replace 'your_database.db' with your actual database file)
        conn = sqlite3.connect(self.database_path)

        # Build the base query
        query = """
            SELECT p.env_hash, p.inst_hash, p.solver_hash, p.performance, p.status,
                e.*, i.*, s.*
            FROM performances p
            LEFT JOIN environments e ON p.env_hash = e.env_hash
            LEFT JOIN instances i ON p.inst_hash = i.inst_hash
            LEFT JOIN solvers s ON p.solver_hash = s.solver_hash
        """

        # Add WHERE clauses based on provided arguments
        conditions = []
        if benchmark_id is not None:
            conditions.append(f"p.inst_hash = '{benchmark_id}'")
        if solver_id is not None:
            conditions.append(f"p.solver_hash = '{solver_id}'")
        if hardware_id is not None:
            conditions.append(f"p.env_hash = '{hardware_id}'")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute the query and fetch results
        df = pl.read_database(query, conn)

        # Close the connection
        conn.close()

        return df

    def get_competition_env_hash(self,comp_name:str):
        """returns the hash of the environment used dirung the given competition

        Args:
            comp_name (str): name of the competition track
        """
        pass
        