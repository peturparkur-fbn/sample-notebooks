import pandas as pd

class Result0D:
    resultValueType: str = "Result0D"
    dimension: int = 0
    value: float
    units: list

    def __init__(self, json: dict):
        if(json["resultValueType"] != self.resultValueType): raise Exception(f"Cannot parse json to {self.resultValueType}")
        self.value = json["values"]["(0,0)"]
        self.units = json["units"]["units"]

    @property
    def result(self):
        return (self.value, self.units)
    
    def __str__(self) -> str:
        return str(self.result)

class Result1D:
    resultValueType: str = "Result1D"
    dimension: int = 1
    units: list
    labels: dict[int, str]
    values: dict[str, float]

    def __init__(self, json: dict, prune: bool = False):
        if(json["resultValueType"] != self.resultValueType): raise Exception(f"Cannot parse json to {self.resultValueType}")
        self.labels = { v: k for k, v in json["labelsY"].items() }
        def get_key(k: str):
            x = k.removeprefix("(").removesuffix(")").split(",")
            return int(x[0])
        tmp = {get_key(k): v for k, v in json["values"].items() if not (prune and v == 0)}
        self.values = {self.labels[k]: v for k, v in tmp.items() if k in self.labels}
        self.units = json["units"]["units"]
    
    
    
    @property
    def result(self):
        return (self.values, self.units)
    
    def __str__(self) -> str:
        return str(self.result)

class Result2D:
    resultValueType: str = "Result2D"
    dimension: int = 2
    units: list
    labelsX: dict[int, str]
    labelsY: dict[int, str]
    values: dict[tuple[str, str], float]

    def __init__(self, json: dict, prune: bool = False):
        if(json["resultValueType"] != self.resultValueType): raise Exception(f"Cannot parse json to {self.resultValueType}")
        self.labelsX = { v: k for k, v in json["labelsX"].items() }
        self.labelsY = { v: k for k, v in json["labelsY"].items() }
        def get_key(k: str):
            x = k.removeprefix("(").removesuffix(")").split(",")
            return int(x[0]),int(x[1])
        tmp = {get_key(k): v for k, v in json["values"].items() if not (prune and v == 0)}
        self.values = {(self.labelsY[k[0]], self.labelsX[k[1]]): v for k, v in tmp.items() if k[0] in self.labelsY and k[1] in self.labelsX}

        self.units = json["units"]["units"]
    
    
    
    @property
    def result(self):
        return (self.values, self.units)
    
    def __str__(self) -> str:
        return str(self.result)


def parse_df_resultvalues(df: pd.DataFrame):
    def try_convert_value(entry: dict):
        if("resultValueType" not in entry): return entry
        if(entry["resultValueType"] == "Result0D"): return Result0D(entry)
        if(entry["resultValueType"] == "Result1D"): return Result1D(entry, prune = True)
        if(entry["resultValueType"] == "Result2D"): return Result2D(entry, prune = True)
        return entry
    def convert_row_entry(row_entry):
        if(not isinstance(row_entry, dict)): return row_entry
        return {
            k: try_convert_value(row_entry[k]) for k in row_entry
        }
    return df.applymap(convert_row_entry)