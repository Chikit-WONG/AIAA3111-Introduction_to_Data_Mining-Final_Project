"""One isolated process per timing repetition; imports/encoding are not timed."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
import psutil
from .mining import mine, signature


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--columns", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--algorithm", choices=["apriori", "fpgrowth"], required=True)
    parser.add_argument("--support", type=float, required=True)
    parser.add_argument("--max-length", type=int, required=True)
    parser.add_argument("--low-memory", action="store_true")
    args = parser.parse_args()
    matrix = pd.DataFrame(np.load(args.matrix), columns=json.loads(Path(args.columns).read_text()))
    process = psutil.Process()
    baseline = process.memory_info().rss
    start = time.perf_counter()
    itemsets = mine(matrix, args.algorithm, args.support, args.max_length, args.low_memory)
    seconds = time.perf_counter() - start
    memory = process.memory_info()
    itemsets.to_pickle(args.output)
    print(json.dumps({"seconds": seconds, "itemsets": len(itemsets), "signature": signature(itemsets, len(matrix)), "baseline_rss_mib": baseline / 2**20, "os_peak_rss_mib": getattr(memory, "peak_wset", memory.rss) / 2**20}), flush=True)


if __name__ == "__main__":
    main()
