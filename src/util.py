
def l1(x1, y1, x2, y2):
    return abs(x1-x2) + abs(y1-y2)


def l1_car_ride(car, ride):
    return l1(car.x, car.y, ride.x1, ride.y1)


class Car:

    def __init__(self):
        self.x, self.y = 0, 0
        self.t_available = 0
        self.rides = []

    def __str__(self):
        return "Car[{x},{y},t_avail={t_available},ass_rides={rides}]".format(**self.__dict__)

    def servable(self, ride):
        return self.t_available + l1(self.x, self.y, ride.x1, ride.y1) + len(ride) <= ride.t2

    def bonus(self, ride):
        return self.t_available + l1(self.x, self.y, ride.x1, ride.y1) <= ride.t1

    def serve(self, ride):
        self.t_available = len(ride) + max(ride.t1, self.t_available + l1(self.x, self.y, ride.x1, ride.y1))
        self.x, self.y = ride.x2, ride.y2


class Ride:

    def __init__(self, i, x1, y1, x2, y2, t1, t2):
        self.i = i
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.t1 = t1
        self.t2 = t2

        self.density = 0.0

    def __str__(self):
        return "Ride[i={i},src=[{x1},{y1}],dest=[{x2},{y2}],t1={t1},t2={t2}]".format(**self.__dict__)

    def __len__(self):
        return l1(self.x1, self.y1, self.x2, self.y2)

    def __lt__(self, other):
        return self.t1 < other.t1 or self.t1 == other.t1 and self.t2 < other.t2


def read_input(in_file):
    rides = []

    with open(in_file, 'r') as f:
        R, C, F, N, B, T = [int(x) for x in f.readline().strip().split()]
        for n in range(N):
            x1, y1, x2, y2, t1, t2 = [int(x) for x in f.readline().strip().split()]
            rides.append(Ride(n, x1, y1, x2, y2, t1, t2))

    cars = [Car() for _ in range(F)]
    return R, C, B, T, rides, cars


def write_output(out_file, cars):
    with open(out_file, "w") as f:
        for c in cars:
            print(len(c.rides), *c.rides, file=f, sep=" ")