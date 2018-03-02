from src.util import Car, read_input


def evaluate(in_file, out_file):
    _, _, F, B, _, rides = read_input(in_file)
    rides = rides
    used_rides = [False] * len(rides)

    score = 0

    def error():
        print("Invalid output file")
        exit(0)

    with open(out_file, 'r') as f:
        for _ in range(F):
            c = Car()
            line = [int(x) for x in f.readline().strip().split()]
            if line[0] != len(line)-1:
                error()
            for r in line[1:]:
                if not used_rides[r]:
                    used_rides[r] = True
                    score += len(rides[r]) if c.servable(rides[r]) else 0
                    score += B if c.bonus(rides[r]) else 0
                    c.serve(rides[r])
                else:
                    error()
    return score


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Please provide input file and output file of the dataset instance")
        exit(0)

    in_file, out_file = sys.argv[1:3]
    print("Score is {}".format(evaluate(in_file, out_file)))
