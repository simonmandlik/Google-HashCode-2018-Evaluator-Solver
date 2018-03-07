from os.path import join

from copy import deepcopy

from evaluate import evaluate
from util import read_input, Car, write_output, l1, l1_car_ride
from math import inf

HYPERPARAMS = {}
HYPERPARAMS["a"] = HYPERPARAMS["b"] = HYPERPARAMS["c"] = HYPERPARAMS["d"] = HYPERPARAMS["e"] = {
    "theta": -inf, "A": 1, "B": 10, "k1": 10, "k2": 300
}


def solve(in_file, out_file, letter):
    R, C, B, T, rides, cars = read_input(in_file)
    hyperparams = HYPERPARAMS[letter]
    rides.sort()
    compute_event_density(rides, T, hyperparams)

    for ride in rides:
        # print(ride.density)
        best_car_score, best_car = -inf, None
        for car in cars:
            car_score = f(car, ride, cars, rides, hyperparams, B, R, C)
            if car_score > best_car_score:
                best_car_score, best_car = car_score, car

        if best_car_score > hyperparams["theta"]:
            best_car.rides.append(ride.i)
            best_car.serve(ride)

    write_output(out_file, cars)


def f(car, ride, rides, cars, hyperparams, B, R, C):
    if not car.servable(ride):
        return -inf
    ride_len = len(ride)
    bonus = B if car.bonus(ride) else 0
    distance = -hyperparams["A"] * l1_car_ride(car, ride) / (R + C)
    density = hyperparams["B"] * ride.density
    # print("ride_len={0}\t\tbonus={1}\t\tdistance={2}\t\t{3}".format(ride_len, bonus, distance, density))
    return ride_len + bonus + distance + density


def compute_event_density(rides, T, hyperparams):
    dummy1, dummy2 = Car(), Car()
    for i in reversed(range(len(rides))):
        rides[i].density = 0.0
        dummy1.x = dummy2.x = rides[i].x2
        dummy1.y = dummy2.y = rides[i].y2
        dummy1.t = rides[i].t1 + len(rides[i])
        dummy2.t = rides[i].t2
        for j in range(i + 1, min(i + hyperparams["k1"], len(rides))):
            rides[i].density += int(dummy1.servable(rides[j]))
            rides[i].density += int(dummy2.servable(rides[j]))
            # rides[i].density += int(dummy1.bonus(rides[j]))

        rides[i].density /= 2.0 * len(rides)
        rides[i].density /= (T - rides[i].t2 + 1) / T


def hyperparam_grid_search(in_file, out_file, letter):
    best_score, BEST = -inf, None
    global HYPERPARAMS
    for theta in [-inf]:
        HYPERPARAMS[letter]["theta"] = theta
        for A in [0, 1, 10, 100]:
            HYPERPARAMS[letter]["A"] = A
            for B in [0, 1, 10, 100, 1000, 10000]:
                HYPERPARAMS[letter]["B"] = B
                # for k1 in [0]:
                for k1 in [0, 10, 50, 100, 250, 500]:
                    HYPERPARAMS[letter]["k1"] = k1
                    for k2 in [0, 100, 200, 300, 400, 500]:
                        HYPERPARAMS[letter]["k2"] = k2
                        solve(in_file, out_file, letter)
                        score = evaluate(in_file, out_file)
                        if score > best_score:
                            best_score, BEST = score, deepcopy(HYPERPARAMS[letter])
    print("Best hyperparams for {letter} are {H} scoring {score}".format(letter=letter, H=BEST, score=best_score))
    return BEST


if __name__ == "__main__":
    letters = ["a", "b", "c", "d", "e"]
    # letters = ["a", "b"]
    in_files = map(lambda x: join("../data", x + ".in"), letters)
    out_files = map(lambda x: join("../data", x + ".out"), letters)

    for in_file, out_file, letter in zip(in_files, out_files, letters):
        solve(in_file, out_file, letter)
        print("{letter}: {score}".format(letter=letter, score=evaluate(in_file, out_file)))
        # hyperparam_grid_search(in_file, out_file, letter)
