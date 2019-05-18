g++ prepare_dataset.cpp -g -o prepare_dataset --std=c++14 -lboost_locale -O2
./prepare_dataset
python try_different_models.py
python test_solver.py regression-2.clf

