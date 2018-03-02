
def l1(x1, y1, x2, y2):
    return abs(x1-x2) + abs(y1-y2)


class Car:

    def __init__(self):
        self.x, self.y = 0, 0
        self.t_available = 0

    def __str__(self):
        return "Car[{x},{y},t_avail={t_available}]".format(**self.__dict__)

    def servable(self, ride):
        return self.t_available + l1(self.x, self.y, ride.x1, ride.y1) + len(ride) <= ride.t2

    def bonus(self, ride):
        return self.t_available + l1(self.x, self.y, ride.x1, ride.y1) <= ride.t1

    def serve(self, ride):
        self.t_available = len(ride) + max(ride.t1, self.t_available + l1(self.x, self.y, ride.x1, ride.y1))
        self.x, self.y = ride.x2, ride.y2


class Ride:

    def __init__(self, x1, y1, x2, y2, t1, t2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.t1 = t1
        self.t2 = t2

    def __str__(self):
        return "Ride[src=[{x1},{y1}],dest=[{x2},{y2}],t1={t1},t2={t2}]".format(**self.__dict__)

    def __len__(self):
        return l1(self.x1, self.y1, self.x2, self.y2)


def read_input(in_file):
    rides = []

    with open(in_file, 'r') as f:
        R, C, F, N, B, T = [int(x) for x in f.readline().strip().split()]
        for n in range(N):
            x1, y1, x2, y2, t1, t2 = [int(x) for x in f.readline().strip().split()]
            rides.append(Ride(x1, y1, x2, y2, t1, t2))

    return R, C, F, B, T, rides
