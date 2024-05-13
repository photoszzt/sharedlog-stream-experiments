import json


def output_spec(fname: str, spec: list):
    with open(fname, "w") as f:
        json.dump(spec, f, sort_keys=True, indent=2, separators=(',', ': '))


def configs(instance: int):
    q1 = [
        { "funcName": "scale", "funcId": 40, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "chkptmngr", "funcId": 60, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 70, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "query1", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "dump", "funcId": 50, "minWorkers": 1, "maxWorkers": 1 }
    ]
    q2 = [
        { "funcName": "scale", "funcId": 40, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "chkptmngr", "funcId": 50, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 70, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "dump", "funcId": 60, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "query2", "funcId": 30, "minWorkers": instance, "maxWorkers": instance }
    ]
    q3 = [
        { "funcName": "scale", "funcId": 60, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "chkptmngr", "funcId": 70, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 80, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q3GroupBy", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q3JoinTable", "funcId": 40, "minWorkers": instance, "maxWorkers": instance }
    ]
    q4 = [ 
        { "funcName": "scale", "funcId": 70, "minWorkers": 1,"maxWorkers": 1 },
        { "funcName": "chkptmngr", "funcId": 80, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 100, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "qinstance6GroupBy", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "qinstanceJoinStream", "funcId": 40, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "qinstanceMaxBid", "funcId": 50, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "qinstanceAvg", "funcId": 60, "minWorkers": instance, "maxWorkers": instance }
    ]
    q5 = [
        { "funcName": "scale", "funcId": 60, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "chkptmngr", "funcId": 70, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 90, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "source", "funcId": 20, "minWorkers": 4, "maxWorkers": 4 },
        { "funcName": "q5bidkeyedbyauction", "funcId": 30, "minWorkers": 4, "maxWorkers": 4 },
        { "funcName": "q5aucbids", "funcId": 40, "minWorkers": 4, "maxWorkers": 4 },
        { "funcName": "q5maxbid", "funcId": 50, "minWorkers": 4, "maxWorkers": 4 }
    ]
    q6 = [
        { "funcName": "scale", "funcId": 70, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "chkptmngr", "funcId": 80, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 100, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q46GroupBy", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q6JoinStream", "funcId": 40, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q6MaxBid", "funcId": 50, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q6Avg", "funcId": 60, "minWorkers": instance, "maxWorkers": instance }
    ]
    q7 = [
        { "funcName": "scale", "funcId": 70, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q7BidByPrice", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q7BidByWin", "funcId": 40, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q7MaxBid", "funcId": 50, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q7JoinMaxBid", "funcId": 60, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "chkptmngr", "funcId": 90, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 100, "minWorkers": 1, "maxWorkers": 1 }
    ]
    q8 = [
        { "funcName": "scale", "funcId": 60, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "source", "funcId": 20, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q8GroupBy", "funcId": 30, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "q8JoinStream", "funcId": 50, "minWorkers": instance, "maxWorkers": instance },
        { "funcName": "chkptmngr", "funcId": 70, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "redisSetup", "funcId": 90, "minWorkers": 1, "maxWorkers": 1 },
        { "funcName": "dump", "funcId": 40, "minWorkers": 1, "maxWorkers": 1 }
    ]
    gateway = [{ "funcName": "remoteTxnMngr", "funcId": 110, "minWorkers": 1, "maxWorkers": 1 }]
    specs = [q1, q2, q3, q4, q5, q6, q7, q8]
    gateways = [q + gateway for q in specs]
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
