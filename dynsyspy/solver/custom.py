from dynsyspy.types.problem import ProblemType

def discrete(results, eqs, y0):
    results.iloc[0,1:] = y0

    for idx, _ in results.iloc[1:,:].iterrows():
        results.iloc[idx,1:] = results.iloc[idx-1,1:] + [eq(idx, results.iloc[idx-1,1:]) for eq in eqs]
    return results

def solve(results, eqs, y0, problem_type):
    match (problem_type):
        case (ProblemType.discrete):
            res = discrete(results, eqs, y0)
            return res
        case _:
            print('This solver cannot solve this kind of problem')
        