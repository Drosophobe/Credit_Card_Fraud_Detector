import numpy as np
import bentoml
from bentoml.io import NumpyNdarray

runner = bentoml.sklearn.get("ccf_classif:latest").to_runner()
svc=bentoml.Service("ccf_tree", runners=[runner])
@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
def classify(input_series) -> np.ndarray:
    # Convert the input string to numpy array
    label = runner.predict.run(input_series)

    return label
