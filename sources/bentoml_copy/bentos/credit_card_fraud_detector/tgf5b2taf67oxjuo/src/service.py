import numpy as np
import pandas as pd 
import bentoml 
from bentoml.io import NumpyNdarray
BENTO_MODEL_TAG = "ccf_partial:zrasw7taegklxjuo"
ccf_runner = bentoml.sklearn.get(BENTO_MODEL_TAG).to_runner()
ccf_service = bentoml.Service("Credit_Card_Fraud_Detector", runners = 
[ccf_runner])
@ccf_service.api(input=NumpyNdarray(), output=NumpyNdarray()) 
def detection(input_data: np.ndarray) -> np.ndarray:
    return ccf_runner.predict.run(input_data)
