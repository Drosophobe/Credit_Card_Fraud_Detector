import pickle

loaded_model = pickle.load(open('../models/dt_partial.sav', 'rb'))
print(loaded_model)
