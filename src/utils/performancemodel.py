import polars as pl
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


class PerformanceModel:
    """A performance model learning from 4 input files (currently, corresponding to the 4 tables in our future database)

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    
    def __init__(self, environments_path, instances_path, solvers_path, performances_path):
        """Initialises the model with the given files, loads and preprocesses the data

        Args:
            environments_path (str): path of the file containing the environment table
            instances_path (str): path of the file containing the instance table
            solvers_path (str): path of the file containing the solver table
            performances_path (str): path of the file containing the performance table

        Raises:
            FileNotFoundError: if csv files are not there
        """
        self.environments_path = environments_path
        self.instances_path = instances_path
        self.solvers_path = solvers_path
        self.performances_path = performances_path
        self.load_data()
        self.prepare_data()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def load_data(self):
        """Reads the csv files and loads the data into memory

        Raises:
            FileNotFoundError: if csv files are not there
        """
        # Load features
        self.environments = pl.read_csv(self.environments_path)
        self.instances = pl.read_csv(self.instances_path)
        self.solvers = pl.read_csv(self.solvers_path)
        # Load performances
        self.performances = pl.read_csv(self.performances_path)
        

    def prepare_data(self):
        """_summary_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        # Merge perf with environments on env_hash
        merged = self.perf.join(self.environments, left_on="env_hash", right_on="env_hash", how="left")

        # Merge with instances on inst_hash
        merged = merged.join(self.instances, left_on="inst_hash", right_on="inst_hash", how="left")

        # Merge with solvers on solver_hash
        merged = merged.join(self.solvers, left_on="solver_hash", right_on="solver_hash", how="left")

        # Drop hash columns and status, keep only features and perf
        self.X = merged.drop(["env_hash", "inst_hash", "solver_hash", "status","perf"])
        self.Y = self.perf["perf"].to_numpy()

    def train(self):
        """_summary_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Model trained. Test MSE: {mse:.4f}")

    def predict(self, env_hash, inst_hash):
        """_summary_

        Args:
            env_hash (bool): _description_
            inst_hash (bool): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        idx1 = self.hash_to_index.get(env_hash)
        idx2 = self.hash_to_index.get(inst_hash)
        if idx1 is not None and idx2 is not None:
            combined = self.features[idx1].to_list() + self.features[idx2].to_list()
            return self.model.predict([combined])[0]
        else:
            raise ValueError("One or both hashes not found in features.")


if __name__ == "__main__":

    # Initialize
    rf = PerformanceModel("environments.csv", "instances.csv", "solvers.csv", "performances.csv")

    # Train
    rf.train()

    # Predict
    prediction = rf.predict("hash_a", "hash_b")
    print(f"Predicted value: {prediction}")
