import json


def output_spec(fname: str, spec: list):
    with open(fname, "w") as f:
        json.dump(spec, f, sort_keys=True, indent=2, separators=(',', ': '))


def configs(instance: int):
    common_deps = [
        { "funcName": "scale", "funcId": 20, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "chkptmngr", "funcId": 30, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 40, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "dump", "funcId": 50, "minWorkers": 1, "maxWorkers": 1 },
    ]
    names = [
    ['source', 'query1'],
    ['source', 'query2'],
    ['source', 'q3GroupBy', 'q3JoinTable'],
    ['source', 'q46GroupBy', 'q4JoinStream', 'q4MaxBid', 'q4Avg'],
    ['source', 'q5bidkeyedbyauction', 'q5aucbids', 'q5maxbid'],
    ['source', 'q46GroupBy', 'q6JoinStream', 'q6MaxBid', 'q6Avg'],
    ['source', 'q7BidByPrice', 'q7BidByWin', 'q7MaxBid', 'q7JoinMaxBid'],
    ['source', 'q8GroupBy', 'q8JoinStream']]

    specs = []
    gateways = []
    gateway = [{ "funcName": "remoteTxnMngr", "funcId": 110, "minWorkers": 1, "maxWorkers": 1 }]
    for q in names:
        spec = []
        funcId = 60
        for n in q:
            spec.append({"funcName": n, "funcId": funcId, "minWorkers": instance, "maxWorkers": instance})
            funcId += 10
        specs.append(common_deps + spec)
        gateways.append(common_deps + spec + gateway)
        # q1 = [
        #     { "funcName": "source", "funcId": 60, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "query1", "funcId": 70, "minWorkers": instance, "maxWorkers": instance },
        # ]
        # q2 = [
        #     { "funcName": "source", "funcId": 60, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "query2", "funcId": 70, "minWorkers": instance, "maxWorkers": instance }
        # ]
        # q3 = [
        #     { "funcName": "source", "funcId": 60, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q3GroupBy", "funcId": 70, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q3JoinTable", "funcId": 80, "minWorkers": instance, "maxWorkers": instance }
        # ]
        # q4 = [ 
        #     { "funcName": "source", "funcId": 60, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q46GroupBy", "funcId": 70, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q4JoinStream", "funcId": 80, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q4MaxBid", "funcId": 90, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q4Avg", "funcId": 100, "minWorkers": instance, "maxWorkers": instance }
        # ]
        # q5 = [
        #     { "funcName": "source", "funcId": 20, "minWorkers": 4, "maxWorkers": 4 },
        #     { "funcName": "q5bidkeyedbyauction", "funcId": 30, "minWorkers": 4, "maxWorkers": 4 },
        #     { "funcName": "q5aucbids", "funcId": 40, "minWorkers": 4, "maxWorkers": 4 },
        #     { "funcName": "q5maxbid", "funcId": 50, "minWorkers": 4, "maxWorkers": 4 }
        # ]
        # q6 = [
        #     { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q46GroupBy", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q6JoinStream", "funcId": 40, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q6MaxBid", "funcId": 50, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q6Avg", "funcId": 60, "minWorkers": instance, "maxWorkers": instance }
        # ]
        # q7 = [
        #     { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q7BidByPrice", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q7BidByWin", "funcId": 40, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q7MaxBid", "funcId": 50, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q7JoinMaxBid", "funcId": 60, "minWorkers": instance, "maxWorkers": instance },
        # ]
        # q8 = [
        #     { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q8GroupBy", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        #     { "funcName": "q8JoinStream", "funcId": 50, "minWorkers": instance, "maxWorkers": instance },
        # ]
        # specs = [q1, q2, q3, q4, q5, q6, q7, q8]
        # for q in specs:
        #     names = [l['funcName'] for l in q]
        #     print(names)
        # gateways = [q + gateway for q in specs]
    return specs, gateways


def output_specs(instances: int):
    specs, gateways = configs(instances)
    for i in range(8):
        sp = specs[i]
        gateway = gateways[i]
        output_spec(f"./{instances}_ins/q{i+1}.json", sp)
        output_spec(f"./{instances}_ins/q{i+1}_gateway.json", gateway)


def main():
    specs, gateways = configs(4)
    for i in range(8):
        sp = specs[i]
        gateway = gateways[i]
        output_spec(f"q{i+1}.json", sp)
        output_spec(f"q{i+1}_gateway.json", gateway)
        output_spec(f"./4_ins/q{i+1}.json", sp)
        output_spec(f"./4_ins/q{i+1}_gateway.json", gateway)
    output_specs(8)
    output_specs(1)
    output_specs(2)


if __name__ == '__main__':
    main()
