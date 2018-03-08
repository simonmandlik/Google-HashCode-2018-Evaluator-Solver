import multiprocessing
import os
from copy import deepcopy
from math import inf, log
from os.path import join
from random import choice

import numpy as np

from evaluate import evaluate
from util import read_input, Car, write_output, l1_car_ride

HYPERPARAMS = {}
HYPERPARAMS["a"] = {'theta': -10, 'A': 0, 'B': 1, 'C': 1, 'k': 50}
HYPERPARAMS["b"] = {'theta': 0, 'A': 0, 'B': 1, 'C': 1, 'k': 100}
HYPERPARAMS["c"] = {'theta': -3.7990081123373294, 'A': 2.737837660419136, 'k': 14, 'C': 0, 'B': -3.367669716110166}
HYPERPARAMS["d"] = {"theta": 130, "A": 1, "B": 20000, 'C': 0, "k": 10}
HYPERPARAMS["e"] = {"theta": -2750, "A": 1, "B": 0, 'C': 0, "k": 0}


def solve(in_file, out_file, hyperparams):
    R, C, B, T, rides, cars = read_input(in_file)
    rides.sort()
    compute_event_density(rides, hyperparams)

    for ride in rides:
        best_car_score, best_car = -inf, None
        car_density = 0
        for car in cars:
            car_score = f(car, ride, hyperparams, B, R, C)
            if car_score > best_car_score:
                best_car_score, best_car = car_score, car

            car_density += int(car.servable(ride))
            car_density += int(car.bonus(ride))
        car_density /= 2.0 * len(cars)
        if len(ride) + \
                best_car_score + \
                ((T - ride.t2)/T) * hyperparams["B"] * ride.density + \
                hyperparams["C"] * car_density > hyperparams["theta"]:
            best_car.rides.append(ride.i)
            best_car.serve(ride)

    write_output(out_file, cars)


def f(car, ride, hyperparams, B, R, C):
    if not car.servable(ride):
        return -inf
    bonus = B if car.bonus(ride) else 0
    distance = l1_car_ride(car, ride) / (R+C)
    return bonus - hyperparams["A"] * distance


def compute_event_density(rides, hyperparams):
    dummy1, dummy2 = Car(), Car()
    for i in reversed(range(len(rides))):
        rides[i].density = 0.0
        dummy1.x = dummy2.x = rides[i].x2
        dummy1.y = dummy2.y = rides[i].y2
        dummy1.t = rides[i].t1 + len(rides[i])
        dummy2.t = rides[i].t2
        for j in range(i + 1, min(i + hyperparams["k"], len(rides))):
            rides[i].density += int(dummy1.servable(rides[j]))
            rides[i].density += int(dummy2.servable(rides[j]))
            rides[i].density += int(dummy1.bonus(rides[j]))
            rides[i].density += int(dummy2.bonus(rides[j]))

        rides[i].density /= 4.0 * len(rides)


def hyperparam_grid_search(in_file, out_file, letter):
    global HYPERPARAMS
    best_score, BEST = -inf, None
    for theta in [-inf, -1, 0, 1]:
        HYPERPARAMS[letter]["theta"] = theta
        for A in [0, 1, 10, 100]:
            HYPERPARAMS[letter]["A"] = A
            for B in [0, 1, 10, 100, 1000, 10000]:
                HYPERPARAMS[letter]["B"] = B
                for k in [0, 100, 200, 300, 400, 500]:
                    HYPERPARAMS[letter]["k"] = k
                    solve(in_file, out_file, HYPERPARAMS[letter])
                    score = evaluate(in_file, out_file)
                    if score > best_score:
                        best_score, BEST = score, deepcopy(HYPERPARAMS[letter])
                        print(best_score)
    print("Best hyperparams for {letter} are {H} scoring {score}".format(letter=letter, H=BEST, score=best_score))
    return BEST


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def __eq__(self, other):
        for k in self.keys():
            if abs(self.get(k) - other.get(k)) >= log(self.get(k)):
                return False
        return True


def evaluate_seed(params):
    seed, in_file, i = params
    out_file = "{i}.out".format(i=i)
    solve(in_file, out_file, seed)
    score = evaluate(in_file, out_file)
    os.remove(out_file)
    return score


def hyperparams_random_search(in_file, epochs=20):
    """Inspired here: https://blog.openai.com/evolution-strategies/"""
    theta_vals = [-10000, -100, -10, -5, -1, 0, 1, 5, 10, 100]

    def random_init():
        return hashabledict({"theta": choice(theta_vals),
              "A": int(np.random.uniform(-3, 10)),
              "B": int(np.random.uniform(-3, 10)),
              "C": int(np.random.uniform(-3, 10)),
              "k": int(np.random.uniform(100, 500))})

    N_seeds = 10
    N_children = 3

    seeds = [random_init() for _ in range(N_seeds)]

    best_score, best_params = -inf, None
    grow = 1
    pool = multiprocessing.Pool()
    for epoch in range(epochs):
        for i in range(N_seeds):
            for _ in range(N_children):
                seeds.append(deepcopy(seeds[i]))
                seeds[-1]["theta"] += np.random.normal(0, 2 ** grow)
                seeds[-1]["A"] += np.random.normal(0, 2 ** grow)
                seeds[-1]["B"] += np.random.normal(0, 2 ** grow)
                seeds[-1]["C"] += np.random.normal(0, 2 ** grow)
                seeds[-1]["k"] += int(np.random.normal(0, 2 ** grow))
            seeds.append(random_init())

        seeds = list(set(seeds))

        scores = pool.map(evaluate_seed, [(seed, in_file, i) for (i, seed) in enumerate(seeds)])
        keydict = dict(zip(seeds, scores))
        seeds.sort(key=keydict.get, reverse=True)
        seeds = seeds[:N_seeds]
        scores = sorted(scores, reverse=True)
        if scores[0] > best_score:
            best_score, best_params = scores[0], deepcopy(seeds[0])
            grow = 1
        else:
            grow += 1
        print("Epoch {e}: best hyperparams are {H} with score {s}".format(e=epoch, H=seeds[0], s=best_score))
    pool.close()


if __name__ == "__main__":
    letters = ["a", "b", "c", "d", "e"]
    # letters = ["e"]
    in_files = map(lambda x: join("../data", x + ".in"), letters)
    out_files = map(lambda x: join("../data", x + ".out"), letters)

    for in_file, out_file, letter in zip(in_files, out_files, letters):
        solve(in_file, out_file, HYPERPARAMS[letter])
        print("{letter}: {score}".format(letter=letter, score=evaluate(in_file, out_file)))
        # hyperparam_grid_search(in_file, out_file, letter)
        # hyperparams_random_search(in_file)
